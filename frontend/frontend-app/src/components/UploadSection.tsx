import React, { useState, ChangeEvent, useEffect } from 'react';
import axios from 'axios';
import { Button, Form, Spinner, Alert, ProgressBar } from 'react-bootstrap';

interface UploadSectionProps {
  apiUrl: string;
  onSuccess: () => void;
  onError: (msg: string) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ apiUrl, onSuccess, onError }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setSuccessMessage('');
      setJobStatus(null);
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
      const response = await axios.post(`${apiUrl}/videos/upload`, formData);
      setUploading(false);
      setUploadedFilename(file.name);
      setJobStatus('processing');
      setSuccessMessage('Video uploaded successfully and AI job triggered!');
      setFile(null); // Reset the input after upload
      onSuccess();
    } catch {
      setUploading(false);
      onError('Failed to upload video.');
    }
  };

  // Poll job status
  useEffect(() => {
    let interval: NodeJS.Timeout;

    const checkJobStatus = async () => {
      if (!uploadedFilename) return;

      try {
        const response = await axios.get<{ status: string }>(`${apiUrl}/videos/job-status/${uploadedFilename}`);
        setJobStatus(response.data.status);

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch {
        onError('Failed to fetch job status.');
      }
    };

    if (jobStatus === 'processing') {
      interval = setInterval(checkJobStatus, 5000);
    }

    return () => clearInterval(interval);
  }, [jobStatus, uploadedFilename, apiUrl, onError]);

  const renderProgress = () => {
    switch (jobStatus) {
      case 'processing':
        return <ProgressBar animated now={60} label="Processing..." />;
      case 'completed':
        return <ProgressBar now={100} label="Completed" />;
      case 'failed':
        return <ProgressBar variant="danger" now={100} label="Failed" />;
      default:
        return null;
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

      <div className="mt-3">{renderProgress()}</div>
    </Form>
  );
};

export default UploadSection;
