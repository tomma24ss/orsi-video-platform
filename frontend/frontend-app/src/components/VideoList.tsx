import React from 'react';
import axios from 'axios';
import { Card, Button, Row, Col } from 'react-bootstrap';

interface VideoListProps {
  apiUrl: string;
  videos: string[];
  onDelete: () => void;
  onError: (msg: string) => void;
}

const VideoList: React.FC<VideoListProps> = ({ apiUrl, videos, onDelete, onError }) => {
  const deleteVideo = async (filename: string) => {
    try {
      await axios.delete(`${apiUrl}/videos/${filename}`);
      onDelete();
    } catch {
      onError('Failed to delete video.');
    }
  };

  return (
    <Row>
      {videos.map((video) => (
        <Col key={video} md={6} lg={4} className="mb-4">
          <Card>
            <Card.Body>
              <Card.Title>{video}</Card.Title>
              <video width="100%" controls>
                <source src={`${apiUrl}/videos/${video}`} type="video/mp4" />
              </video>
              <Button
                variant="danger"
                className="mt-2"
                onClick={() => deleteVideo(video)}
              >
                Delete
              </Button>
            </Card.Body>
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default VideoList;
