// src/utils/helpers.js

/**
 * Format a number with commas as thousands separators
 * @param {number} num - The number to format
 * @returns {string} Formatted number
 */
export const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };
  
  /**
   * Format a decimal number to a specified number of decimal places
   * @param {number} num - The number to format
   * @param {number} decimals - Number of decimal places (default: 2)
   * @returns {string} Formatted number with specified decimal places
   */
  export const formatDecimal = (num, decimals = 2) => {
    return num.toFixed(decimals);
  };
  
  /**
   * Capitalize the first letter of each word in a string
   * @param {string} str - The string to capitalize
   * @returns {string} String with first letter of each word capitalized
   */
  export const capitalizeWords = (str) => {
    return str
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };
  
  /**
   * Format a database field name into a human-readable label
   * @param {string} fieldName - The field name to format
   * @returns {string} Formatted label
   */
  export const formatFieldLabel = (fieldName) => {
    return capitalizeWords(fieldName.replace(/_/g, ' '));
  };
  
  /**
   * Get a color from a gradient based on a value between 0 and 1
   * @param {number} value - Value between 0 and 1
   * @param {string} startColor - Hex color code for minimum value
   * @param {string} endColor - Hex color code for maximum value
   * @returns {string} Hex color code for the gradient position
   */
  export const getGradientColor = (value, startColor = '#FFFFFF', endColor = '#3182CE') => {
    // Convert hex to RGB
    const startRGB = hexToRgb(startColor);
    const endRGB = hexToRgb(endColor);
    
    // Interpolate between the colors
    const r = Math.round(startRGB.r + (endRGB.r - startRGB.r) * value);
    const g = Math.round(startRGB.g + (endRGB.g - startRGB.g) * value);
    const b = Math.round(startRGB.b + (endRGB.b - startRGB.b) * value);
    
    // Convert back to hex
    return rgbToHex(r, g, b);
  };
  
  /**
   * Convert hex color code to RGB object
   * @param {string} hex - Hex color code
   * @returns {Object} RGB values
   */
  export const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };
  
  /**
   * Convert RGB values to hex color code
   * @param {number} r - Red value (0-255)
   * @param {number} g - Green value (0-255)
   * @param {number} b - Blue value (0-255)
   * @returns {string} Hex color code
   */
  export const rgbToHex = (r, g, b) => {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  };
  
  /**
   * Truncate a string to a specified length and add ellipsis
   * @param {string} str - String to truncate
   * @param {number} length - Maximum length
   * @returns {string} Truncated string
   */
  export const truncateString = (str, length = 100) => {
    if (str.length <= length) return str;
    return str.slice(0, length) + '...';
  };
  
  /**
   * Group an array of objects by a specific key
   * @param {Array} array - Array of objects to group
   * @param {string} key - Key to group by
   * @returns {Object} Grouped objects
   */
  export const groupBy = (array, key) => {
    return array.reduce((result, item) => {
      const group = item[key];
      result[group] = result[group] || [];
      result[group].push(item);
      return result;
    }, {});
  };
  
  /**
   * Deep clone an object
   * @param {Object} obj - Object to clone
   * @returns {Object} Cloned object
   */
  export const deepClone = (obj) => {
    return JSON.parse(JSON.stringify(obj));
  };
  
  /**
   * Get a readable date string from a timestamp
   * @param {string|number} timestamp - Date timestamp
   * @returns {string} Formatted date
   */
  export const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };