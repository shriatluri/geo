import { Queue } from 'bullmq';

// Create a new queue for analysis jobs
const analysisQueue = new Queue('analysisQueue');

export default analysisQueue;
