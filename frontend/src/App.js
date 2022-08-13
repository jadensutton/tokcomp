import React from 'react';

import PrivateRoute from './components/PrivateRoute';
import Signup from './components/Signup';
import Login from './components/Login';
import Compilations from './components/Compilations';
import Exports from './components/Exports';
import Settings from './components/Settings';

import { Container } from 'react-bootstrap';
import { AuthProvider } from './contexts/AuthContext';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import 'antd/dist/antd.css';

function App() {
  return (
    <div
      className="d-flex align-items-center justify-content-center"
      style={{ minHeight: '100vh' }}
    >
      <div className="w-100 d-flex align-items-center justify-content-center">
        <Router>
          <AuthProvider>
            <Routes>
              <Route exact path="/" element={<PrivateRoute />}>
                <Route exact path="/compilations" element={<Compilations />} />
                <Route exact path="/exports" element={<Exports />} />
                <Route exact path="/settings" element={<Settings />} />
              </Route>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
            </Routes>
          </AuthProvider>
        </Router>
      </div>
    </div>
  );
}

export default App;
