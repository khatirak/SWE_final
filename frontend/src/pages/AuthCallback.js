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
          console.log('Auth callback received user data:', userData);
          console.log('Phone field value:', userData.phone);
          setUserData(userData);
          
          // Check if user has a phone number (check for null, undefined, empty string)
          if (!userData.phone && userData.phone !== 0) {
            console.log('No phone number detected, redirecting to /number');
            // If no phone number, redirect to the number collection page
            navigate('/number');
          } else {
            console.log('Phone number found, redirecting to home');
            // If user has a phone number, redirect to home page
            navigate('/');
          }
        } else {
          console.log('Auth failed, redirecting to login');
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