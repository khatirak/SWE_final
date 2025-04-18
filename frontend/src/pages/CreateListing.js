import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Container, Row, Col, Alert } from 'react-bootstrap';
import { Formik } from 'formik';
import * as Yup from 'yup';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// Define validation schema
const listingSchema = Yup.object().shape({
  title: Yup.string()
    .min(3, 'Title must be at least 3 characters')
    .max(100, 'Title cannot exceed 100 characters')
    .required('Title is required'),
  description: Yup.string()
    .min(10, 'Description must be at least 10 characters')
    .max(1000, 'Description cannot exceed 1000 characters')
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
  const [categories, setCategories] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [fileError, setFileError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
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
  const handleSubmit = async (values, { setSubmitting, resetForm, setErrors }) => {
    setIsSubmitting(true);
    
    if (selectedFiles.length < 2) {
      setFileError('Please select at least 2 images');
      setIsSubmitting(false);
      return;
    }
    
    try {
      // Create listing first
      const listingData = {
        ...values,
        seller_id: currentUser.id
      };
      
      const createdListing = await apiService.listings.create(listingData);
      
      // Then upload images
      await apiService.listings.uploadImages(createdListing.id, selectedFiles);
      
      // Reset form and redirect
      resetForm();
      setSelectedFiles([]);
      navigate(`/listing/${createdListing.id}`);
    } catch (error) {
      console.error('Error creating listing:', error);
      if (error.response && error.response.data) {
        setErrors(error.response.data);
      }
    } finally {
      setIsSubmitting(false);
      setSubmitting(false);
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
                        placeholder="Describe your item (max 200 words)"
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
                        {categories.map((category, index) => (
                          <option key={index} value={category}>
                            {category}
                          </option>
                        ))}
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
                        <option value="Brand New">Brand New</option>
                        <option value="Opened-Unused">Opened-Unused</option>
                        <option value="Good">Good</option>
                        <option value="Used">Used</option>
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