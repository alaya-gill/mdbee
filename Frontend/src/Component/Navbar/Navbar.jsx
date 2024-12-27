import React, { useEffect } from "react";
import "./navbar.css";
import img from "../../images/logo.png";
import globals from "../../../globals"
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from 'react-toastify';
import { useAuth } from '../../StoreContext/AuthContext';

const Navbar = () => {
  const navigate = useNavigate();
  const { isLoggedIn, login, logout } = useAuth();

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

  const handleLogout = async (e) => { 
    e.preventDefault(); // Prevent default form submission behavior
  
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
    const response = await axios.post(globals.apiBaseUrl +
      'api/web/users/logout/', // Proxy to backend during development (config in vite.config.js)
      JSON.stringify({}), // Send the data as JSON
      {
        headers: {
          'Content-Type': 'application/json', // Ensure the content type is set correctly
          'X-CSRFToken': csrfToken, // Include CSRF token
        },
        crossDomain: true,
        withCredentials: true, // Make sure credentials (cookies) are sent with the request
      }
    ).then((res)=>{
      toast.error("User logged out!",{
        theme: "light",
      });
      localStorage.removeItem('user_id')
      logout();
      navigate('/')
    }).catch((error) => {
      toast.error("Error logging out!",{
        theme: "light",
      });
      return;
    });
  };
  return (
    <>
    <div className="navbar">
      <img className="img" src={img} alt="" />
      {isLoggedIn && (
        <div className="button-group">
          <button className="logout-button">
            <a href="/notes">Notes</a>
          </button>
          <button className="logout-button">
            <a href="/users">Users</a>
          </button>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      )}
    </div>
  </>
  
  );

};

export default Navbar;
