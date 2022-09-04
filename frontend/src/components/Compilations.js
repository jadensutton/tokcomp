import React, { useState, useRef, useEffect } from 'react';
import { Modal, Button, Card, Form, Alert, Carousel } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import Header from './Header';
import axios from 'axios';

export default function Compilations() {
  const { currentUser } = useAuth();

  const newCompilationTitle = useRef();
  const editCompilationId = useRef();
  const editCompilationTitle = useRef();
  const editCompilationBackground = useRef();
  const videoShareURL = useRef();
  const newVideoPosition = useRef();
  const backgroundName = useRef();
  const backgroundFile = useRef();

  const [createCompilationError, setCreateCompilationError] = useState('');
  const [saveCompilationError, setSaveCompilationError] = useState('');
  const [addVideoError, setAddVideoError] = useState('');
  const [addBackgroundError, setAddBackgroundError] = useState('');
  const [loading, setLoading] = useState(false);
  const [compilations, setCompilations] = useState([]);
  const [noCompilationsMessage, setNoCompilationsMessage] = useState();
  const [showNewCompilationModal, setShowNewCompilationModal] = useState(false);
  const [showEditCompilationModal, setShowEditCompilationModal] =
    useState(false);
  const [showAddVideoModal, setShowAddVideoModal] = useState(false);
  const [showChangePositionModal, setShowChangePositionModal] = useState(false);
  const [showAddBackgroundModal, setShowAddBackgroundModal] = useState(false);

  const [videos, setVideos] = useState([]);
  const [noVideosMessage, setNoVideosMessage] = useState(
    'You have not added any videos.',
  );
  const [videoIndex, setVideoIndex] = useState(0);
  const [backgrounds, setBackgrounds] = useState([
    'Default TokComp Background',
    'None',
  ]);

  const handleVideoSelect = (selectedIndex, e) => {
    setVideoIndex(selectedIndex);
  };

  const arrayMove = (arr, old_index, new_index) => {
    if (new_index >= arr.length) {
      var k = new_index - arr.length + 1;
      while (k--) {
        arr.push(undefined);
      }
    }
    arr.splice(new_index, 0, arr.splice(old_index, 1)[0]);
    return arr;
  };

  const instance = axios.create({
    withCredentials: true,
  });

  useEffect(() => {
    instance
      .get(`compilations/${currentUser._id}`)
      .then((response) => {
        if (response.data.data.length > 0) {
          setCompilations(response.data.data);
          setNoCompilationsMessage('');
        } else {
          setNoCompilationsMessage(
            'You have not created any compilations yet.',
          );
        }
      })
      .catch((error) => {
        setNoCompilationsMessage(
          'Error pulling user compilations. Please try again later.',
        );
      });
  }, []);

  function deleteVideo(videoId) {
    setVideos(
      videos.filter(function (obj) {
        return obj.id != videoId;
      }),
    );
  }

  function handleChangeVideoPosition(e) {
    e.preventDefault();

    const newVideoIndex = newVideoPosition - 1;
    setVideos(arrayMove(videos, videoIndex, newVideoIndex));
    setShowChangePositionModal(false);
  }

  function handleAddVideo(e) {
    e.preventDefault();

    setLoading(true);
    setAddVideoError('');

    instance
      .get(`thumbnails/${encodeURIComponent(videoShareURL.current.value)}`)
      .then((response) => {
        setVideos((videos) => [
          ...videos,
          {
            share_url: videoShareURL.current.value,
            thumbnail: response.data,
          },
        ]);
        setShowAddVideoModal(false);
        setVideoIndex(videos.length);
      })
      .catch((error) => {
        if (error.response.status == 400) {
          setAddVideoError('Invalid URL');
        } else {
          setAddVideoError(
            'Encountered error while trying to find video. Please double check the URL.',
          );
        }
      });

    setLoading(false);
  }

  function handleEditCompilation(compilationId) {
    const editCompilation = compilations.filter(function (obj) {
      return obj._id === compilationId;
    })[0];
    editCompilationId.current = compilationId;
    editCompilationTitle.current = editCompilation.title;
    editCompilationBackground.current = editCompilation.background;
    setVideos(editCompilation.videos);
    setShowEditCompilationModal(true);
  }

  async function handleAddBackground(e) {
    e.preventDefault();

    setLoading(true);
    setAddBackgroundError('');

    const bodyFormData = new FormData();
    bodyFormData.append('name', backgroundName.current.value);
    bodyFormData.append('file', backgroundFile.current.files[0]);

    await instance
      .post(`backgrounds/${currentUser._id}`, bodyFormData, {
        headers: {
          'Content-type': 'multipart/form-data',
        },
      })
      .then((response) => {
        setShowNewCompilationModal(false);
      })
      .catch((error) => {
        console.log(error);
        setAddBackgroundError(
          'Unknown error encountered while trying to create compilation.',
        );
      });

    setLoading(false);
  }

  async function handleNewCompilation(e) {
    e.preventDefault();

    setCreateCompilationError('');

    await instance
      .post(`compilations/${currentUser._id}`, {
        title: newCompilationTitle.current.value,
      })
      .then((response) => {
        setCompilations((compilations) => [...compilations, response.data]);
        setShowNewCompilationModal(false);
      })
      .catch((error) => {
        setCreateCompilationError(
          'Unknown error encountered while trying to create compilation.',
        );
      });
  }

  async function handleSaveCompilation(e) {
    e.preventDefault();

    setLoading(true);

    await instance
      .patch(`compilations/${currentUser._id}/${editCompilationId.current}`, {
        title: editCompilationTitle.current.value,
        background: editCompilationBackground.current.value,
        videos: videos,
      })
      .then((response) => {
        const modifiedCompilationIndex = compilations.findIndex(
          (x) => x._id === editCompilationId.current,
        );
        const modifiedCompilation = compilations[modifiedCompilationIndex];
        modifiedCompilation.title = editCompilationTitle.current.value;
        modifiedCompilation.background =
          editCompilationBackground.current.value;
        modifiedCompilation.videos = videos;
        const newCompilations = [...compilations];
        newCompilations[modifiedCompilationIndex] = modifiedCompilation;

        setCompilations(newCompilations);
        setShowEditCompilationModal(false);
      })
      .catch((error) => {
        if (error.response.status == 400) {
          setSaveCompilationError('Invalid input. Please check your inputs.');
        } else {
          setSaveCompilationError(
            'Unknown error encountered while trying to save compilation.',
          );
        }
      });

    setLoading(false);
  }

  async function handleDeleteCompilation(compilationId) {
    await instance
      .delete(`compilations/${currentUser._id}/${compilationId}`)
      .then((response) => {
        setCompilations(
          compilations.filter(function (obj) {
            return obj._id !== compilationId;
          }),
        );
      });
  }

  return (
    <div
      className="w-100"
      style={{ minHeight: '100vh', backgroundColor: '#fffff' }}
    >
      <Header />

      <Modal
        show={showNewCompilationModal}
        onHide={() => setShowNewCompilationModal(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>New Compilation</Modal.Title>
        </Modal.Header>
        {createCompilationError && (
          <div className="w-100 d-flex align-items-center justify-content-center">
            <Alert variant="danger" style={{ width: '90%', marginTop: '5px' }}>
              {createCompilationError}
            </Alert>
          </div>
        )}
        <Modal.Body>
          <Form onSubmit={handleNewCompilation}>
            <Form.Group id="new-compilation-title">
              <Form.Label>Title</Form.Label>
              <Form.Control type="text" ref={newCompilationTitle} required />
            </Form.Group>

            <Button className="mt-4" variant="primary" type="submit">
              Create
            </Button>
          </Form>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>

      <Modal
        show={showChangePositionModal}
        onHide={() => setShowChangePositionModal(false)}
        size="small"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Change Video Position</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleChangeVideoPosition}>
            <Form.Group id="new-video-position">
              <Form.Label>New position</Form.Label>
              <Form.Control
                type="number"
                ref={newVideoPosition}
                min={1}
                max={videos.length}
                required
              />
            </Form.Group>

            <Button className="mt-4" variant="primary" type="submit">
              Move
            </Button>
          </Form>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>

      <Modal
        show={showAddBackgroundModal}
        onHide={() => setShowAddBackgroundModal(false)}
        size="small"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Add Background</Modal.Title>
        </Modal.Header>
        {addBackgroundError && (
          <div className="w-100 d-flex align-items-center justify-content-center">
            <Alert variant="danger" style={{ width: '90%', marginTop: '5px' }}>
              {addBackgroundError}
            </Alert>
          </div>
        )}
        <Modal.Body>
          <Form onSubmit={handleAddBackground}>
            <Form.Group id="add-background">
              <Form.Label>Name</Form.Label>
              <Form.Control type="text" ref={backgroundName} required />

              <Form.Label>Background image (1920 x 1080)</Form.Label>
              <Form.Control type="file" ref={backgroundFile} required />
            </Form.Group>

            <Button
              className="mt-4"
              variant="primary"
              type="submit"
              disabled={loading}
            >
              Upload
            </Button>
          </Form>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>

      <Modal
        show={showEditCompilationModal}
        onHide={() => setShowEditCompilationModal(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Edit Compilation</Modal.Title>
        </Modal.Header>
        {saveCompilationError && (
          <div className="w-100 d-flex align-items-center justify-content-center">
            <Alert variant="danger" style={{ width: '90%', marginTop: '5px' }}>
              {saveCompilationError}
            </Alert>
          </div>
        )}
        <Modal.Body>
          <Form onSubmit={handleSaveCompilation}>
            <Form.Group id="new-compilation-title">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                ref={editCompilationTitle}
                defaultValue={editCompilationTitle.current}
                required
              />
              <Form.Label>Background</Form.Label>
              <Button
                variant="primary"
                style={{
                  marginLeft: '5px',
                  paddingTop: '0px',
                  paddingBottom: '0px',
                  paddingLeft: '2px',
                  paddingRight: '2px',
                  fontSize: '13px',
                }}
                disabled={currentUser.plan === 'free'}
                onClick={() => setShowAddBackgroundModal(true)}
              >
                {currentUser.plan === 'free'
                  ? 'Premium feature'
                  : 'Add Background'}
              </Button>

              <Form.Select
                ref={editCompilationBackground}
                defaultValue={editCompilationBackground.current}
                disabled={currentUser.plan === 'free'}
                required
              >
                {backgrounds.map((background) => {
                  return <option>{background}</option>;
                })}
              </Form.Select>

              <Form.Label>Videos</Form.Label>
              <Button
                variant="primary"
                style={{
                  marginLeft: '5px',
                  paddingTop: '0px',
                  paddingBottom: '0px',
                  paddingLeft: '2px',
                  paddingRight: '2px',
                  fontSize: '13px',
                }}
                onClick={() => setShowAddVideoModal(true)}
              >
                Add TikTok
              </Button>

              {videos.length > 0 ? (
                <Carousel
                  activeIndex={videoIndex}
                  onSelect={handleVideoSelect}
                  interval={null}
                  variant="dark"
                  fade
                >
                  {videos.map((video) => {
                    return (
                      <Carousel.Item className="d-flex align-items-center justify-content-center">
                        <div className="w-50">
                          <img
                            className="d-block w-100"
                            src={video.thumbnail}
                            alt={video.id}
                          />
                        </div>
                        <Carousel.Caption>
                          <div>
                            <Button
                              variant="primary"
                              onClick={() => setShowChangePositionModal(true)}
                            >
                              Change position
                            </Button>
                          </div>
                          <div className="mt-1">
                            <Button
                              variant="danger"
                              onClick={() => deleteVideo(video.id)}
                            >
                              Delete
                            </Button>
                          </div>
                        </Carousel.Caption>
                      </Carousel.Item>
                    );
                  })}
                </Carousel>
              ) : (
                <p>{noVideosMessage}</p>
              )}
            </Form.Group>

            <Button
              className="mt-4"
              variant="primary"
              type="submit"
              disabled={loading}
            >
              Save
            </Button>
          </Form>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>

      <Modal
        show={showAddVideoModal}
        onHide={() => setShowAddVideoModal(false)}
        size="small"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Add TikTok</Modal.Title>
        </Modal.Header>
        {addVideoError && (
          <div className="w-100 d-flex align-items-center justify-content-center">
            <Alert variant="danger" style={{ width: '90%', marginTop: '5px' }}>
              {addVideoError}
            </Alert>
          </div>
        )}
        <Modal.Body>
          <Form onSubmit={handleAddVideo}>
            <Form.Group id="new-compilation-title">
              <Form.Label>Share URL</Form.Label>
              <Form.Control type="text" ref={videoShareURL} required />
            </Form.Group>

            <Button
              className="mt-4"
              variant="primary"
              type="submit"
              disabled={loading}
            >
              Add
            </Button>
          </Form>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>

      <div className="w-100 d-flex align-items-center justify-content-center">
        <div style={{ width: '90%', marginTop: '50px' }}>
          <h2 className="text-center mb-4">Compilations</h2>
          {compilations.length > 0 ? (
            <div
              className="w-100 align-items-center justify-content-left"
              style={{
                display: 'grid',
                gridAutoFlow: 'row',
                gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
                columnGap: '20px',
                rowGap: '20px',
              }}
            >
              {compilations.map((compilation) => {
                return (
                  <Card style={{ width: '350px' }}>
                    <Card.Header as="h5">{compilation.title}</Card.Header>
                    <Card.Body>
                      <Card.Text>Created: {compilation.created_at}</Card.Text>
                      <Card.Text>Modified: {compilation.modified_at}</Card.Text>
                      <Button
                        variant="primary"
                        style={{ marginRight: '5px' }}
                        onClick={() => handleEditCompilation(compilation._id)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => handleDeleteCompilation(compilation._id)}
                      >
                        Delete
                      </Button>
                    </Card.Body>
                  </Card>
                );
              })}
            </div>
          ) : (
            <div
              className="w-100 d-flex align-items-center justify-content-center"
              style={{ marginTop: '50px' }}
            >
              <h5>{noCompilationsMessage}</h5>
            </div>
          )}
        </div>
      </div>
      <div
        className="w-100 d-flex align-items-center justify-content-center"
        style={{ marginTop: '100px' }}
      >
        <Button
          variant="primary"
          onClick={() => setShowNewCompilationModal(true)}
          style={{ marginBottom: '100px' }}
        >
          Create Compilation
        </Button>
      </div>
    </div>
  );
}
