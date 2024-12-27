import React, { useState, useEffect, useContext } from "react";
import "./set-password.css";
import globals from "../../../globals"
import axios from 'axios';
import { useNavigate, useSearchParams, useParams} from "react-router-dom";
import { GlobalContext } from "../../../user"
import { ToastContainer, toast } from 'react-toastify';

// Function to get the CSRF token from cookies



const SetPassword = () => {
  const navigate = useNavigate();
  const { uid, token } = useParams();
  const [userData, setUserData] = useState();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const isValidPassword = (password) => {
    // Minimum 8 characters, includes letters, numbers, and special characters
    return /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&.]{8,}$/.test(password);
  };
  
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
  

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };
  
  // Handle form submission
  const onSubmitHandler = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior
  
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
      setError(""); // Clear previous errors
      setSuccess(""); // Clear previous success messages

      if (!isValidPassword(newPassword)) {
        setError(
          "Password must be at least 8 characters long and include letters, numbers, and special characters."
        );
        return;
      }
  
      if (newPassword !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
  
      setSuccess("Password successfully updated!");
      let tempData = {};
      tempData['uid'] = uid
      tempData['token'] = token
      tempData['new_password'] = newPassword
      tempData['re_new_password'] = confirmPassword
      const response = await axios.post(globals.apiBaseUrl +
        'api/web/users/reset_password_confirm/', // Proxy to backend during development (config in vite.config.js)
        JSON.stringify(tempData), // Send the data as JSON
        {
          headers: {
            'Content-Type': 'application/json', // Ensure the content type is set correctly
            'X-CSRFToken': csrfToken, // Include CSRF token
            },
          crossDomain: true,
          withCredentials: true, // Make sure credentials (cookies) are sent with the request
        }
      ).catch((error) => {
        toast.error("Error while setting password!",{
          theme: "light",
        });
        return;
      });
      if (response.status){
        navigate('/');
        return;
      }
    }
  return (
    <>
      <div className="main">
      <ToastContainer />
        <div className="left-content">
          <h1>Set Password</h1>
          <p>Start Seamless Your AI</p>
          <p className="lf-p1">Dental Scibe</p>
        </div>
        <div className="login-container">
          <form
            className="login-form"
            onSubmit={onSubmitHandler}
          >
            <h2>Set Password</h2>
            <div className="form-group">
              <label htmlFor="newPassword">Password</label>
              <input
                type="password"
                id="newPassword"
                name="newPassword" // Added name attribute
                placeholder="Enter your password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword" // Added name attribute
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="login-button">
              Submit
            </button>
          </form>
          {error && <p style={{ color: "red" }}>{error}</p>}
          {success && <p style={{ color: "green" }}>{success}</p>}
        </div>
      </div>
    </>
  );
};

export default SetPassword;
