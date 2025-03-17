import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Alert } from 'react-bootstrap';
import UploadSection from './components/UploadSection';
import VideoList from './components/VideoList';

const API_URL = process.env.REACT_APP_API_URL as string;

interface VideoData {
  uploaded: string[];
  processed: string[];
}

const App: React.FC = () => {
  const [videos, setVideos] = useState<VideoData>({ uploaded: [], processed: [] });
  const [alert, setAlert] = useState<string>('');

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await axios.get<VideoData>(`${API_URL}/videos`);
      setVideos(response.data);
    } catch (error) {
      setAlert('Failed to fetch videos.');
    }
  };

  return (
    <Container className="py-4">
      <h1 className="text-center mb-4">🎥 ORSI Video Platform</h1>

      {alert && (
        <Alert variant="danger" dismissible onClose={() => setAlert('')}>
          {alert}
        </Alert>
      )}

      <UploadSection apiUrl={API_URL} onSuccess={fetchVideos} onError={setAlert} />

      <VideoList apiUrl={API_URL} videos={videos} onDelete={fetchVideos} onError={setAlert} />
    </Container>
  );
};

export default App;
