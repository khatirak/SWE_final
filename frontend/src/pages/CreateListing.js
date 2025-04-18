import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Container, Row, Col, Alert } from 'react-bootstrap';
import { Formik } from 'formik';
import * as Yup from 'yup';
import apiService from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

// Define validation schema
const listingSchema = Yup.object().shape({
  title: Yup.string()
    .min(1, 'Title must be at least 1 character')
    .max(100, 'Title cannot exceed 100 characters')
    .required('Title is required'),
  description: Yup.string()
    .test(
      'min-words',
      'Description must be at least 5 words',
      value => value && value.trim().split(/\s+/).filter(word => word.length > 0).length >= 5
    )
    .test(
      'max-words',
      'Description cannot exceed 200 words',
      value => !value || value.trim().split(/\s+/).filter(word => word.length > 0).length <= 200
    )
    .required('Description is required'),
  price: Yup.number()
    .min(0, 'Price cannot be negative')
    .required('Price is required'),
  category: Yup.string()
    .required('Category is required'),
  condition: Yup.string()
    .required('Condition is required')
});

const CreateListing = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [fileError, setFileError] = useState('');
  const [error, setError] = useState('');
  
  // Handle file selection
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    
    // Validate number of files
    if (files.length < 2) {
      setFileError('Please select at least 2 images');
      return;
    }
    
    if (files.length > 10) {
      setFileError('You can upload maximum 10 images');
      return;
    }
    
    // Validate file size (5MB limit per file)
    const oversizedFiles = files.filter(file => file.size > 5 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      setFileError('Some files exceed the 5MB size limit');
      return;
    }
    
    setSelectedFiles(files);
    setFileError('');
  };
  
  // Handle form submission
  const handleSubmit = async (values) => {
    if (selectedFiles.length < 2) {
      setError('Please select at least 2 images');
      return;
    }

    try {
      // Use placeholder image URLs for testing
      const placeholderImages = [
        "https://via.placeholder.com/300x200?text=Image+1",
        "https://via.placeholder.com/300x200?text=Image+2"
      ];

      // Create the listing data with placeholder images
      const listingData = {
        title: values.title,
        description: values.description,
        price: Math.round(parseFloat(values.price)), 
        category: values.category,
        condition: values.condition,
        status: "AVAILABLE",
        images: placeholderImages
      };

      // Create the listing
      const createdListing = await apiService.listings.create(listingData);
      navigate('/search');
    } catch (error) {
      console.error('Error creating listing:', error);
      setError(error.response?.data?.detail || 'Failed to create listing. Please try again.');
    }
  };
  
  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={8}>
          <Card className="shadow">
            <Card.Body className="p-4">
              <h2 className="text-center mb-4">Create a New Listing</h2>
              
              <Formik
                initialValues={{
                  title: '',
                  description: '',
                  price: '',
                  category: '',
                  condition: ''
                }}
                validationSchema={listingSchema}
                onSubmit={handleSubmit}
              >
                {({
                  values,
                  errors,
                  touched,
                  handleChange,
                  handleBlur,
                  handleSubmit,
                  isSubmitting
                }) => (
                  <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                      <Form.Label>Title *</Form.Label>
                      <Form.Control
                        type="text"
                        name="title"
                        value={values.title}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.title && errors.title}
                        placeholder="Enter a title for your item (max 100 characters)"
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.title}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Form.Group className="mb-3">
                      <Form.Label>Description *</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={4}
                        name="description"
                        value={values.description}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.description && errors.description}
                        placeholder="Describe your item (5-200 words)"
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.description}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Form.Group className="mb-3">
                      <Form.Label>Price (AED) *</Form.Label>
                      <Form.Control
                        type="number"
                        name="price"
                        value={values.price}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.price && errors.price}
                        placeholder="Enter price (0 for free items)"
                        min="0"
                      />
                      <Form.Control.Feedback type="invalid">
                        {errors.price}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Form.Group className="mb-3">
                      <Form.Label>Category *</Form.Label>
                      <Form.Select
                        name="category"
                        value={values.category}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.category && errors.category}
                      >
                        <option value="">Select a category</option>
                        <option value="apparel_accessories">Apparel & Accessories</option>
                        <option value="furniture">Furniture</option>
                        <option value="home_appliances">Home Appliances</option>
                        <option value="books_stationery">Books & Stationery</option>
                        <option value="beauty_personal_care">Beauty & Personal Care</option>
                        <option value="electronics_gadgets">Electronics & Gadgets</option>
                        <option value="misc_general_items">Misc. & General Items</option>
                      </Form.Select>
                      <Form.Control.Feedback type="invalid">
                        {errors.category}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Form.Group className="mb-3">
                      <Form.Label>Condition *</Form.Label>
                      <Form.Select
                        name="condition"
                        value={values.condition}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        isInvalid={touched.condition && errors.condition}
                      >
                        <option value="">Select condition</option>
                        <option value="brand_new">Brand New</option>
                        <option value="opened_unused">Opened-Unused</option>
                        <option value="good">Good</option>
                        <option value="used">Used</option>
                      </Form.Select>
                      <Form.Control.Feedback type="invalid">
                        {errors.condition}
                      </Form.Control.Feedback>
                    </Form.Group>
                    
                    <Form.Group className="mb-3">
                      <Form.Label>Images (2-10 images, max 5MB each) *</Form.Label>
                      <Form.Control
                        type="file"
                        multiple
                        onChange={handleFileChange}
                        accept="image/*"
                      />
                      {fileError && (
                        <Alert variant="danger" className="mt-2">
                          {fileError}
                        </Alert>
                      )}
                      {selectedFiles.length > 0 && (
                        <div className="mt-2">
                          <p>{selectedFiles.length} files selected</p>
                        </div>
                      )}
                    </Form.Group>
                    
                    {error && (
                      <Alert variant="danger" className="mt-3">
                        {typeof error === 'string' ? error : 'An error occurred. Please try again.'}
                      </Alert>
                    )}
                    
                    <div className="d-grid gap-2 mt-4">
                      <Button
                        variant="primary"
                        type="submit"
                        disabled={isSubmitting}
                      >
                        {isSubmitting ? 'Creating Listing...' : 'Create Listing'}
                      </Button>
                    </div>
                  </Form>
                )}
              </Formik>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default CreateListing;