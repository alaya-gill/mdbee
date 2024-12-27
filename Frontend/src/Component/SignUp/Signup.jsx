import React, { useState } from "react";
import "./signup.css";
import globals from "../../../globals"
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { GlobalContext } from "../../../user"
import { ToastContainer, toast } from 'react-toastify';

const SignUp = () => {
  const [data, setData] = useState({
    email: "",
    first_name: "",
    last_name: "",
    address: "",
    city: "",
    country: "",
    state: "",
    phone: "",
    company: "",
    zipcode: "",
    is_superuser: false,
  });

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

  // Corrected onChangeHandler
  const onChangeHandler = (event) => {
    const { name, value } = event.target; // Destructure event.target
    setData((prevData) => ({
      ...prevData,
      [name]: value, // Dynamically update the correct field
    }));
  };

  // Form submission handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
    const response = await axios.post(globals.apiBaseUrl +
      'api/web/users/create_system_user/', // Proxy to backend during development (config in vite.config.js)
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
    
      
  };

  

  return (
    <div className="main">
      <div className="left-content">
        <h1>Sign up</h1>
        <p>Create your account</p>
        <p className="lf-p1">Dental Scribe</p>
      </div>
      <div className="login-container">
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="place-order-left">
            <p>Create an Account</p>
            <div className="multi-fields">
              <input
                name="first_name"
                onChange={onChangeHandler}
                type="text"
                placeholder="Enter your first name"
                value={data.first_name}
              />
              <input
                name="last_name"
                onChange={onChangeHandler}
                type="text"
                placeholder="Enter your last name"
                value={data.last_name}
              />
            </div>
            <div className="single-field">
              <input
                name="email"
                onChange={onChangeHandler}
                type="email"
                placeholder="Enter your email address"
                value={data.email}
              />
              <input
                name="address"
                onChange={onChangeHandler}
                type="text"
                placeholder="Address"
                value={data.address}
              />
            </div>
            <div className="multi-fields">
              <input
                name="city"
                onChange={onChangeHandler}
                type="text"
                placeholder="City"
                value={data.city}
              />
              <input
                name="state"
                onChange={onChangeHandler}
                type="text"
                placeholder="State"
                value={data.state}
              />
            </div>
            <div className="multi-fields">
              <input
                name="zipcode"
                onChange={onChangeHandler}
                type="text"
                placeholder="Zip Code"
                value={data.zipcode}
              />
              <input
                name="country"
                onChange={onChangeHandler}
                type="text"
                placeholder="Country"
                value={data.country}
              />
            </div>
            <input
              name="phone"
              onChange={onChangeHandler}
              type="tel"
              placeholder="Phone"
              value={data.phone}
            />
          </div>
          <button type="submit" className="login-button">
            Submit
          </button>
          <p className="signup-text">
              Already have an account? <a href="/">Login</a>
            </p>
        </form>
      </div>
    </div>
  );
};

export default SignUp;
