import React, { useState } from 'react';
import axios from 'axios';
import { Card, Button, Row, Col, Modal } from 'react-bootstrap';

interface VideoListProps {
  apiUrl: string;
  videos: { uploaded: string[]; processed: string[] };
  onDelete: () => void;
  onError: (msg: string) => void;
}

const VideoList: React.FC<VideoListProps> = ({ apiUrl, videos, onDelete, onError }) => {
  const [selectedMetadata, setSelectedMetadata] = useState<any | null>(null);
  const [showMetadata, setShowMetadata] = useState(false);

  // Handle video deletion
  const deleteVideo = async (folder: string, filename: string) => {
    try {
      await axios.delete(`${apiUrl}/videos/${folder}/${filename}`);
      onDelete();
    } catch {
      onError('Failed to delete video.');
    }
  };

  // Fetch metadata for a processed video
  const fetchMetadata = async (filename: string) => {
    try {
      const response = await axios.get(`${apiUrl}/videos/metadata/${filename}.json`);
      setSelectedMetadata(response.data);
      setShowMetadata(true);
    } catch {
      onError('Failed to fetch metadata.');
    }
  };

  // Render video cards
  const renderVideoCard = (folder: string, filename: string, isProcessed = false) => (
    <Col key={filename} md={6} lg={4} className="mb-4">
      <Card>
        <Card.Body>
          <Card.Title>{filename}</Card.Title>
          <video width="100%" controls>
            <source src={`${apiUrl}/videos/${folder}/${filename}`} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <div className="mt-2">
            {isProcessed && (
              <Button
                variant="info"
                size="sm"
                className="me-2"
                onClick={() => fetchMetadata(filename)}
              >
                View Metadata
              </Button>
            )}
            <Button
              variant="danger"
              size="sm"
              onClick={() => deleteVideo(folder, filename)}
            >
              Delete
            </Button>
          </div>
        </Card.Body>
      </Card>
    </Col>
  );

  return (
    <>
      <h3>Uploaded Videos</h3>
      <Row>
        {videos.uploaded.length > 0 ? (
          videos.uploaded.map((video) => renderVideoCard('uploaded', video))
        ) : (
          <p>No uploaded videos.</p>
        )}
      </Row>

      <h3>Processed Videos</h3>
      <Row>
        {videos.processed.length > 0 ? (
          videos.processed.map((video) => renderVideoCard('processed', video, true))
        ) : (
          <p>No processed videos.</p>
        )}
      </Row>

      {/* Metadata Modal */}
      <Modal show={showMetadata} onHide={() => setShowMetadata(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Video Metadata</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedMetadata ? (
            <pre>{JSON.stringify(selectedMetadata, null, 2)}</pre>
          ) : (
            <p>No metadata available.</p>
          )}
        </Modal.Body>
      </Modal>
    </>
  );
};

export default VideoList;
