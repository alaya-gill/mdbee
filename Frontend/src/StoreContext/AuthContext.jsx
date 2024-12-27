import React, { createContext, useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [authData, setAuthData] = useState({
    email: "",
    password: "",
  });
  
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Simulated global state

  const login = () =>{ 
    setIsLoggedIn(true)
    localStorage.setItem('isLoggedIn', 'true'); // Persist login state
  };
  const logout = () => {
    setIsLoggedIn(false)
    localStorage.removeItem('isLoggedIn') // Persist login state
  };

  useEffect(() => {
    // Sync state with localStorage in case of direct reloads
    const storedState = localStorage.getItem('isLoggedIn') === 'true';
    if (storedState !== isLoggedIn) setIsLoggedIn(storedState);
  }, [isLoggedIn]);
  
  const updateAuthData = (name, value) => {
    setAuthData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <AuthContext.Provider value={{ authData, updateAuthData, isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
