import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Button, Row, Col, Modal, ProgressBar, Alert, Spinner } from 'react-bootstrap';

interface VideoListProps {
  apiUrl: string;
  videos: { uploaded: string[]; processed: string[] };
  onDelete: () => void;
  onError: (msg: string) => void;
}

const VideoList: React.FC<VideoListProps> = ({ apiUrl, videos, onDelete, onError }) => {
  const [selectedMetadata, setSelectedMetadata] = useState<any | null>(null);
  const [showMetadata, setShowMetadata] = useState(false);
  const [progressStatuses, setProgressStatuses] = useState<{ [filename: string]: number }>({});
  const [completedJobs, setCompletedJobs] = useState<{ [filename: string]: boolean }>({});
  const [processedVideos, setProcessedVideos] = useState<string[]>(videos.processed);
  const [loadingProcessed, setLoadingProcessed] = useState(false);

  // Fetch the latest list of processed videos
  const fetchProcessedVideos = async () => {
    try {
      const response = await axios.get<{ processed: string[] }>(`${apiUrl}/videos`);
      setProcessedVideos(response.data.processed);
    } catch {
      onError('Failed to fetch processed videos.');
    }
  };

  // Poll AI Job Progress
  useEffect(() => {
    const interval = setInterval(() => {
      videos.uploaded.forEach(async (filename) => {
        try {
          const response = await axios.get<{ status: string, progress: number }>(
            `${apiUrl}/videos/job-progress/${filename}`
          );
          const { status, progress } = response.data;

          setProgressStatuses((prev) => ({
            ...prev,
            [filename]: progress,
          }));

          if (status === 'completed' && progress === 100 && !completedJobs[filename]) {
            setCompletedJobs((prev) => ({ ...prev, [filename]: true }));
            setLoadingProcessed(true);
            await fetchProcessedVideos(); // Refresh the processed list
            setLoadingProcessed(false);
            onDelete(); // Trigger parent to refresh lists if needed
          }
        } catch {
          onError('Failed to fetch job progress.');
        }
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [videos.uploaded, apiUrl, onError, onDelete, completedJobs]);

  const deleteVideo = async (folder: string, filename: string) => {
    try {
      await axios.delete(`${apiUrl}/videos/${folder}/${filename}`);
      await onDelete();
      await fetchProcessedVideos();
    } catch {
      onError('Failed to delete video.');
    }
  };

  const fetchMetadata = async (filename: string) => {
    try {
      const response = await axios.get(`${apiUrl}/videos/metadata/${filename}.json`);
      setSelectedMetadata(response.data);
      setShowMetadata(true);
    } catch {
      onError('Failed to fetch metadata.');
    }
  };

  const renderProgressBar = (filename: string) => {
    const progress = progressStatuses[filename] || 0;

    if (progress === 100) {
      return (
        <Alert variant="success" className="mt-2 p-1 text-center">
          AI Job Completed 🎉
        </Alert>
      );
    }

    return (
      <div className="mt-2">
        <small>AI Job in progress...</small>
        <ProgressBar now={progress} label={`${progress}%`} />
      </div>
    );
  };

  const renderVideoCard = (folder: string, filename: string, isProcessed = false) => (
    <Col key={filename} md={6} lg={4} className="mb-4">
      <Card>
        <Card.Body>
          <Card.Title>{filename}</Card.Title>

          <video width="100%" controls>
            <source src={`${apiUrl}/videos/${folder}/${filename}?t=${new Date().getTime()}`} type="video/mp4" />
          </video>

          <div className="mt-2">
            {isProcessed && (
              <Button variant="info" size="sm" className="me-2" onClick={() => fetchMetadata(filename)}>
                View Metadata
              </Button>
            )}
            <Button variant="danger" size="sm" onClick={() => deleteVideo(folder, filename)}>
              Delete
            </Button>
          </div>

          {folder === 'uploaded' && renderProgressBar(filename)}
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
        {loadingProcessed ? (
          <Spinner animation="border" role="status" className="m-auto mt-4">
            <span className="visually-hidden">Loading Processed Videos...</span>
          </Spinner>
        ) : processedVideos.length > 0 ? (
          processedVideos.map((video) => renderVideoCard('processed', video, true))
        ) : (
          <p>No processed videos.</p>
        )}
      </Row>

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
