import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button, Card, Container, Row, Col } from 'react-bootstrap';

const Login = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // If already authenticated, redirect to home
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);
  
  return (
    <Container>
      <Row className="justify-content-center mt-5">
        <Col md={8} lg={6}>
          <Card className="shadow">
            <Card.Body className="p-5">
              <h2 className="text-center mb-4">NYUAD Bazaar</h2>
              <p className="text-center text-muted mb-4">
                Please log in with your NYU account to access the marketplace
              </p>
              
              <div className="d-grid gap-2">
                <Button 
                  variant="primary" 
                  size="lg" 
                  onClick={login}
                  className="d-flex align-items-center justify-content-center"
                >
                  <img 
                    src="/google-icon.png" 
                    alt="Google" 
                    className="me-2" 
                    style={{ width: '20px', height: '20px' }}
                  />
                  Login with NYU Google Account
                </Button>
              </div>
              
              <div className="mt-4">
                <p className="text-center text-muted small">
                  By logging in, you agree to the NYUAD Bazaar terms and conditions
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Login;