// src/services/heatmapapi.js

/**
 * Service for handling API calls related to heatmap data
 */
const API_URL = "http://127.0.0.1:4000/";

export const ApiService = {
  /**
   * Fetches heatmap data for visualization
   * @param {string} endpoint - API endpoint for fetching heatmap data
   * @returns {Promise<Object>} - Promise resolving to response
   */
  async getHeatmapData(endpoint) {
    try {
      const response = await fetch(API_URL + endpoint);
      return response;
    } catch (error) {
      console.error("Error in API call:", error);
      throw error;
    }
  },
};
