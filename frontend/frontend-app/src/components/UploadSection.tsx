import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';
import { Button, Form, Spinner } from 'react-bootstrap';

interface UploadSectionProps {
  apiUrl: string;
  onSuccess: () => void;
  onError: (msg: string) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ apiUrl, onSuccess, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
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
      onSuccess();
    } catch {
      setUploading(false);
      onError('Failed to upload video.');
    }
  };

  return (
    <Form className="mb-4">
      <Form.Group controlId="videoUpload">
        <Form.Label>Select Video to Upload</Form.Label>
        <Form.Control type="file" accept="video/*" onChange={handleFileChange} />
      </Form.Group>
      <Button onClick={uploadVideo} className="mt-3" disabled={uploading}>
        {uploading ? <Spinner animation="border" size="sm" /> : 'Upload'}
      </Button>
    </Form>
  );
};

export default UploadSection;
