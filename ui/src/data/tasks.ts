import { Task } from '../types';

// 10 dummy tasks in 3 similar groups
export const dummyTasks: Task[] = [
  // Data Analysis Tasks (Group 1)
  {
    id: 1,
    title: "Data Analysis - Customer Behavior",
    description: "Analyze customer purchase patterns and create a summary report",
    category: "Data Analysis",
    time: "8 hours",
    payout: "$2"
  },
  {
    id: 2,
    title: "Data Analysis - Website Traffic",
    description: "Analyze website traffic patterns and identify peak usage times",
    category: "Data Analysis",
    time: "8 hours",
    payout: "$2"
  },
  {
    id: 3,
    title: "Data Analysis - Social Media Engagement",
    description: "Analyze engagement metrics across social media platforms",
    category: "Data Analysis",
    time: "8 hours",
    payout: "$2"
  },
  
  // Content Moderation Tasks (Group 2)
  {
    id: 4,
    title: "Content Moderation - Forum Posts",
    description: "Review and moderate forum posts according to community guidelines",
    category: "Content Moderation",
    time: "8 hours",
    payout: "$2"
  },
  {
    id: 5,
    title: "Content Moderation - Image Review",
    description: "Review uploaded images for policy violations",
    category: "Content Moderation",
    time: "8 hours",
    payout: "$2"
  },
  {
    id: 6,
    title: "Content Moderation - Comments Review",
    description: "Review user comments for inappropriate content",
    category: "Content Moderation",
    time: "8 hours",
    payout: "$2"
  },
  {
    id: 7,
    title: "Content Moderation - Product Listings",
    description: "Review product listings for policy compliance",
    category: "Content Moderation",
    time: "8 hours",
    payout: "$2"
  },
  
  // Text Classification Tasks (Group 3)
  {
    id: 8,
    title: "Text Classification - Customer Feedback",
    description: "Classify customer feedback into predefined categories",
    category: "Text Classification",
    time: "8 hours",
    payout: "$2"
  },
  {
    id: 9,
    title: "Text Classification - Support Tickets",
    description: "Categorize support tickets by issue type",
    category: "Text Classification",
    time: "8 hours",
    payout: "$2"
  },
  {
    id: 10,
    title: "Text Classification - Email Content",
    description: "Classify email content by intent and priority",
    category: "Text Classification",
    time: "8 hours",
    payout: "$2"
  }
];