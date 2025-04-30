import axios from 'axios';

const API_URL = 'http://localhost:8000';

const apiService = {
  listings: {
    create: async (data) => {
      try {
        const response = await axios.post(`${API_URL}/listings/`, data, {
          headers: {
            'Content-Type': 'application/json',
          },
          withCredentials: true,
        });
        return response.data;
      } catch (error) {
        console.error('Error creating listing:', error.response?.data || error);
        throw error;
      }
    },
    get: async (id) => {
      const response = await axios.get(`${API_URL}/listings/${id}/`, {
        withCredentials: true,
      });
      return response.data;
    },
    getUserListings: async (userId) => {
      const response = await axios.get(`${API_URL}//user/${userId}/listings`, {
        withCredentials: true,
      });
      return response.data;
    }
  },
  uploadImages: async (itemId, formData) => {
    const response = await axios.post(`${API_URL}/listings/${itemId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      withCredentials: true,
    });
    return response.data;
  },
  search: async (params) => {
    const response = await axios.get(`${API_URL}/search/`, {
      params,
      withCredentials: true,
    });
    return response.data;
  },
  auth: {
    me: async () => {
      const response = await axios.get(`${API_URL}/auth/me`, {
        withCredentials: true,
      });
      return response.data;
    },
    logout: async () => {
      const response = await axios.post(`${API_URL}/auth/logout`, {}, {
        withCredentials: true,
      });
      return response.data;
    },
  },
};

export default apiService; 