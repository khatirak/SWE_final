import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {

    const checkLoginStatus = async () => {
      try {
        const response = await axios.get(`${API_URL}/auth/me`, {
          withCredentials: true
        });
        
        if (response.status === 200) {
          setCurrentUser(response.data);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.log('User not authenticated');
        setCurrentUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    
    checkLoginStatus();
  }, []);

  // Login function - redirects to Google OAuth
  const login = () => {
    window.location.href = `${API_URL}/auth/login`;
  };

  // Logout function
  const logout = async () => {
    try {
      await axios.get(`${API_URL}/auth/logout`, {
        withCredentials: true
      });
      setCurrentUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Function to update user data after successful login
  const setUserData = (userData) => {
    setCurrentUser(userData);
    setIsAuthenticated(true);
    setLoading(false);
  };

  const value = {
    currentUser,
    isAuthenticated,
    loading,
    login,
    logout,
    setUserData
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
