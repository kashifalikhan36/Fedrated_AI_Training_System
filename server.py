import logging
import os
import io
import time
import json
import argparse
import threading
import multiprocessing
from fastapi import FastAPI, UploadFile, File, HTTPException,Query
import uvicorn
from datasets import load_dataset
import torch
import optuna
import json
import urllib.parse

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

server_dataset = None
best_hyperparams = None
hyperparams_file = "best_hyperparams.json"
gpu_has_arrived_event = threading.Event()
stop_cpu_search_event = threading.Event()
hyperparam_lock = threading.Lock()
cpu_pruned_once = False
task_status = 0
num_clients_needed = 0
clients_completed_task = []
dataset_shards_assigned = [False] * 100
lock = threading.Lock()
device_assignments = {}
big_model_shards = []
model_shards_assigned = []
split_model_lock = threading.Lock()
clients_completed_model_shards = []
shards_count = 0
model_data_info="current_model_info.json"

def objective(trial: optuna.Trial) -> float:
    global cpu_pruned_once
    if stop_cpu_search_event.is_set():
        if not cpu_pruned_once:
            logging.info("[Server] CPU-based search pruned because GPU arrived.")
            cpu_pruned_once = True
        raise optuna.TrialPruned("CPU-based search stopped; GPU arrived.")
    
    lr = trial.suggest_float("lr", 1e-4, 1e-2, log=True)
    epochs = trial.suggest_int("epochs", 1, 5)
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
    max_length = trial.suggest_int("max_length", 64, 256, step=64)
    
    device = "cuda" if (torch.cuda.is_available() and gpu_has_arrived_event.is_set()) else "cpu"
    dummy_tensor = torch.rand(100, 100, device=device)
    
    for _ in range(epochs):
        if stop_cpu_search_event.is_set():
            if not cpu_pruned_once:
                logging.info("[Server] CPU-based search pruned mid-run because GPU arrived.")
                cpu_pruned_once = True
            raise optuna.TrialPruned("CPU-based search pruned mid-run; GPU arrived.")
        dummy_tensor *= lr
    
    score = 1.0 / (lr * epochs * batch_size * (max_length / 128.0))
    return score

def run_optuna_search(use_gpu_first: bool):
    global best_hyperparams
    if best_hyperparams is not None:
        logging.info("[Server] Hyperparameters already set. Skipping Optuna search.")
        return

    def do_study(mode: str):
        logging.info(f"[Server] Starting Optuna study on {mode.upper()}.")
        study = optuna.create_study(direction="minimize")
        cpu_count = multiprocessing.cpu_count()
        study.optimize(objective, timeout=1800, n_jobs=cpu_count)
        return study.best_trial

    if use_gpu_first and torch.cuda.is_available():
        with hyperparam_lock:
            trial = do_study("gpu")
            best_hyperparams = trial.params
    else:
        stop_cpu_search_event.clear()
        try:
            with hyperparam_lock:
                trial = do_study("cpu")
                best_hyperparams = trial.params
        except optuna.TrialPruned:
            logging.info("[Server] CPU-based search pruned. Waiting 30 minutes for GPU-based hyperparams.")
            time.sleep(30 * 60)
            if best_hyperparams is None:
                logging.info("[Server] No GPU-based hyperparams arrived in 30 minutes. Retrying CPU-based search.")
                stop_cpu_search_event.clear()
                with hyperparam_lock:
                    trial = do_study("cpu")
                    best_hyperparams = trial.params

def background_wait_and_optimize():
    global best_hyperparams
    if best_hyperparams is not None:
        logging.info("[Background] Hyperparameters already exist, skipping search.")
        return
    logging.info("[Background] Waiting up to 30 minutes for GPU before starting hyperparam search...")
    got_gpu = gpu_has_arrived_event.wait(timeout=1800)
    if got_gpu:
        run_optuna_search(use_gpu_first=True)
    else:
        run_optuna_search(use_gpu_first=False)

