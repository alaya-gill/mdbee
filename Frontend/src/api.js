// api.js
import axios from 'axios';
import globals from '../globals';

const api = axios.create({
  baseURL: globals.apiBaseUrl, // Replace with your API base URL
  headers: {
    'Content-Type': 'application/json',
  },
});


// Add a response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Handle unauthorized access
      console.log('User is not logged in or session expired');
      window.location.href = '/'; // Redirect to login
    }
    return Promise.reject(error);
  }
);

export default api;
