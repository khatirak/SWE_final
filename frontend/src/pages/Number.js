// here is where users will be directed to after they login and there is no number assoicated to their account
// need ot have only digits and  '+' be accpetable - use regex
// this page should only ever appear once, wehen the user logins for the very forst timre and then the db field number should not mempty from this point

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Number = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { currentUser, setUserData } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate phone number format using regex
    // Allows digits and optionally a leading plus sign
    const phoneRegex = /^\+?\d+$/;
    
    if (!phoneRegex.test(phoneNumber)) {
      setError('Please enter a valid phone number (only digits and optional + sign allowed)');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await axios.post(`${API_URL}/user/update-phone`, 
        { phoneNumber },
        { withCredentials: true }
      );
      
      if (response.status === 200) {
        // Update the current user data with the new phone number
        setUserData({
          ...currentUser,
          phone: phoneNumber
        });
        
        // Redirect to home page after successful submission
        navigate('/');
      }
    } catch (error) {
      console.error('Error updating phone number:', error);
      setError('Failed to save phone number. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-center">Welcome to the App!</h3>
            </div>
            <div className="card-body">
              <p className="text-center mb-4">
                Please enter your phone number to complete your profile.
              </p>
              
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}
              
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="phoneNumber" className="form-label">Phone Number</label>
                  <input
                    type="tel"
                    className="form-control"
                    id="phoneNumber"
                    placeholder="e.g., +1234567890"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    required
                  />
                  <div className="form-text">
                    Enter your phone number with country code (only digits and + are allowed)
                  </div>
                </div>
                
                <div className="d-grid">
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Saving...
                      </>
                    ) : 'Continue'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Number;