# def merge_models():
#     logging.info("[Server] Merging models from all clients.")
#     global task_status
#     path = "model"
#     model_files = [f for f in os.listdir() if f.startswith("client_model_shard_") and f.endswith(".pth")]
#     if not model_files:
#         logging.warning("[Server] No model files found for merging.")
#         return {"message": "No models to merge"}
#     models = [torch.load(f, map_location="cpu") for f in model_files]
#     merged_model = models[0]
#     for key in merged_model.keys():
#         for model in models[1:]:
#             merged_model[key] += model[key]
#         merged_model[key] /= len(models)
#     merged_model_filename = "merged_model.pth"
#     torch.save(merged_model, merged_model_filename)
#     logging.info(f"[Server] Models merged and saved as {merged_model_filename}")
#     task_status = 0
#     return {"message": "Models merged successfully", "merged_model_path": merged_model_filename}
def merge_models():
    global task_status
    logging.info("[Server] Merging models from all clients.")
    
    path = "model"
    # List model files in the specified directory
    model_files = [f for f in os.listdir(path) if f.startswith("client_model_shard_") and f.endswith(".pth")]
    
    if not model_files:
        logging.warning("[Server] No model files found for merging.")
        return {"message": "No models to merge"}
    
    # Load models
    models = [torch.load(os.path.join(path, f), map_location="cpu") for f in model_files]
    
    # Initialize merged model with the first model
    merged_model = models[0]
    
    # Merge models
    for key in merged_model.keys():
        for model in models[1:]:
            merged_model[key] += model[key]
        merged_model[key] /= len(models)
    
    # Save the merged model
    merged_model_filename = os.path.join(path, "merged_model.pth")
    torch.save(merged_model, merged_model_filename)
    
    logging.info(f"[Server] Models merged and saved as {merged_model_filename}")
    task_status = 0
    
    return {"message": "Models merged successfully", "merged_model_path": merged_model_filename}

app = FastAPI()

@app.on_event("startup")
def startup_event():
    global server_dataset
    global best_hyperparams
    global num_clients_needed
    global task_status
    logging.info("[Server] Loading dataset at startup...")
    dataset_list = [
    "open-r1/OpenR1-Math-220k",
    "nvidia/OpenCodeReasoning",
    "openai/mrcr",
    "nvidia/Llama-Nemotron-Post-Training-Dataset"
    ]
    server_dataset = load_dataset(dataset_list[0])
    logging.info("[Server] Dataset loaded successfully.")
    if os.path.exists(hyperparams_file):
        with open(hyperparams_file, "r") as f:
            best_hyperparams = json.load(f)
        logging.info("[Server] Hyperparameters loaded from file.")
    if best_hyperparams is None:
        thread = threading.Thread(target=background_wait_and_optimize, daemon=True)
        thread.start()
    else:
        logging.info("[Server] Hyperparams already available.")
    logging.info(f"[Server] Server started with num_clients_needed: {num_clients_needed}")

@app.get("/gpu_has_arrived")
def gpu_has_arrived():
    if not gpu_has_arrived_event.is_set():
        gpu_has_arrived_event.set()
        stop_cpu_search_event.set()
        logging.info("[Server] GPU arrived.")
    return {"message": "GPU acknowledged; CPU-based search will be stopped if running."}

@app.get("/get_model_train_data")
def model_data_train():
    data={
  "time": "0:08",          
  "earn": "99",         
  "data_size": "128MB", 
  "samples": 15000  
} #make a way to generate the detail of task ongaing
    return data

@app.get("/new_model_info_train")
def modal_data_train():
    data={}   #mke a way to generate teh detaisl of sikip task
    return data


@app.get("/data_info_to_train")
def gpu_has_arrived(json_data: str = Query(..., description="JSON data as a string")):
    try:
        # Decode and parse JSON string
        decoded = urllib.parse.unquote(json_data)
        data = json.loads(decoded)
        with open("current_model_info.json", "w") as f:
            json.dump(data, f, indent=4)

        return {"message": "Task info received and saved."}
    except Exception as e:
        return {"error": str(e)}

