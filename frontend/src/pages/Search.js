// frontend/src/pages/search.js
import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Row, 
  Col, 
  Form, 
  Button, 
  Card, 
  ListGroup,
  Spinner,
  Badge,
  Alert
} from 'react-bootstrap';
import apiService from '../services/api';

const Search = () => {

  // Add this near the top of your component, after your state declarations
  const [useMockData, setUseMockData] = useState(true); // Set to true to use mock data

  // URL search params
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // State for search filters
  const [keyword, setKeyword] = useState(searchParams.get('keyword') || '');
  const [category, setCategory] = useState(searchParams.get('category') || '');
  const [minPrice, setMinPrice] = useState(searchParams.get('minPrice') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('maxPrice') || '');
  const [condition, setCondition] = useState(searchParams.get('condition') || '');
  const [status, setStatus] = useState(searchParams.get('status') || 'AVAILABLE');
  
  // State for search results
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [noResults, setNoResults] = useState(false);
  
  // State for filter options
  const [categories, setCategories] = useState([]);

  // Add this mock data to your component
const mockListings = [
  {
    id: "mock1",
    title: "Modern Coffee Table",
    description: "Beautiful wood coffee table in excellent condition",
    price: 150,
    category: "Furniture",
    status: "AVAILABLE",
    images: ["/placeholder-image.jpg"],
  },
  {
    id: "mock2",
    title: "iPad Pro 11-inch (2021)",
    description: "Barely used iPad Pro with Apple Pencil included",
    price: 1200,
    category: "Electronics & Gadgets",
    status: "AVAILABLE",
    images: ["/placeholder-image.jpg"],
  },
  {
    id: "mock3",
    title: "Desk Lamp",
    description: "Adjustable desk lamp with multiple brightness settings",
    price: 45,
    category: "Home Appliances",
    status: "RESERVED",
    images: ["/placeholder-image.jpg"],
  },
  {
    id: "mock4",
    title: "University Textbooks",
    description: "Set of 3 engineering textbooks in good condition",
    price: 75,
    category: "Books & Stationery",
    status: "AVAILABLE",
    images: ["/placeholder-image.jpg"],
  },
  {
    id: "mock5",
    title: "Winter Coat",
    description: "Warm winter coat, size M, worn only a few times",
    price: 90,
    category: "Apparel & Accessories",
    status: "AVAILABLE",
    images: ["/placeholder-image.jpg"],
  },
  {
    id: "mock6",
    title: "Plant Stand",
    description: "Wooden plant stand, perfect for indoor plants",
    price: 0,
    category: "Furniture",
    status: "AVAILABLE",
    images: ["/placeholder-image.jpg"],
  }
];
  
  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const categoriesData = await apiService.search.getCategories();
        setCategories(categoriesData);
      } catch (error) {
        console.error('Error fetching categories:', error);
        // Set default categories in case API fails
        setCategories([
          'Apparel & Accessories',
          'Furniture',
          'Home Appliances',
          'Books & Stationery',
          'Beauty & Personal Care',
          'Electronics & Gadgets',
          'Misc. & General Items'
        ]);
      }
    };
    
    fetchCategories();
  }, []);
  
  
  useEffect(() => {
    // Load all listings when component mounts
    performSearch();
  }, []);
  
  // Modify your performSearch function
  const performSearch = async () => {
    setLoading(true);
    setError(null);
    setNoResults(false);
    
    try {
      // Build query parameters from current state
      const params = {};
      if (keyword) params.q = keyword;
      if (category && category !== "") params.category = category;
      if (minPrice && minPrice !== "") params.min_price = minPrice;
      if (maxPrice && maxPrice !== "") params.max_price = maxPrice;
      if (condition && condition !== "") params.condition = condition;
      if (status && status !== "") params.status = status.toLowerCase();
      
      // Notice the URL changed from /api/search to /search
      const queryString = new URLSearchParams(params).toString();
      const response = await fetch(`http://localhost:8000/search?${queryString}`);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Received listings:", data);
      
      if (data.length === 0) {
        setNoResults(true);
      }
      
      setResults(data);
    } catch (error) {
      console.error('Error searching items:', error);
      setError('An error occurred while searching. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle search form submission
  const handleSearch = (e) => {
    e.preventDefault();
    
    // Build search params
    const params = new URLSearchParams();
    
    if (keyword) params.set('keyword', keyword);
    if (category) params.set('category', category);
    if (minPrice) params.set('minPrice', minPrice);
    if (maxPrice) params.set('maxPrice', maxPrice);
    if (condition) params.set('condition', condition);
    if (status) params.set('status', status);
    
    // Update URL search params
    setSearchParams(params);
  };
  
  // Handle reset filters
  const handleReset = () => {
    setKeyword('');
    setCategory('');
    setMinPrice('');
    setMaxPrice('');
    setCondition('');
    setStatus('AVAILABLE');
    setSearchParams({});
    setResults([]);
    setNoResults(false);
  };
  
  // Navigate to listing detail
  const handleListingClick = (id) => {
    navigate(`/listing/${id}`);
  };
  
  return (
    <Container>
      <h2 className="mb-4">Search Items</h2>
      
      <Row>
        {/* Filter sidebar */}
        <Col md={3}>
          <Card className="mb-4">
            <Card.Header>
              <strong>Filters</strong>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSearch}>
                <Form.Group className="mb-3">
                  <Form.Label>Keyword</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Search..."
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    <option value="">All Categories</option>
                    {categories.map((cat, index) => (
                      <option key={index} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Price Range (AED)</Form.Label>
                  <Row>
                    <Col>
                      <Form.Control
                        type="number"
                        placeholder="Min"
                        value={minPrice}
                        onChange={(e) => setMinPrice(e.target.value)}
                        min="0"
                      />
                    </Col>
                    <Col>
                      <Form.Control
                        type="number"
                        placeholder="Max"
                        value={maxPrice}
                        onChange={(e) => setMaxPrice(e.target.value)}
                        min="0"
                      />
                    </Col>
                  </Row>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Condition</Form.Label>
                  <Form.Select
                    value={condition}
                    onChange={(e) => setCondition(e.target.value)}
                  >
                    <option value="">Any Condition</option>
                    <option value="Brand New">Brand New</option>
                    <option value="Opened-Unused">Opened-Unused</option>
                    <option value="Good">Good</option>
                    <option value="Used">Used</option>
                  </Form.Select>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Status</Form.Label>
                  <Form.Select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                  >
                    <option value="AVAILABLE">Available Only</option>
                    <option value="RESERVED">Reserved Only</option>
                    <option value="SOLD">Sold Only</option>
                    <option value="">All</option>
                  </Form.Select>
                </Form.Group>
                
                <div className="d-grid gap-2">
                  <Button variant="primary" type="submit">
                    Search
                  </Button>
                  <Button 
                    variant="outline-secondary" 
                    type="button"
                    onClick={handleReset}
                  >
                    Reset Filters
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
        
        {/* Results */}
        <Col md={9}>
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
              <p className="mt-2">Loading listings...</p>
            </div>
          ) : error ? (
            <Alert variant="danger">{error}</Alert>
          ) : noResults ? (
            <div className="text-center py-5">
              <p>No items found matching your search criteria.</p>
              <p>Try adjusting your filters or search for something else.</p>
            </div>
          ) : results.length > 0 ? (
            <>
              <p>{results.length} items found</p>
              <Row>
                {results.map((item) => (
                  <Col md={4} key={item.id} className="mb-4">
                    <Card 
                      className="h-100 listing-card" 
                      onClick={() => handleListingClick(item.id)}
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
                        <small>Category: {item.category}</small>
                      </Card.Footer>
                    </Card>
                  </Col>
                ))}
              </Row>
            </>
          ) : (
            <div className="text-center py-5">
              <p>No items available at this time.</p>
              <p>Check back later or try different search criteria.</p>
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Search;