import React, { useState, useRef, useEffect } from 'react';

import { Container, Button, Navbar, Nav, Card, Alert } from 'react-bootstrap';
import { Modal } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

import 'antd/dist/antd.css';

export default function Settings() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const BASE_URL = 'https://ezcv.herokuapp.com/';

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [pageLoaded, setPageLoaded] = useState(false);

  const [currentPlan, setCurrentPlan] = useState('');
  const [nextDate, setNextDate] = useState('');
  const [cancelPlanAttempt, setCancelPlanAttempt] = useState(false);

  useEffect(() => {
    axios
      .get(BASE_URL + 'get_user_plan', {
        params: {
          user: currentUser.email,
        },
      })
      .then((response) => {
        setCurrentPlan(response.data.type);
        if (response.data.valid == true) {
          setNextDate(response.data.end);
        }
        setPageLoaded(true);
      })
      .catch((error) => {
        setError('Error retrieving user subscription plan.');
        setPageLoaded(true);
      });
  }, []);

  const openInNewTab = (url) => {
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
    if (newWindow) newWindow.opener = null;
  };

  const cancelSubscription = () => {
    setLoading(true);
    setError('');
    axios
      .post(BASE_URL + 'cancel_subscription', {
        user: currentUser.email,
      })
      .then((response) => {
        setSuccess(
          'Successfully cancelled subscription. Expiry date: ',
          response.data,
        );
      })
      .catch((error) => {
        setError('Internal server error. Please contact support.');
      });
    setLoading(false);
  };

  async function handleLogout() {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.log(err.message);
    }
  }

  async function handleAction(e) {
    e.preventDefault();

    setLoading(true);
    setError('');

    if (currentPlan == 'Free' || currentPlan == 'Cancelled Premium') {
      try {
        await axios
          .get(BASE_URL + 'get_checkout_url', {
            params: {
              user: currentUser.email,
            },
          })
          .then((response) => {
            openInNewTab(response.data);
          })
          .catch((error) => {
            setError(
              'Unknown error encountered, please try again later. If the error persists, please contact support.',
            );
          });
      } catch (err) {
        setError(
          'Unknown error encountered, please try again later. If the error persists, please contact support.',
        );
      }
    } else {
      setCancelPlanAttempt(true);
    }

    setLoading(false);
  }

  if (!pageLoaded) {
    return <div />;
  }

  return (
    <div
      className="w-100"
      style={{ minHeight: '100vh', backgroundColor: '#fffff' }}
    >
      <Navbar collapseOnSelect expand="lg" bg="primary" variant="dark">
        <Container>
          <Navbar.Brand href="#home">ezcv</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href="/new_resume">New Resume</Nav.Link>
              <Nav.Link href="/my_info">My Info</Nav.Link>
              <Nav.Link href="/settings">Settings</Nav.Link>
            </Nav>
            <Nav>
              <Button onClick={() => handleLogout()}>Log out</Button>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <div className="w-100 d-flex align-items-center justify-content-center">
        <div style={{ width: '60%', marginTop: '50px' }}>
          <h2 className="text-center mb-4">Settings</h2>
          <Card>
            <Card.Header as="h5">Account Information</Card.Header>
            <Card.Body>
              <Card.Text>Email: {currentUser.email}</Card.Text>
              <Card.Text>Current plan: {currentPlan}</Card.Text>
              <Card.Text>{nextDate}</Card.Text>
              <Button
                variant="primary"
                disabled={loading}
                onClick={(e) => handleAction(e)}
              >
                {currentPlan == 'Free' || currentPlan == 'Cancelled Premium'
                  ? 'Upgrade Plan'
                  : 'Cancel Subscription'}
              </Button>
            </Card.Body>
          </Card>
          <Modal
            title="Confirm"
            visible={cancelPlanAttempt}
            okText="Confirm"
            onCancel={() => {
              setCancelPlanAttempt(false);
            }}
            onOk={() => {
              cancelSubscription();
              setCancelPlanAttempt(false);
            }}
          >
            <p>Are you sure you want to cancel your subscription?</p>
          </Modal>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
        </div>
      </div>
    </div>
  );
}
