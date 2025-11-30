import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCamera, faExclamationTriangle, faCheckCircle } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';

const ImageUpload = ({ onViolationDetected }) => {
  const [uploadResult, setUploadResult] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await axios.post('http://localhost:3001/api/upload_image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.success) {
        setUploadResult({
          success: !response.data.has_violations,
          message: response.data.message,
          hasViolations: response.data.has_violations,
          missingPpe: response.data.missing_ppe
        });
        
        setImagePreview(response.data.annotated_image);
        
        if (response.data.has_violations) {
          setTimeout(() => {
            alert(`⚠️ PPE VIOLATION DETECTED!\n\nMissing: ${response.data.missing_ppe.join(', ')}\n\nPlease ensure all required safety equipment is worn.`);
          }, 500);
        }
        
        if (onViolationDetected) {
          onViolationDetected();
        }
      } else {
        setUploadResult({
          success: false,
          message: response.data.error
        });
      }
    } catch (error) {
      setUploadResult({
        success: false,
        message: 'Upload failed: ' + error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="alert-panel">
      <div className="panel-header">
        <h2>
          <FontAwesomeIcon icon={faCamera} /> Image PPE Detection
        </h2>
      </div>
      
      <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <input
            type="file"
            id="imageInput"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleImageUpload}
          />
          
          <button
            onClick={() => document.getElementById('imageInput').click()}
            className="action-btn primary"
            style={{ width: '100%', marginBottom: '15px' }}
            disabled={loading}
          >
            <FontAwesomeIcon icon={faCamera} /> 
            {loading ? ' Analyzing...' : ' Upload Image for PPE Detection'}
          </button>
          
          {uploadResult && (
            <div className={`upload-result ${uploadResult.success ? 'success' : 'warning'}`}>
              <FontAwesomeIcon 
                icon={uploadResult.success ? faCheckCircle : faExclamationTriangle} 
              />
              {' ' + uploadResult.message}
            </div>
          )}
        </div>
        
        <div style={{ flex: 1, textAlign: 'center' }}>
          {imagePreview && (
            <img 
              src={imagePreview} 
              alt="Detected PPE" 
              className="preview-image"
              style={{
                maxWidth: '100%',
                maxHeight: '300px',
                borderRadius: '10px',
                boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageUpload;