import React, { useState, useEffect, useContext } from "react";
import "./users.css";
import globals from "../../../globals"
import axios from 'axios';
import { useNavigate, useSearchParams, useParams} from "react-router-dom";
import { GlobalContext } from "../../../user"
import { ToastContainer, toast } from 'react-toastify';

// Function to get the CSRF token from cookies



const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

  // Fetch users (replace with your API URL if needed)
  const fetchUsers = async () => {
    
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
    try {
      setLoading(true);
      try {
        setLoading(true);
        const response = await axios.get("http://localhost:8000/api/web/users/",{
          headers: {
            "Content-Type": "application/json", // Set content type to JSON
            "X-CSRFToken": csrfToken, // Include CSRF token in the header
          },
          crossDomain: true, // Enable cross-domain requests
          withCredentials: true, // Ensure credentials (cookies) are sent with the request
        }).catch((err)=>{
          console.log(err)
        });
        setUsers(response.data.data.results); // Set the user data
        
      } catch (err) {
        setError("Error fetching data");
      } finally {
        setLoading(false);
      }
   

    
  }
  catch (err) {
    console.log(err)
    setError(err.message);
  
}
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  if (loading) {
    return <p>Loading users...</p>;
  }

  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }
  return (
    <>
      <div className="main">
      <ToastContainer />
       
        <div className="login-container">
        <div>
      <h1>User List</h1>
      {users.length === 0 ? (
        <p>No users found.</p>
      ) : (
        <table className="user-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.phone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
        </div>
      </div>
    </>
  );
};

export default Users;
