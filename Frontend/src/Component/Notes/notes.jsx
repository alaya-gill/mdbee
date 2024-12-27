import React, { useState, useEffect, useContext } from "react";
import { FaEdit, FaTrash } from "react-icons/fa";
import "./notes.css";
import globals from "../../../globals"
import axios from 'axios';
import { useNavigate, useSearchParams, useParams, data} from "react-router-dom";
import { GlobalContext } from "../../../user"
import { ToastContainer, toast } from 'react-toastify';
import api from "../../api";
import { useAuth } from "../../StoreContext/AuthContext";
// Function to get the CSRF token from cookies



const Notes = () => {
  const [notes, setnotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [note, setNote] = useState({ title: "", description: "" });
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
  const [selectedNote, setSelectedNote] = useState(null); // Track the note being updated

const handleOpenUpdateModal = (note) => {
  setSelectedNote(note); // Set the note to be updated
  setIsUpdateModalOpen(true); // Open the modal
};

const handleCloseUpdateModal = () => {
  setSelectedNote(null); // Clear the selected note
  setIsUpdateModalOpen(false); // Close the modal
};

const handleUpdate = async () => {
  if (!selectedNote) return;

  const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies

  try {
    const response = await axios.put(
      `${globals.apiBaseUrl}api/web/notes/notes/${selectedNote.slug}/`,
      JSON.stringify({ title: selectedNote.title, description: selectedNote.description }),
      {
        headers: {
          'Content-Type': 'application/json', // Ensure the content type is set correctly
          'X-CSRFToken': csrfToken, // Include CSRF token
        },
        crossDomain: true,
        withCredentials: true, // Ensure credentials (cookies) are sent
      }
    );
    fetchnotes(); // Refresh the notes list
    toast.success('Note updated successfully!', { theme: 'light' });
    handleCloseUpdateModal();
  } catch (error) {
    console.error('Error updating note:', error);
    toast.error('Error while updating a Note!', { theme: 'light' });
  }
};


  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNote({ ...note, [name]: value });
  };

  const handleAddNote = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior
    setNote({ title: "", description: "" });
    setIsModalOpen(false);
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
    let temp = note
    temp['user'] = localStorage.getItem('user_id')
    const response = await axios.post(globals.apiBaseUrl +
      'api/web/notes/notes/', // Proxy to backend during development (config in vite.config.js)
      JSON.stringify(temp), // Send the data as JSON
      {
        headers: {
          'Content-Type': 'application/json', // Ensure the content type is set correctly
          'X-CSRFToken': csrfToken, // Include CSRF token
          },
        crossDomain: true,
        withCredentials: true, // Make sure credentials (cookies) are sent with the request
      }
      ).then((res)=>{
        fetchnotes()
      }).catch((error) => {
        toast.error("Error while adding a Note!",{
          theme: "light",
        });
      return;
        });
    }

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

  const onDelete = async (slug) => {
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
    
    const response = await axios.delete(globals.apiBaseUrl +
      'api/web/notes/notes/' + slug, 
      {
        headers: {
          'Content-Type': 'application/json', // Ensure the content type is set correctly
          'X-CSRFToken': csrfToken, // Include CSRF token
          },
        crossDomain: true,
        withCredentials: true, // Make sure credentials (cookies) are sent with the request
      }
      ).then((res)=>{
        fetchnotes()
      }).catch((error) => {
        toast.error("Error while deleting a Note!",{
          theme: "light",
        });
      return;
        });
    }

  const onUpdate = async (oldNote) => {
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
    setNote({ title: oldNote.title, description: oldNote.description });
    setIsUpdateModalOpen(false);
    const response = await axios.put(globals.apiBaseUrl +
      'api/web/notes/notes/' + oldNote.slug+ '/', 
      JSON.stringify(note),
      {
        headers: {
          'Content-Type': 'application/json', // Ensure the content type is set correctly
          'X-CSRFToken': csrfToken, // Include CSRF token
          },
        crossDomain: true,
        withCredentials: true, // Make sure credentials (cookies) are sent with the request
      }
      ).then((res)=>{
        fetchnotes()
      }).catch((error) => {
        toast.error("Error while updating a Note!",{
          theme: "light",
        });
      return;
        });
  }

  // Fetch notes (replace with your API URL if needed)
  const fetchnotes = async () => {
    
    const csrfToken = getCookie('csrftoken'); // Get CSRF token from cookies
    try {
      setLoading(true);
      try {
        setLoading(true);
        const response = await api.get("http://localhost:8000/api/web/notes/notes",{
          headers: {
            "Content-Type": "application/json", // Set content type to JSON
            "X-CSRFToken": csrfToken, // Include CSRF token in the header
          },
          crossDomain: true, // Enable cross-domain requests
          withCredentials: true, // Ensure credentials (cookies) are sent with the request
        }).catch((err)=>{
          toast.error("Error while fetching the notes!",{
            theme: "light",
          });
        });
        setnotes(response.data.data.results); // Set the user data
        
      } catch (err) {
        setError("Login to see notes data");
      } finally {
        setLoading(false);
      }
    
  }
  catch (err) {
    setError(err.message);
  
}
  };

  useEffect(() => {
    fetchnotes();
  }, []);

  if (loading) {
    return <p>Loading notes...</p>;
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
        <div className="notes-header">
  <h1 className="notes-title">Notes</h1>
  <button className="add-note-button"
    onClick={() => setIsModalOpen(true)}>Add Note</button>
  
</div>
  {notes.length === 0 ? (
    <p>No notes found.</p>
  ) : (
    <table className="user-table">
  <thead>
    <tr>
      <th>Title</th>
      <th>Description</th>
      <th>Actions</th> {/* New column for actions */}
    </tr>
  </thead>
  <tbody>
    {notes.map((note) => (
      <tr key={note.id}>
        <td>{note.title}</td>
        <td>{note.description}</td>
        <td>
        <FaEdit
          className="icon edit-icon"
          onClick={() => handleOpenUpdateModal(note)}
          title="Update"
        />
          <FaTrash
            className="icon delete-icon"
            onClick={() => onDelete(note.slug)}
            title="Delete"
          />
        </td>
      </tr>
    ))}
  </tbody>
</table>

  )}
</div>

        </div>
        {isUpdateModalOpen && selectedNote && (
  <div className="modal">
    <div className="modal-content">
      <h2>Update Note</h2>
      <form onSubmit={(e) => e.preventDefault()}>
        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            value={selectedNote.title}
            onChange={(e) =>
              setSelectedNote({ ...selectedNote, title: e.target.value })
            }
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={selectedNote.description}
            onChange={(e) =>
              setSelectedNote({ ...selectedNote, description: e.target.value })
            }
            required
          />
        </div>
        <div className="modal-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={handleCloseUpdateModal}
          >
            Cancel
          </button>
          <button type="button" className="save-button" onClick={handleUpdate}>
            Save
          </button>
        </div>
      </form>
    </div>
  </div>
)}

        {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Add Note</h2>
            <form>
              <div className="form-group">
                <label htmlFor="title">Title</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={note.title}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  name="description"
                  value={note.description}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-button"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="save-button"
                  onClick={handleAddNote}
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      </div>
      
      
    </>
  );
};

export default Notes;
