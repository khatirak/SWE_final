import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Button, Tabs, Tab, Alert, Spinner } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';

const Profile = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  const [userListings, setUserListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchUserListings = async () => {
      if (!currentUser?.id) return;
      
      try {
        const listings = await apiService.listings.getUserListings(currentUser.id);
        setUserListings(listings);
      } catch (error) {
        console.error('Error fetching user listings:', error);
        setError('Failed to load your listings. Please tryAz again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchUserListings();
  }, [currentUser]);
  
  const handleCreateListing = () => {
    navigate('/create-listing');
  };
  
  const handleEditListing = (id) => {
    navigate(`/listing/${id}/edit`);
  };
  
  const handleDeleteListing = async (id) => {
    if (!window.confirm('Are you sure you want to delete this listing?')) {
      return;
    }
    
    try {
      await apiService.listings.delete(id);
      setUserListings(listings => listings.filter(listing => listing.id !== id));
    } catch (error) {
      console.error('Error deleting listing:', error);
      alert('Failed to delete listing. Please try again later.');
    }
  };
  
  const handleViewListing = (id) => {
    navigate(`/listing/${id}`);
  };
  
  // Filter listings by status
  const availableListings = userListings.filter(listing => listing.status === 'available');
  const reservedListings = userListings.filter(listing => listing.status === 'reserved');
  const soldListings = userListings.filter(listing => listing.status === 'sold');
  
  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }
  
  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>My Profile</h2>
        <Button 
          variant="primary" 
          onClick={handleCreateListing}
        >
          Create New Listing
        </Button>
      </div>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={2}>
              <div className="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center mb-3" style={{ width: '80px', height: '80px' }}>
                <h2>{currentUser?.name?.charAt(0) || 'U'}</h2>
              </div>
            </Col>
            <Col md={10}>
              <h4>{currentUser?.name || 'User'}</h4>
              <p className="text-muted">{currentUser?.email}</p>
              <p>Member since: {new Date(currentUser?.created_at || Date.now()).toLocaleDateString()}</p>
            </Col>
          </Row>
        </Card.Body>
      </Card>
      
      <h3 className="mb-3">My Listings</h3>
      
      <Tabs defaultActiveKey="available" className="mb-4">
        <Tab eventKey="available" title={`Available (${availableListings.length})`}>
          <ListingsGrid 
            listings={availableListings} 
            onView={handleViewListing}
            onEdit={handleEditListing}
            onDelete={handleDeleteListing}
          />
        </Tab>
        <Tab eventKey="reserved" title={`Reserved (${reservedListings.length})`}>
          <ListingsGrid 
            listings={reservedListings} 
            onView={handleViewListing}
            onEdit={handleEditListing}
            onDelete={handleDeleteListing}
          />
        </Tab>
        <Tab eventKey="sold" title={`Sold (${soldListings.length})`}>
          <ListingsGrid 
            listings={soldListings} 
            onView={handleViewListing}
            onEdit={handleEditListing}
            onDelete={handleDeleteListing}
          />
        </Tab>
      </Tabs>
      
      {userListings.length === 0 && (
        <div className="text-center py-5">
          <p>You haven't created any listings yet.</p>
          <Button 
            variant="primary" 
            onClick={handleCreateListing}
          >
            Create Your First Listing
          </Button>
        </div>
      )}
    </Container>
  );
};

// Helper component for displaying listings in a grid
const ListingsGrid = ({ listings, onView, onEdit, onDelete }) => {
  if (listings.length === 0) {
    return (
      <div className="text-center py-4">
        <p>No listings in this category</p>
      </div>
    );
  }
  
  return (
    <Row>
      {listings.map((listing) => (
        <Col md={4} key={listing.id} className="mb-4">
          <Card>
            <Card.Img 
              variant="top" 
              src={listing.images?.[0] || '/placeholder-image.jpg'} 
              style={{ height: '150px', objectFit: 'cover' }}
              onClick={() => onView(listing.id)}
              className="cursor-pointer"
            />
            <Card.Body>
              <Card.Title className="text-truncate">{listing.title}</Card.Title>
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">
                  {listing.price === 0 ? 'Free' : `${listing.price} AED`}
                </h5>
                <Badge bg={
                  listing.status === 'available' ? 'success' : 
                  listing.status === 'reserved' ? 'warning' : 'secondary'
                }>
                  {listing.status}
                </Badge>
              </div>
            </Card.Body>
            <Card.Footer>
              <div className="d-flex justify-content-between">
                <Button 
                  variant="outline-primary" 
                  size="sm"
                  onClick={() => onView(listing.id)}
                >
                  View
                </Button>
                <Button 
                  variant="outline-secondary" 
                  size="sm"
                  onClick={() => onEdit(listing.id)}
                >
                  Edit
                </Button>
                <Button 
                  variant="outline-danger" 
                  size="sm"
                  onClick={() => onDelete(listing.id)}
                >
                  Delete
                </Button>
              </div>
            </Card.Footer>
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default Profile;