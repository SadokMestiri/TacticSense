import React, { useState, useEffect } from 'react';
import Header from './Header';
import { Tabs, Tab, Container} from '@mui/material';
import './Profile.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';

const AgencyProfile = () => {
  const [profileImage, setProfileImage] = useState('');
  const [username, setUsername] = useState('');
  const [club_id, setClub_id] = useState({});
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [country, setCountry] = useState({});
  const [clubs, setClubs] = useState([]);

useEffect(() => {
  const fetchClubs = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_clubs`);
      setClubs(response.data);
      console.log('Clubs:', response.data);
    } catch (error) {
      console.error('Error fetching clubs:', error);
    }
  };

  fetchClubs();
}, []);

  useEffect(() => {
    const fetchUserData = async () => {
      const userCookie = Cookies.get('user');
      if (userCookie) {
        const parsedUser = JSON.parse(userCookie);
        const userId = parsedUser.id; // Assuming `id` is stored in the cookie

        try {
          const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${userId}`, {
            headers: {
              Authorization: `Bearer ${Cookies.get('token')}`, // Include the token for authentication
            },
          });

          const userData = response.data;

          // Update state with the fetched user data
          setClub_id(userData.club_id);
          setCountry(userData.country);
          setProfileImage(userData.profile_image);
          setUsername(userData.username);
          setName(userData.name);
          setEmail(userData.email);
          setRole(userData.role);
          console.log('User data:', userData);

        } catch (error) {
          console.error('Error fetching user data:', error);
          setMessage('Failed to fetch user data. Please try again.');
        }
      }
    };

    fetchUserData();
  }, []);

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('profile_image', file);

            const token = Cookies.get('token');
            if (!token) {
                setMessage('No token found. Please log in again.');
                return;
            }

            try {
                const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile`, formData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setProfileImage(response.data.profile_image);
                setMessage('Profile image updated successfully');
            } catch (error) {
                setMessage('Error updating profile image');
            }
        }
  };

  const handleProfileUpdate = async () => {
  const token = Cookies.get('token');
  if (!token) {
    setMessage('No token found. Please log in again.');
    return;
  }
  const updatedProfile = {
  username,
  name,
  email,
  role,
  country,
  club_id,
};

  try {
    const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile`, updatedProfile, {
      headers: {
        Authorization: `Bearer ${token}`,
        // 'Content-Type': 'multipart/form-data',
      },
    });

    if (response.status === 200) {
      setMessage('Profile updated successfully');
    } else {
      setMessage('Unexpected response from the server.');
    }
  } catch (error) {
    if (error.response) {
      if (error.response.status === 401) {
        setMessage('Unauthorized. Please log in again.');
      } else {
        setMessage(`Error: ${error.response.data.message || 'Failed to update profile.'}`);
      }
    } else {
      setMessage('Network error. Please try again later.');
    }
  }
};


  //export default MarketValuePredictor;

  return (
    <div>
      <Header />
      <div className="container">
        <div className="left-sidebar">
          <div className="sidebar-profile-box">
            <img src="assets/images/cover-pic.jpg" alt="cover" className="cover-image" />
            <div className="sidebar-profile-info">
              <div className="profile-image-wrapper">
                <img
                  src={`${process.env.REACT_APP_BASE_URL}/${profileImage}`}
                  alt="profile"
                  className="profile-image"
                />
                <label htmlFor="profile-image-upload" className="edit-icon">
                  <img
                    src="assets/images/edit-icon.png"
                    alt="edit"
                    className="edit-icon-image"
                  />
                </label>
                <input
                  type="file"
                  id="profile-image-upload"
                  style={{ display: 'none' }}
                  accept="image/*"
                  onChange={handleImageChange}
                />
              </div>
              <h1 className="profile-name">{name}</h1>
              <h3 className="profile-username">{username}</h3>
              <ul className="profile-stats">
                <li>
                  Profile views <span className="stat-value">10K</span>
                </li>
                <li>
                  Post views <span className="stat-value">50K</span>
                </li>
                <li>
                  Connections <span className="stat-value">5K</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className="main-content">
            <div>
                <h2>Account Info</h2>
                <div>
                <form>
                    <div className="form-group">
                    <label>Username</label>
                    <input
                        type="text"
                        className="form-control"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Enter new username"
                    />
                    </div>
                    <div className="form-group">
                    <label>Name</label>
                    <input
                        type="text"
                        className="form-control"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Enter full name"
                    />
                    </div>
                    <div className="form-group">
                    <label>Role</label>
                    <select
                        className="form-control"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                    >
                        <option value="Manager">Manager</option>
                        <option value="Scout">Scout</option>
                        <option value="Staff">Staff</option>
                        <option value="Agent">Agent</option>
                        <option value="Coach">Coach</option>
                        <option value="Player">Player</option>
                    </select>
                    </div>
                    <div className="form-group">
                    <label>Email</label>
                    <input
                        type="email"
                        className="form-control"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter email address"
                    />
                    </div>
                    <div className="form-group">
                    <a
                        href="/Reset"
                        className="reset-password-link"
                    >
                        Reset Password
                    </a>
                    </div>
                    <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>
                    
                    <h2>Details</h2>

                    <div className="form-group">
                    <label>Country</label>
                    <input
                        type="text"
                        className="form-control"
                        value={country || ''}
                        onChange={(e) => setCountry(e.target.value)}
                        placeholder="Enter nationality"
                    />
                    </div>

                    <div className="form-group">
                    <label>Club</label>
                    <select
                        className="form-control"
                        value={club_id || ''}
                        onChange={(e) => setClub_id(e.target.value)}
                    >
                        <option value="">Select a club</option>
                        {clubs.map((club) => (
                        <option key={club.id} value={club.id}>
                            {club.name}
                        </option>
                        ))}
                    </select>
                    </div>

                    <button type="button" className="update-profile-btn" onClick={handleProfileUpdate}>
                    Update Profile
                    </button>
                </form>
                {message && <p className="text-info">{message}</p>}
                </div>
            </div>
        </div>
        <div className="right-sidebar">
          <div className="sidebar-news">
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgencyProfile;