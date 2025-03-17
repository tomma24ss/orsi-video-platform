import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';
import { Button, Form, Spinner, Alert } from 'react-bootstrap';

interface UploadSectionProps {
  apiUrl: string;
  onSuccess: () => void;
  onError: (msg: string) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ apiUrl, onSuccess, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setSuccessMessage('');
    }
  };

  const uploadVideo = async () => {
    if (!file) {
      onError('No file selected!');
      return;
    }

    const formData = new FormData();
    formData.append('video', file);
    setUploading(true);

    try {
      await axios.post(`${apiUrl}/videos/upload`, formData);
      setUploading(false);
      setSuccessMessage('Video uploaded successfully and AI job triggered!');
      setFile(null); // Reset the input after upload
      onSuccess();
    } catch {
      setUploading(false);
      onError('Failed to upload video.');
    }
  };

  return (
    <Form className="mb-4">
      {successMessage && (
        <Alert variant="success" onClose={() => setSuccessMessage('')} dismissible>
          {successMessage}
        </Alert>
      )}

      <Form.Group controlId="videoUpload">
        <Form.Label>Select Video to Upload</Form.Label>
        <Form.Control
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          disabled={uploading}
        />
      </Form.Group>

      <Button onClick={uploadVideo} className="mt-3" disabled={uploading || !file}>
        {uploading ? <Spinner animation="border" size="sm" /> : 'Upload'}
      </Button>
    </Form>
  );
};

export default UploadSection;
