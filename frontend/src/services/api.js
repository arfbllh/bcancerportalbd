// src/services/api.js
import axios from 'axios';

const API_URL = 'http://127.0.0.1:4000/api';

// Create an axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Dataset services
export const datasetService = {
  // Get all datasets grouped by type
  getAllDatasets: async () => {
    try {
      const response = await apiClient.get('/datasets');
      return response.data;
    } catch (error) {
      console.error('Error fetching datasets:', error);
      throw error;
    }
  },

  // Get a specific dataset by ID
  getDatasetById: async (datasetId) => {
    try {
      const response = await apiClient.get(`/datasets/${datasetId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching dataset ${datasetId}:`, error);
      throw error;
    }
  },

  // Get clinical data for a specific dataset
  getClinicalData: async (datasetId) => {
    try {
      const response = await apiClient.get(`/datasets/${datasetId}/clinical`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching clinical data for ${datasetId}:`, error);
      throw error;
    }
  },

  // Get summary statistics for a specific dataset
  getSummaryStats: async (datasetId) => {
    try {
      const response = await apiClient.get(`/datasets/${datasetId}/summary`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching summary for ${datasetId}:`, error);
      throw error;
    }
  },

  // Run analysis on a dataset
  runAnalysis: async (datasetId, params) => {
    try {
      const response = await apiClient.post(`/datasets/${datasetId}/analysis`, params);
      return response.data;
    } catch (error) {
      console.error(`Error running analysis on ${datasetId}:`, error);
      throw error;
    }
  }
};

export default {
  datasetService
};