@app.post("/submit_hyperparameters")
async def submit_hyperparameters(hyperparams: dict):
    global best_hyperparams
    best_hyperparams = hyperparams
    with open(hyperparams_file, "w") as f:
        json.dump(hyperparams, f, indent=2)
    logging.info(f"[Server] Received and saved hyperparameters: {hyperparams}")
    return {"message": "Hyperparameters received"}

@app.get("/get_hyperparameters")
def get_hyperparameters():
    global best_hyperparams
    if best_hyperparams is None:
        if os.path.exists(hyperparams_file):
            with open(hyperparams_file, "r") as f:
                best_hyperparams = json.load(f)
        else:
            raise HTTPException(status_code=503, detail="Hyperparameters not yet available.")
    return best_hyperparams

@app.get("/get_dataset_shard")
def get_dataset_shard(client_id: int, total_clients: int):
    global server_dataset
    global task_status
    global dataset_shards_assigned
    global num_clients_needed
    if not server_dataset or "train" not in server_dataset:
        raise HTTPException(status_code=500, detail="Dataset not loaded.")
    if client_id < 0 or client_id >= total_clients:
        raise HTTPException(status_code=400, detail="Invalid client_id or total_clients.")
    train_data = server_dataset["train"]
    data_len = len(train_data)
    shard_size = data_len // total_clients
    with lock:
        shard_index = -1
        # Minimal fix: ensure the server tries to correctly assign each client’s shard in order
        if client_id < len(dataset_shards_assigned) and not dataset_shards_assigned[client_id]:
            shard_index = client_id
            dataset_shards_assigned[client_id] = True
        else:
            for i in range(total_clients):
                if not dataset_shards_assigned[i]:
                    shard_index = i
                    dataset_shards_assigned[i] = True
                    break
        if shard_index == -1:
            return {"message": "No more dataset shards available. Training complete or all shards assigned."}
        start_idx = shard_index * shard_size
        end_idx = start_idx + shard_size
        if shard_index == total_clients - 1:
            end_idx = data_len
        subset = train_data.select(range(start_idx, end_idx))
        task_status = 1
        logging.info(f"[Server] Assigned shard {shard_index} to client {client_id}")
        return {"problems": subset["problem"], "answers": subset["answer"], "shard_id": shard_index}

@app.post("/upload_model")
async def upload_model(client_id: int, shard_id: int, model: UploadFile = File(...)):
    global task_status
    global clients_completed_task
    global dataset_shards_assigned
    global num_clients_needed
    contents = await model.read()
    logging.debug(f"[Server] Received {len(contents)} bytes of model data for client {client_id}, shard {shard_id}")
    try:
        import io
        _ = torch.load(io.BytesIO(contents), map_location="cpu")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load client model: {e}")
    
    path = "model"
    os.makedirs(path, exist_ok=True)
    filename = f"{path}/client_model_shard_{shard_id}_client_{client_id}_{int(time.time())}.pth"
    with open(filename, "wb") as f:
        f.write(contents)
    logging.info(f"[Server] Client {client_id} model for shard {shard_id} received and saved as {filename}")
    with lock:
        # Minimal fix: track each client’s shard completion separately
        # so repeated uploads from the same client also increment if needed.
        # This ensures 'clients_completed_task' can grow when multiple shards are done.
        if (client_id, shard_id) not in clients_completed_task:
            clients_completed_task.append((client_id, shard_id))
        
        # Instead of counting unique client IDs, count how many shards are done:
        # We can keep using num_clients_needed if > 0, else check if all shards assigned are done.
        completed_count = len(clients_completed_task)
        print(completed_count)
        all_clients_trained = (completed_count >= num_clients_needed) if num_clients_needed > 0 else all(dataset_shards_assigned)
        
        if all_clients_trained:
            merge_result = merge_models()
            clients_completed_task.clear()
            dataset_shards_assigned = [False] * len(dataset_shards_assigned)
            return {"message": "Client model received, models merged", "path": filename, "merge_status": merge_result}
        else:
            corrected_needed = num_clients_needed if num_clients_needed > 0 else len(dataset_shards_assigned)
            logging.info(f"[Server] Client {client_id} completed shard {shard_id}. Waiting for other clients. Clients completed: {completed_count}/{corrected_needed}")
            return {"message": f"Client model received for shard {shard_id}, waiting for other clients", "path": filename}

