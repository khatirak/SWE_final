import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AuthCallback = () => {
  const navigate = useNavigate();
  const { setUserData } = useAuth();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if user is authenticated
        const response = await fetch('http://localhost:8000/auth/me', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUserData(userData);
          navigate('/'); // Redirect to home page
        } else {
          navigate('/login'); // Redirect to login if not authenticated
        }
      } catch (error) {
        console.error('Auth check error:', error);
        navigate('/login');
      }
    };

    checkAuth();
  }, [navigate, setUserData]);

  return (
    <div className="text-center mt-5">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      <p className="mt-2">Completing authentication...</p>
    </div>
  );
};

export default AuthCallback;