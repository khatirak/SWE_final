import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Badge } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home = () => {
  const navigate = useNavigate();
  const { isAuthenticated, login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Dummy listings data
  const dummyListings = [
    {
      id: 'dummy1',
      title: 'MacBook Pro 2022',
      description: 'Excellent condition, barely used. M1 Pro chip, 16GB RAM, 512GB SSD.',
      price: 4500,
      status: 'AVAILABLE',
      category: 'Electronics & Gadgets',
      images: ['/placeholder-image.jpg'],
      created_at: new Date().toISOString()
    },
    {
      id: 'dummy2',
      title: 'IKEA Desk Lamp',
      description: 'White desk lamp, perfect for studying. Works great.',
      price: 50,
      status: 'RESERVED',
      category: 'Home Appliances',
      images: ['/placeholder-image.jpg'],
      created_at: new Date().toISOString()
    },
    {
      id: 'dummy3',
      title: 'Calculus Textbook',
      description: 'Calculus: Early Transcendentals. Great condition, minimal highlighting.',
      price: 90,
      status: 'AVAILABLE',
      category: 'Books & Stationery',
      images: ['/placeholder-image.jpg'],
      created_at: new Date().toISOString()
    }
  ];

  return (
    <Container>
      {/* Hero Section */}
      <div className="py-5 text-center bg-light rounded mb-5">
        <h1>Welcome to NYUAD Bazaar</h1>
        <p className="lead">Buy, sell, and give away items within the NYUAD community</p>
        
        <div className="d-flex justify-content-center gap-3 mt-4">
          {isAuthenticated ? (
            <Button 
              variant="primary" 
              size="lg" 
              onClick={() => navigate('/create-listing')}
            >
              Create a Listing
            </Button>
          ) : (
            <Button 
              variant="primary" 
              size="lg"
              onClick={login}
            >
              Login to Get Started
            </Button>
          )}

        </div>
      </div>
      
      
      
      {/* How It Works Section */}
      <section className="py-4 mb-5">
        <h2 className="text-center mb-4">How It Works</h2>
        <Row className="text-center">
          <Col md={4}>
            <div className="p-3">
              <div className="bg-primary text-white rounded-circle d-inline-flex justify-content-center align-items-center mb-3" style={{ width: '60px', height: '60px' }}>
                <h3 className="m-0">1</h3>
              </div>
              <h4>Sign In</h4>
              <p>Login with your NYU account to access the marketplace</p>
            </div>
          </Col>
          <Col md={4}>
            <div className="p-3">
              <div className="bg-primary text-white rounded-circle d-inline-flex justify-content-center align-items-center mb-3" style={{ width: '60px', height: '60px' }}>
                <h3 className="m-0">2</h3>
              </div>
              <h4>Create a Listing</h4>
              <p>List items you want to sell, give away, or exchange</p>
            </div>
          </Col>
          <Col md={4}>
            <div className="p-3">
              <div className="bg-primary text-white rounded-circle d-inline-flex justify-content-center align-items-center mb-3" style={{ width: '60px', height: '60px' }}>
                <h3 className="m-0">3</h3>
              </div>
              <h4>Connect & Exchange</h4>
              <p>Coordinate with buyers/sellers to complete the transaction</p>
            </div>
          </Col>
        </Row>
      </section>

      {/* Recent Listings Section */}
      <section className="mb-5">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Recent Listings</h2>
          {isAuthenticated && (
            <Link to="/search" className="btn btn-link">View All</Link>
          )}
        </div>
        
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : error ? (
          <div className="alert alert-danger">{error}</div>
        ) : (
          <Row>
            {dummyListings.map((item) => (
              <Col md={4} key={item.id} className="mb-4">
                <Card 
                  className="h-100" 
                  onClick={() => isAuthenticated ? navigate(`/listing/${item.id}`) : login()}
                  style={{ cursor: 'pointer' }}
                >
                  <Card.Img 
                    variant="top" 
                    src={item.images?.[0] || '/placeholder-image.jpg'} 
                    style={{ height: '200px', objectFit: 'cover' }}
                  />
                  <Card.Body>
                    <Card.Title className="text-truncate">{item.title}</Card.Title>
                    <Card.Text className="text-truncate">{item.description}</Card.Text>
                    <div className="d-flex justify-content-between align-items-center">
                      <h5 className="mb-0">
                        {item.price === 0 ? 'Free' : `${item.price} AED`}
                      </h5>
                      <Badge bg={
                        item.status === 'AVAILABLE' ? 'success' : 
                        item.status === 'RESERVED' ? 'warning' : 'secondary'
                      }>
                        {item.status}
                      </Badge>
                    </div>
                  </Card.Body>
                  <Card.Footer className="text-muted">
                    <small>{new Date(item.created_at).toLocaleDateString()}</small>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </section>
    </Container>
  );
};

export default Home;