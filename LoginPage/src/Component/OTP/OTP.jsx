import React, { useState, useEffect, useContext } from "react";
import "./otp.css";
import { useLocation } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import globals from "../../../globals"
import { ToastContainer, toast } from 'react-toastify';


// Function to get the CSRF token from cookies

const OTPScreen = () => {
    const navigate = useNavigate();
    const [otp, setOtp] = useState(new Array(6).fill("")); // State for 6 digits
    const [rememberMe, setRememberMe] = useState(false); // State for "Remember Me"
    const location = useLocation();
    const { userData } = location.state || {};
    console.log(userData)

    // Handle individual digit changes
    const handleChange = (value, index) => {
        if (/^\d$/.test(value) || value === "") { // Allow only digits or empty value
            const newOtp = [...otp];
            newOtp[index] = value;
            setOtp(newOtp);

            // Automatically focus the next input field if a digit is entered
            if (value !== "" && index < 5) {
                document.getElementById(`otp-input-${index + 1}`).focus();
            }
        }
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
        const otpValue = otp.join(""); // Combine digits into a single OTP string

        if (otpValue.length !== 6) {
            alert("Please enter a valid 6-digit OTP");
            return;
        }

        // Clear OTP after submission
        setOtp(new Array(6).fill(""));
        const response = await axios.post(globals.apiBaseUrl +
            'api/token', // Proxy to backend during development (config in vite.config.js)
            JSON.stringify({ code_token: userData.codeToken, code: otpValue, remember_flag: true}), // Send the data as JSON
            {
                headers: {
                    'Content-Type': 'application/json', // Ensure the content type is set correctly
                    'X-CSRFToken': csrfToken, // Include CSRF token
                },
                crossDomain: true,
                withCredentials: true,
                // Make sure credentials (cookies) are sent with the request
            }

        ).then((response) => {
            console.log(response.status)
            toast.error("Error while logging in", {
                theme: "light",
            });


            navigate('/')
        }).catch((error)=>{
            toast.error("Error while logging in", {
                theme: "light",
            });
            return;
        });

    }
    return (
        <>
            <div className="main">
                  <ToastContainer />
                <div className="left-content">
                    <h1>Enter Your OTP</h1>
                    <p className="lf-p1">OTP sent to email: {userData?.email}</p>
                </div>
                <div className="login-container">
                    <form
                        className="login-form"
                        onSubmit={onSubmitHandler}
                    >
                        <h2>OTP</h2>
                        <div className="form-group">
                            <label htmlFor="otp">OTP</label>
                            {otp.map((digit, index) => (
                                <input
                                    key={index}
                                    id={`otp-input-${index}`}
                                    type="number"
                                    value={digit}
                                    onChange={(e) => handleChange(e.target.value, index)}
                                    maxLength={1}
                                    style={styles.otpInput}
                                />
                            ))}
                        </div>
                        <div style={styles.checkboxGroup}>
                            <input
                                type="checkbox"
                                id="rememberMe"
                                checked={rememberMe}
                                onChange={(e) => setRememberMe(e.target.checked)}
                            />
                            <label htmlFor="rememberMe" style={styles.label}>Remember Me</label>
                        </div>
                        <button type="submit" style={styles.button}>
                            Submit
                        </button>
                    </form>
                </div>

            </div>
        </>
    );
};

const styles = {
    otpContainer: {
        display: "flex",
        justifyContent: "center",
        marginBottom: "20px",
    },
    otpInput: {
        width: "40px",
        height: "40px",
        margin: "0 5px",
        fontSize: "18px",
        textAlign: "center",
        border: "1px solid #ccc",
        borderRadius: "4px",
    },
    checkboxGroup: {
        display: "flex",
        alignItems: "center",
        marginBottom: "20px",
        marginRight: "5px"
    },
    button: {
        padding: "10px 20px",
        backgroundColor: "#007bff",
        color: "#fff",
        border: "none",
        cursor: "pointer",
        fontSize: "16px",
        borderRadius: "4px",
    },
    label: {
        marginLeft: "5px"
    }
}
export default OTPScreen;
