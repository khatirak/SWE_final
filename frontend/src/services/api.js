import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

// Configure axios to include credentials in requests
axios.defaults.withCredentials = true;

// Create API service object
const apiService = {
  // Authentication endpoints
  auth: {
    getCurrentUser: async () => {
      try {
        const response = await axios.get(`${API_URL}/auth/me`);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    logout: async () => {
      try {
        await axios.get(`${API_URL}/auth/logout`);
      } catch (error) {
        throw error;
      }
    }
  },
  
  // Listing endpoints
  listings: {
    getAll: async () => {
      try {
        const response = await axios.get(`${API_URL}/listings`);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    getById: async (id) => {
      try {
        const response = await axios.get(`${API_URL}/listings/${id}`);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    create: async (listingData) => {
      try {
        const response = await axios.post(`${API_URL}/listings`, listingData);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    update: async (id, updateData) => {
      try {
        const response = await axios.put(`${API_URL}/listings/${id}`, updateData);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    delete: async (id) => {
      try {
        await axios.delete(`${API_URL}/listings/${id}`);
      } catch (error) {
        throw error;
      }
    },
    
    uploadImages: async (id, imageFiles) => {
      try {
        const formData = new FormData();
        for (let i = 0; i < imageFiles.length; i++) {
          formData.append('files', imageFiles[i]);
        }
        
        const response = await axios.post(
          `${API_URL}/listings/${id}/images`, 
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        );
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    updateStatus: async (id, status) => {
      try {
        const response = await axios.put(`${API_URL}/listings/${id}/status?status=${status}`);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    getUserListings: async (userId) => {
      try {
        const response = await axios.get(`${API_URL}/listings/user/${userId}`);
        return response.data;
      } catch (error) {
        throw error;
      }
    }
  },
  
  // Search endpoints
  search: {
    searchItems: async (params) => {
      try {
        const response = await axios.get(`${API_URL}/search`, { params });
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    getCategories: async () => {
      try {
        const response = await axios.get(`${API_URL}/search/categories`);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    getPopularTags: async () => {
      try {
        const response = await axios.get(`${API_URL}/search/popular-tags`);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    savePreferences: async (preferences) => {
      try {
        const response = await axios.post(`${API_URL}/search/save-preferences`, preferences);
        return response.data;
      } catch (error) {
        throw error;
      }
    }
  },
  
  // Home page endpoints
  home: {
    getRecentListings: async (params) => {
      try {
        const response = await axios.get(`${API_URL}/home/recent`, { params });
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    getFeaturedListings: async () => {
      try {
        const response = await axios.get(`${API_URL}/home/featured`);
        return response.data;
      } catch (error) {
        throw error;
      }
    },
    
    getMarketplaceStats: async () => {
      try {
        const response = await axios.get(`${API_URL}/home/stats`);
        return response.data;
      } catch (error) {
        throw error;
      }
    }
  }
};

export default apiService;