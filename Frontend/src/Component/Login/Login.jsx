import React, { useState, useEffect, useContext } from "react";
import "./login.css";
import globals from "../../../globals"
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { GlobalContext } from "../../../user"
import { ToastContainer, toast } from 'react-toastify';
import { useAuth } from '../../StoreContext/AuthContext';

// Function to get the CSRF token from cookies



const Login = () => {
  const navigate = useNavigate();
  const [data, setData] = useState({
    email: "",
    password: "",
  });
  const [userData, setUserData] = useState();
  const { isLoggedIn, login, logout } = useAuth();

  
  // Corrected onChangeHandler
  const onChangeHandler = (event) => {
    const name = event.target.name; // Correctly get the 'name' attribute
    const value = event.target.value; // Get the 'value'

    setData((prevData) => ({
      ...prevData,
      [name]: value, // Dynamically update the correct field
    }));
  };

  const getCsrfToken = () => {
    const cookieValue = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];
    return cookieValue || "";
  };
  

  useEffect(() => {
  }, [data]);

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };
  
  // Handle form submission
  const onSubmitHandler = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior
  
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
  
      const response = await axios.post(globals.apiBaseUrl +
        'api/code-token', // Proxy to backend during development (config in vite.config.js)
        JSON.stringify(data), // Send the data as JSON
        {
          headers: {
            'Content-Type': 'application/json', // Ensure the content type is set correctly
            'X-CSRFToken': csrfToken, // Include CSRF token
            },
          crossDomain: true,
          withCredentials: true, // Make sure credentials (cookies) are sent with the request
        }
      ).catch((error) => {
        toast.error("Incorrect email or password!",{
          theme: "light",
        });
        return;
      });
      if (response.data.is_authenticated) {
        localStorage.setItem('user_id', response.data.user.id)
        login();
        navigate('/users');
        return;
      }
      let resData = await response.data.user
      resData['codeToken'] = await response.data.token
      navigate("/otp", { state: { userData: resData }});
    }
  return (
    <>
      <div className="main">
      <ToastContainer />
        <div className="left-content">
          <h1>Login Now</h1>
          <p>Start Seamless Your AI</p>
          <p className="lf-p1">Dental Scibe</p>
        </div>
        <div className="login-container">
          <form
            className="login-form"
            onSubmit={onSubmitHandler}
          >
            <h2>Login</h2>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                onChange={onChangeHandler}
                value={data.email}
                type="email"
                id="email"
                name="email" // Added name attribute
                placeholder="Enter your email"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                onChange={onChangeHandler}
                value={data.password}
                type="password"
                id="password"
                name="password" // Added name attribute
                placeholder="Enter your password"
                required
              />
            </div>
            <button type="submit" className="login-button">
              Login
            </button>
            <p className="signup-text">
              Don't have an account? <a href="/signup">Sign up</a>
            </p>
          </form>
        </div>
      </div>
    </>
  );
};

export default Login;
