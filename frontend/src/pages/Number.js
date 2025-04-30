// here is where users will be directed to after they login and there is no number assoicated to their account
// need ot have only digits and  '+' be accpetable - use regex
// this page should only ever appear once, wehen the user logins for the very forst timre and then the db field number should not mempty from this point

// Phone number input page for first-time login
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Row, Col, Form, Button, Alert, Card } from 'react-bootstrap';

// Access the API URL from environment variables
const API_URL = process.env.REACT_APP_API_URL;

const Number = () => {
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  // Check if user already has a phone number
  useEffect(() => {
    const checkPhone = async () => {
      try {
        const response = await axios.get(`${API_URL}/user/has_phone`, { withCredentials: true });
        if (response.data.has_phone) {
          // If user already has a phone number, redirect to home
          navigate('/');
        }
      } catch (err) {
        if (err.response?.status === 401) {
          // Not authenticated, redirect to login
          navigate('/login');
        }
        console.error('Error checking phone status:', err);
      }
    };

    checkPhone();
  }, [navigate]);

  const validatePhone = (phoneNumber) => {
    // Allow only digits and plus sign
    const phoneRegex = /^[+\d]+$/;
    return phoneRegex.test(phoneNumber);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate phone number
    if (!phone.trim()) {
      setError('Phone number is required');
      return;
    }

    if (!validatePhone(phone)) {
      setError('Phone number can only contain digits and + sign');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await axios.post(`${API_URL}/user/update_phone`, { phone }, { withCredentials: true });
      navigate('/');
    } catch (err) {
      console.error('Error updating phone number:', err);
      setError(err.response?.data?.detail || 'Failed to update phone number');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow-sm">
            <Card.Body className="p-4">
              <h2 className="text-center mb-4">Welcome to NYU Marketplace!</h2>
              <p className="text-center mb-4">
                Please enter your phone number to complete your registration.
                This will be used for contact purposes when items are reserved.
              </p>
              
              {error && <Alert variant="danger">{error}</Alert>}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Phone Number</Form.Label>
                  <Form.Control
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+1XXXXXXXXXX"
                    required
                    autoFocus
                  />
                  <Form.Text className="text-muted">
                    Example: +12123334444
                  </Form.Text>
                </Form.Group>
                
                <div className="d-grid">
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={isSubmitting}
                    className="mt-3"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit'}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Number;
