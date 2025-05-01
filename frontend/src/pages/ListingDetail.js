import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Badge, Button, Alert, Spinner, ListGroup, Modal } from 'react-bootstrap';
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
  const [reservations, setReservations] = useState([]);
  const [loadingReservations, setLoadingReservations] = useState(false);
  const [myReservation, setMyReservation] = useState(null);
  const [showContactModal, setShowContactModal] = useState(false);
  const [buyersInfo, setBuyersInfo] = useState({});
  
  // Fetch listing details and reservation info
  useEffect(() => {
    const fetchListingData = async () => {
      try {
        const data = await apiService.listings.getById(id);
        setListing(data);
        
        // If user is authenticated, check different scenarios
        if (isAuthenticated && currentUser?.id) {
          // If user is the seller, fetch all reservation requests
          if (currentUser.id === data.seller_id) {
            await fetchReservations();
          } 
          // If user is not the seller, check if they have a reservation request
          else {
            await fetchMyReservation();
          }
        }
      } catch (error) {
        console.error('Error fetching listing:', error);
        setError('Failed to load listing details. It may have been removed or does not exist.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchListingData();
  }, [id, isAuthenticated, currentUser]);
  
  // Fetch all reservation requests (for seller)
  const fetchReservations = async () => {
    setLoadingReservations(true);
    try {
      console.log("Fetching reservations for listing:", id);
      const reservationData = await apiService.listings.getReservations(id);
      console.log("Reservations data received:", reservationData);
      setReservations(reservationData);
  
      // Fetch buyer details in parallel
      const buyers = await Promise.all(
        reservationData.map(r => apiService.user.getById(r.buyer_id))
      );
  
      const buyerMap = {};
      buyers.forEach(buyer => {
        buyerMap[buyer.id] = buyer;
      });
  
      setBuyersInfo(buyerMap);
    } catch (error) {
      console.error('Error fetching reservations:', error);
    } finally {
      setLoadingReservations(false);
    }
  };
  
  // Fetch user's own reservation (for buyer)
  const fetchMyReservation = async () => {
    try {
      const result = await apiService.listings.getMyReservationRequest(currentUser.id, id);
      if (result && result.length > 0) {
        setMyReservation(result[0]);
      }
    } catch (error) {
      console.error('Error fetching my reservation:', error);
    }
  };
  
  // Request to reserve an item
  const handleReserveClick = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    try {
      setReserving(true);
      await apiService.listings.reserve(currentUser.id, id);
      setSuccess('Reservation request sent successfully! The seller will be notified.');
      
      // Refresh my reservation status
      await fetchMyReservation();
      
    } catch (error) {
      console.error('Error reserving item:', error);
      setError('Failed to reserve this item. Please try again later.');
    } finally {
      setReserving(false);
    }
  };
  
  // Cancel reservation request (for buyer)
  const handleCancelReservation = async () => {
    try {
      await apiService.listings.cancelReservation(currentUser.id, id);
      setSuccess('Reservation request cancelled successfully.');
      setMyReservation(null);
      
      // If this was a confirmed reservation, refresh the listing
      const updatedListing = await apiService.listings.getById(id);
      setListing(updatedListing);
      
    } catch (error) {
      console.error('Error cancelling reservation:', error);
      setError('Failed to cancel reservation. Please try again later.');
    }
  };
  
  // Confirm a reservation request (for seller)
  const handleConfirmReservation = async (buyerId) => {
    try {
      await apiService.listings.confirmReservation(id, buyerId);
      setSuccess('Reservation confirmed! The buyer will be notified.');
      
      // Refresh reservations and listing data
      await fetchReservations();
      const updatedListing = await apiService.listings.getById(id);
      setListing(updatedListing);
      
    } catch (error) {
      console.error('Error confirming reservation:', error);
      setError('Failed to confirm reservation. Please try again later.');
    }
  };
  
  // Cancel a reservation request (for seller)
  const handleSellerCancelReservation = async (buyerId) => {
    try {
      await apiService.listings.cancelReservation(buyerId, id);
      setSuccess('Reservation request cancelled.');
      
      // Refresh reservations
      await fetchReservations();
      
      // If this was a confirmed reservation, refresh the listing
      const updatedListing = await apiService.listings.getById(id);
      setListing(updatedListing);
      
    } catch (error) {
      console.error('Error cancelling reservation:', error);
      setError('Failed to cancel reservation. Please try again later.');
    }
  };
  
  // Mark item as sold
  const handleMarkAsSold = async () => {
    try {
      await apiService.listings.markAsSold(id);
      setSuccess('Item marked as sold successfully!');
      
      // Refresh listing data
      const updatedListing = await apiService.listings.getById(id);
      setListing(updatedListing);
      
    } catch (error) {
      console.error('Error marking item as sold:', error);
      setError('Failed to mark item as sold. Please try again later.');
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
  const hasConfirmedReservation = reservations.some(r => r.status === 'confirmed');
  const hasMyPendingReservation = myReservation && myReservation.status === 'pending';
  const hasMyConfirmedReservation = myReservation && myReservation.status === 'confirmed';
  
  console.log("Debug info:", {
    isOwner,
    isAuthenticated,
    currentUserId: currentUser?.id,
    sellerId: listing.seller_id,
    status: listing.status,
    isAvailable,
    isReserved,
    isSold,
    reservations,
    hasConfirmedReservation,
    myReservation,
    hasMyPendingReservation,
    hasMyConfirmedReservation
  });
  
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
                  {isReserved ? 'RESERVED' : 'SOLD'}
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
          
          {/* Owner Actions */}
          {isOwner && (
            <Card className="mb-4">
              <Card.Body>
                <Card.Title>Manage Your Listing</Card.Title>
                
                {/* Debug info */}
                <div className="mb-3">
                  <small className="text-muted">
                    Status: {listing.status}, 
                    Reservations count: {reservations.length},
                    Has confirmed reservation: {hasConfirmedReservation ? 'Yes' : 'No'}
                  </small>
                </div>
                
                {isReserved && hasConfirmedReservation && (
                  <div className="mb-3">
                    <Alert variant="info">
                      This item is reserved. You can contact the buyer to arrange pickup.
                    </Alert>
                    <Button 
                      variant="success" 
                      className="me-2"
                      onClick={() => setShowContactModal(true)}
                    >
                      Contact Buyer
                    </Button>
                    <Button 
                      variant="primary"
                      onClick={handleMarkAsSold}
                    >
                      Mark as Sold
                    </Button>
                    <Button 
                      variant="outline-danger" 
                      className="ms-2"
                      onClick={() => handleSellerCancelReservation(reservations.find(r => r.status === 'confirmed').buyer_id)}
                    >
                      Cancel Reservation
                    </Button>
                  </div>
                )}
                
                <div>
                  <h6>Reservation Requests</h6>
                  {loadingReservations ? (
                    <Spinner animation="border" size="sm" />
                  ) : reservations.length > 0 ? (
                    <ListGroup>
                      {reservations.map((reservation, index) => (
                        <ListGroup.Item 
                          key={index}
                          className="d-flex justify-content-between align-items-center"
                        >
                          <div>
                            <strong>Buyer:</strong> {buyersInfo[reservation.buyer_id]?.name || reservation.buyer_id}
                            <div><small>Requested: {new Date(reservation.requested_at).toLocaleString()}</small></div>
                          </div>
                          <div>
                            {reservation.status !== 'confirmed' && (
                              <>
                                <Button
                                  variant="success"
                                  size="sm"
                                  className="me-2"
                                  onClick={() => handleConfirmReservation(reservation.buyer_id)}
                                >
                                  Confirm
                                </Button>
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => handleSellerCancelReservation(reservation.buyer_id)}
                                >
                                  Decline
                                </Button>
                              </>
                            )}
                            {reservation.status === 'confirmed' && (
                              <Badge bg="success">Confirmed</Badge>
                            )}
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <Alert variant="info">No reservation requests yet.</Alert>
                  )}
                </div>
              </Card.Body>
            </Card>
          )}
          
          {/* Buyer Actions */}
          {!isOwner && (
            <div className="d-grid gap-2">
              {isAuthenticated ? (
                <>
                  {isAvailable && !hasMyPendingReservation && (
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
                          Requesting...
                        </>
                      ) : (
                        'Request Reservation'
                      )}
                    </Button>
                  )}
                  
                  {hasMyPendingReservation && (
                    <>
                      <Alert variant="info">
                        You have requested to reserve this item. Waiting for seller approval.
                      </Alert>
                      <Button
                        variant="outline-danger"
                        onClick={handleCancelReservation}
                      >
                        Cancel Request
                      </Button>
                    </>
                  )}
                  
                  {hasMyConfirmedReservation && (
                    <>
                      <Alert variant="success">
                        Your reservation has been confirmed! Contact the seller to arrange pickup.
                      </Alert>
                      <Button
                        variant="primary"
                        onClick={() => setShowContactModal(true)}
                      >
                        Contact Seller
                      </Button>
                      <Button
                        variant="outline-danger"
                        onClick={handleCancelReservation}
                      >
                        Cancel Reservation
                      </Button>
                    </>
                  )}
                  
                  {isReserved && !hasMyConfirmedReservation && (
                    <Button variant="secondary" disabled>
                      This item is reserved
                    </Button>
                  )}
                  
                  {isSold && (
                    <Button variant="secondary" disabled>
                      This item has been sold
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
          )}
        </Col>
      </Row>
      
      {/* Contact Modal */}
      <Modal show={showContactModal} onHide={() => setShowContactModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Contact Information</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {isOwner && hasConfirmedReservation ? (
            <div>
              <p><strong>Buyer's Phone:</strong> {reservations.find(r => r.status === 'confirmed')?.buyer_phone || 'Not provided'}</p>
              <p>You can contact the buyer via WhatsApp to arrange pickup.</p>
            </div>
          ) : hasMyConfirmedReservation ? (
            <div>
              <p><strong>Seller's Phone:</strong> {myReservation?.seller_phone || 'Not provided'}</p>
              <p>You can contact the seller via WhatsApp to arrange pickup.</p>
            </div>
          ) : (
            <p>Contact information is not available.</p>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowContactModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default ListingDetail;