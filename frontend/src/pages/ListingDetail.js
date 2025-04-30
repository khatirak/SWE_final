import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Badge, Button, Alert, Spinner } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';

const ListingDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, currentUser } = useAuth();
  
  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reserving, setReserving] = useState(false);
  const [success, setSuccess] = useState(null);
  
  useEffect(() => {
    const fetchListing = async () => {
      try {
        const data = await apiService.listings.getById(id);
        setListing(data);
      } catch (error) {
        console.error('Error fetching listing:', error);
        setError('Failed to load listing details. It may have been removed or does not exist.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchListing();
  }, [id]);
  
  const handleReserveClick = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    try {
      setReserving(true);
      
      // In a real app, this would call a proper reservation endpoint
      // For now, we'll simulate it with a status update
      await apiService.listings.updateStatus(id, 'reserved');
      
      setSuccess('Item reserved successfully! The seller will be notified.');
      
      // Update the listing in our state
      setListing(prev => ({
        ...prev,
        status: 'reserved',
        reserved_by: currentUser.id
      }));
    } catch (error) {
      console.error('Error reserving item:', error);
      setError('Failed to reserve this item. Please try again later.');
    } finally {
      setReserving(false);
    }
  };

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container className="py-4">
        <Alert variant="danger">{error}</Alert>
        <Button variant="primary" onClick={() => navigate(-1)}>
          Go Back
        </Button>
      </Container>
    );
  }
  
  if (!listing) {
    return (
      <Container className="py-4">
        <Alert variant="warning">Listing not found</Alert>
        <Button variant="primary" onClick={() => navigate('/')}>
          Back to Home
        </Button>
      </Container>
    );
  }
  
  const isOwner = isAuthenticated && currentUser?.id === listing.seller_id;
  const isAvailable = listing.status === 'available';
  const isReserved = listing.status === 'reserved';
  const isSold = listing.status === 'sold';
  const isReservedByCurrentUser = isAuthenticated && isReserved && currentUser?.id === listing.reserved_by;
  
  return (
    <Container className="py-4">
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      <Row>
        {/* Image Gallery */}
        <Col md={6} className="mb-4">
          <div className="position-relative">
            {listing.images && listing.images.length > 0 ? (
              <img
                src={listing.images[0]}
                alt={listing.title}
                className="img-fluid rounded"
                style={{ maxHeight: '400px', width: '100%', objectFit: 'cover' }}
              />
            ) : (
              <div 
                className="bg-secondary d-flex align-items-center justify-content-center rounded"
                style={{ height: '400px' }}
              >
                <p className="text-white">No image available</p>
              </div>
            )}
            
            {!isAvailable && (
              <div 
                className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                style={{ background: 'rgba(0,0,0,0.5)' }}
              >
                <h3 className="text-white">
                  {isReserved ? 'reserved' : 'sold'}
                </h3>
              </div>
            )}
          </div>
          
          {listing.images && listing.images.length > 1 && (
            <Row className="mt-2">
              {listing.images.slice(1, 4).map((img, index) => (
                <Col key={index} xs={4}>
                  <img
                    src={img}
                    alt={`${listing.title} ${index + 2}`}
                    className="img-fluid rounded"
                    style={{ height: '100px', width: '100%', objectFit: 'cover' }}
                  />
                </Col>
              ))}
              {listing.images.length > 4 && (
                <div className="mt-2 text-center">
                  <small className="text-muted">
                    +{listing.images.length - 4} more images
                  </small>
                </div>
              )}
            </Row>
          )}
        </Col>
        
        {/* Listing Details */}
        <Col md={6}>
          <div className="d-flex justify-content-between align-items-start mb-3">
            <h2>{listing.title}</h2>
            <h3>
              {listing.price === 0 ? (
                <Badge bg="success">FREE</Badge>
              ) : (
                <span className="text-primary">{listing.price} AED</span>
              )}
            </h3>
          </div>
          
          <div className="mb-4">
            <Badge bg="secondary" className="me-2">{listing.category}</Badge>
            <Badge bg="secondary">{listing.condition}</Badge>
            <div className="mt-2 text-muted">
              Posted on {new Date(listing.created_at).toLocaleDateString()}
            </div>
          </div>
          
          <Card className="mb-4">
            <Card.Body>
              <Card.Title>Description</Card.Title>
              <Card.Text style={{ whiteSpace: 'pre-line' }}>
                {listing.description}
              </Card.Text>
            </Card.Body>
          </Card>
          
          <div className="d-grid gap-2">
            {isAuthenticated ? (
              <>
                {isOwner ? (
                  <Alert variant="info">
                    This is your listing. You can manage it from your profile.
                  </Alert>
                ) : isAvailable ? (
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={handleReserveClick}
                    disabled={reserving}
                  >
                    {reserving ? (
                      <>
                        <Spinner
                          as="span"
                          animation="border"
                          size="sm"
                          role="status"
                          aria-hidden="true"
                          className="me-2"
                        />
                        Reserving...
                      </>
                    ) : (
                      'Request Reservation'
                    )}
                  </Button>
                ) : isReservedByCurrentUser ? (
                  <Alert variant="success">
                    You have reserved this item. Contact the seller to arrange pickup.
                  </Alert>
                ) : (
                  <Button variant="secondary" disabled>
                    {isSold ? 'This item has been sold' : 'This item is reserved'}
                  </Button>
                )}
              </>
            ) : (
              <Button
                variant="primary"
                size="lg"
                onClick={() => navigate('/login')}
              >
                Sign in to Reserve
              </Button>
            )}
            
            <Button
              variant="outline-secondary"
              onClick={() => navigate(-1)}
            >
              Back to Listings
            </Button>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default ListingDetail;