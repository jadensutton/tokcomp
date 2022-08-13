import React, { useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = React.createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState();
  const [loading, setLoading] = useState(true);

  const instance = axios.create({
    withCredentials: true,
  });

  async function signup(email, password) {
    await instance
      .post('user/signup', {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': true,
        },
        email: email,
        password: password,
      })
      .then((response) => {
        return response;
      })
      .catch((error) => {
        throw error.response.data.error;
      });
  }

  async function login(email, password) {
    await instance
      .post('user/login', {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': true,
        },
        email: email,
        password: password,
      })
      .then((response) => {
        return response;
      })
      .catch((error) => {
        throw error.response.data.error;
      });
  }

  function logout() {
    instance
      .get('user/logout')
      .then((response) => {
        return response;
      })
      .catch((error) => {
        throw error.response.data.error;
      });
  }

  useEffect(() => {
    (async () => {
      await instance
        .get('user/me', {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': true,
          },
        })
        .then((response) => {
          setCurrentUser(response.data);
          setLoading(false);
        })
        .catch((error) => {
          setCurrentUser(null);
          setLoading(false);
        });
    })();
  }, []);

  const value = {
    currentUser,
    signup,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
