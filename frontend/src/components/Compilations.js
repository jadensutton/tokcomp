import React, { useState, useRef, useEffect } from 'react';
import { Modal, Button, Card, Form, Alert } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import Header from './Header';
import axios from 'axios';

import 'antd/dist/antd.css';

export default function Compilations() {
  const { currentUser, logout } = useAuth();

  const newCompilationTitle = useRef();

  const [error, setError] = useState('');
  const [compilations, setCompilations] = useState([]);
  const [noCompilationsMessage, setNoCompilationsMessage] = useState();
  const [showNewCompilationModal, setShowNewCompilationModal] = useState(false);

  const instance = axios.create({
    withCredentials: true,
  });

  useEffect(() => {
    instance
      .get(`compilations/${currentUser._id}`)
      .then((response) => {
        setCompilations(response.data.data);
        setNoCompilationsMessage('');
      })
      .catch((error) => {
        setNoCompilationsMessage(
          'Error pulling user compilations. Please try again later.',
        );
      });
  }, []);

  async function handleNewCompilation(e) {
    e.preventDefault();

    await instance
      .post(`compilations/${currentUser._id}`, {
        title: newCompilationTitle.current.value,
      })
      .then((response) => {
        setCompilations((compilations) => [...compilations, response.data]);
        setShowNewCompilationModal(false);
      })
      .catch((error) => {
        setError(
          'Unknown error encountered while trying to create compilation.',
        );
      });
  }

  async function handleDeleteCompilation(compilation_id) {
    await instance
      .delete(`compilations/${currentUser._id}/${compilation_id}`)
      .then((response) => {
        setCompilations(
          compilations.filter(function (obj) {
            return obj._id !== compilation_id;
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
          <Modal.Title>New Backtest</Modal.Title>
        </Modal.Header>
        {error && (
          <div className="w-100 d-flex align-items-center justify-content-center">
            <Alert variant="danger" style={{ width: '90%', marginTop: '5px' }}>
              {error}
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

      <div className="w-100 d-flex align-items-center justify-content-center">
        <div style={{ width: '90%', marginTop: '50px' }}>
          <h2 className="text-center mb-4">Compilations</h2>
          {compilations.length > 0 ? (
            <div
              className="w-100 align-items-center justify-content-left"
              style={{
                display: 'grid',
                gridAutoFlow: 'row',
                gridTemplateColumns: '1fr 1fr 1fr 1fr',
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
                      <Button variant="primary" style={{ marginRight: '5px' }}>
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
