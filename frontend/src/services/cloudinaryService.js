import { Cloudinary } from '@cloudinary/url-gen';
import { auto } from '@cloudinary/url-gen/actions/resize';
import { autoGravity } from '@cloudinary/url-gen/qualifiers/gravity';
import axios from 'axios';

// Extract cloud name from the Cloudinary URL
const CLOUDINARY_URL = process.env.REACT_APP_CLOUDINARY_URL;
if (!CLOUDINARY_URL) {
  throw new Error('REACT_APP_CLOUDINARY_URL environment variable is not set');
}

// Parse the cloud name from the URL
const urlParts = CLOUDINARY_URL.split('@');
if (urlParts.length < 2) {
  throw new Error('Invalid Cloudinary URL format');
}

const cloudName = urlParts[1].split('.')[0];
if (!cloudName) {
  throw new Error('Could not extract cloud name from Cloudinary URL');
}

// Initialize Cloudinary instance
const cld = new Cloudinary({ 
  cloud: { 
    cloudName: cloudName
  } 
});

// Cloudinary configuration
const CLOUDINARY_UPLOAD_URL = `https://api.cloudinary.com/v1_1/${cloudName}/image/upload`;
const UPLOAD_PRESET = 'nyuad_bazaar';
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// Extract API key and secret from the Cloudinary URL
const [apiKey, apiSecret] = CLOUDINARY_URL.split('@')[0].split('//')[1].split(':');

const cloudinaryService = {
  // Function to get a Cloudinary image instance with transformations
  getImage: (publicId) => {
    return cld
      .image(publicId)
      .format('auto')
      .quality('auto')
      .resize(auto().gravity(autoGravity()).width(500).height(500));
  },

  // Function to upload an image and return the secure URL
  uploadImage: async (file) => {
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      throw new Error(`File size exceeds 5MB limit: ${file.name}`);
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      throw new Error(`Invalid file type: ${file.name}. Only images are allowed.`);
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', UPLOAD_PRESET);
    formData.append('folder', 'nyuad_bazaar');

    try {
      const response = await axios.post(CLOUDINARY_UPLOAD_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: false, // Set to false for Cloudinary uploads
      });
      
      if (!response.data.secure_url) {
        throw new Error('No secure URL returned from Cloudinary');
      }
      
      return response.data.secure_url;
    } catch (error) {
      console.error('Error uploading image to Cloudinary:', error.response?.data || error);
      if (error.response?.data?.error) {
        throw new Error(`Cloudinary error: ${error.response.data.error.message}`);
      }
      throw new Error('Failed to upload image to Cloudinary');
    }
  },

  // Function to upload multiple images
  uploadImages: async (files) => {
    if (!files || files.length === 0) {
      throw new Error('No files provided for upload');
    }

    if (files.length < 2) {
      throw new Error('At least 2 images are required');
    }

    if (files.length > 10) {
      throw new Error('Maximum 10 images allowed');
    }

    try {
      const uploadPromises = Array.from(files).map(file => 
        cloudinaryService.uploadImage(file)
      );
      
      const urls = await Promise.all(uploadPromises);
      
      if (urls.length < 2) {
        throw new Error('At least 2 images are required');
      }
      
      return urls;
    } catch (error) {
      console.error('Error uploading images to Cloudinary:', error);
      throw error;
    }
  }
};

export default cloudinaryService; 