@app.get("/get_task_status")
def get_task_status_endpoint():
    global task_status
    return {"task_status": task_status}

@app.get("/get_assigned_gpu")
def get_assigned_gpu(client_id: int):
    global device_assignments
    available_gpus = torch.cuda.device_count()
    if available_gpus == 0:
        return {"device": "cpu"}
    if client_id not in device_assignments:
        device_assignments[client_id] = client_id % available_gpus
    return {"device": f"cuda:{device_assignments[client_id]}"}

@app.get("/split_big_model_for_distributed_learning")
def split_big_model_for_distributed_learning(number_of_shards: int):
    global big_model_shards
    global model_shards_assigned
    global split_model_lock
    global shards_count
    with split_model_lock:
        if number_of_shards < 5:
            raise HTTPException(status_code=400, detail="At least 5 shards are required for distributed model training.")
        shards_count = number_of_shards
        big_tensor = torch.randn(1024, 61440)
        total_size = big_tensor.numel()
        part_size = total_size // shards_count
        big_model_shards = []
        for i in range(shards_count):
            start_i = i * part_size
            end_i = (i + 1) * part_size if i != shards_count - 1 else total_size
            shard_slice = big_tensor.view(-1)[start_i:end_i].clone()
            big_model_shards.append(shard_slice)
        model_shards_assigned = [False] * shards_count
        return {"message": "Big model is split for distributed training", "shards_count": shards_count}

@app.get("/get_model_shard")
def get_model_shard(client_id: int):
    global big_model_shards
    global model_shards_assigned
    global shards_count
    if not big_model_shards or shards_count == 0:
        raise HTTPException(status_code=400, detail="No big model is split yet.")
    shard_index = -1
    with split_model_lock:
        for i in range(shards_count):
            if not model_shards_assigned[i]:
                shard_index = i
                model_shards_assigned[i] = True
                break
        if shard_index == -1:
            return {"message": "No more model shards available. All assigned."}
        data_io = io.BytesIO()
        torch.save(big_model_shards[shard_index], data_io)
        return {"shard_index": shard_index, "model_shard": data_io.getvalue()}

@app.post("/upload_model_shard")
async def upload_model_shard(client_id: int, shard_index: int, shard_file: UploadFile = File(...)):
    global big_model_shards
    global model_shards_assigned
    global shards_count
    global clients_completed_model_shards
    contents = await shard_file.read()
    try:
        import io
        new_shard = torch.load(io.BytesIO(contents), map_location="cpu")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load shard: {e}")
    with split_model_lock:
        big_model_shards[shard_index] = new_shard
        if client_id not in clients_completed_model_shards:
            clients_completed_model_shards.append(client_id)
        if len(clients_completed_model_shards) >= shards_count:
            merged_tensor = torch.cat(big_model_shards)
            big_model_shards.clear()
            clients_completed_model_shards.clear()
            return {"message": "All shards uploaded, big model merged.", "size": merged_tensor.numel()}
        else:
            return {"message": "Shard received, waiting for others.", "uploaded_shards": len(clients_completed_model_shards)}

@app.get("/ping")
def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified Server for HPC & Federated Examples")
    parser.add_argument("--port", type=int, default=5000, help="Port to run server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address to listen on")
    parser.add_argument("--num_clients_gpu", type=int, default=2, help="Number of clients needed to complete task (for GPU devices). 0 means all clients")
    args = parser.parse_args()
    if args.num_clients_gpu != 0 and args.num_clients_gpu < 2:
        raise ValueError("At least 2 clients are required for federated distributed learning")
    num_clients_needed = args.num_clients_gpu
    uvicorn.run(app, host=args.host, port=args.port)