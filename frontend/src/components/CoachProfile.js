import React, { useState, useEffect } from 'react';
import Header from './Header';
import { Tabs, Tab, Container} from '@mui/material';
import './Profile.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';

const CoachProfile = () => {
    const [message, setMessage] = useState('');
    const [profileImage, setProfileImage] = useState('');
    const [username, setUsername] = useState('');
    const [name, setName] = useState('');
    const [role, setRole] = useState('');
    const [email, setEmail] = useState('');
    const [nationality, setNationality] = useState('');
    const [dateOfAppointment, setDateOfAppointment] = useState('');
    const [dateOfEndContract, setDateOfEndContract] = useState('');
    const [yearsOfExperience, setYearsOfExperience] = useState('');
    const [qualification, setQualification] = useState('');
    const [availability, setAvailability] = useState(true);
    const [club_id, setClub_id] = useState('');
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
              setProfileImage(userData.profile_image);
              setUsername(userData.username);
              setName(userData.name);
              setEmail(userData.email);
              setRole(userData.role);
              setNationality(userData.nationality);
              setDateOfAppointment(userData.date_of_appointment);
              setDateOfEndContract(userData.date_of_end_contract);
              setYearsOfExperience(userData.years_of_experience);
              setQualification(userData.qualification);
              setAvailability(userData.availability);
              setClub_id(userData.club_id);
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
        const updatedProfile = {
        username,
        name,
        email,
        role,
        nationality,
        dateOfAppointment,
        dateOfEndContract,
        yearsOfExperience,
        qualification,
        availability,
        club_id,
        };

        const token = Cookies.get('token');
        if (!token) {
        setMessage('No token found. Please log in again.');
        // window.location.href = '/login';
        return;
        }
        console.log('Token:', token);

        try {
        const decodedToken = jwt_decode(token);
        const exp = decodedToken.exp; // Expiration time in seconds
        const now = Math.floor(Date.now() / 1000); // Current time in seconds

        if (exp < now) {
            setMessage('Session expired. Please log in again.');
            // window.location.href = '/login';
            return;
        }
        } catch (error) {
        setMessage('Invalid token. Please log in again.');
        // window.location.href = '/login';
        return;
        }
        
        // Debug: Log the updated profile before sending the request
        console.log('Updated Profile:', updatedProfile);


        try {
        const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile`, updatedProfile, {
            headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
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
            // window.location.href = '/login';
            } else {
            setMessage(`Error: ${error.response.data.message || 'Failed to update profile.'}`);
            }
        } else {
            setMessage('Network error. Please try again later.');
        }
        }
    };

  return (
    <div>
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
          <h2>Account Info</h2>
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
              <label>Nationality</label>
              <input
                type="text"
                className="form-control"
                value={nationality}
                onChange={(e) => setNationality(e.target.value)}
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

            <div className="form-group">
              <label>Date of Appointment</label>
              <input
                type="date"
                className="form-control"
                value={dateOfAppointment}
                onChange={(e) => setDateOfAppointment(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Date of End Contract</label>
              <input
                type="date"
                className="form-control"
                value={dateOfEndContract}
                onChange={(e) => setDateOfEndContract(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Years of Experience</label>
              <input
                type="number"
                className="form-control"
                value={yearsOfExperience}
                onChange={(e) => setYearsOfExperience(e.target.value)}
                placeholder="Enter years of experience"
              />
            </div>

            <div className="form-group">
              <label>Qualification</label>
              <input
                type="text"
                className="form-control"
                value={qualification}
                onChange={(e) => setQualification(e.target.value)}
                placeholder="Enter qualification"
              />
            </div>

            <div className="form-group">
              <label>Availability</label>
              <select
                className="form-control"
                value={availability}
                onChange={(e) => setAvailability(e.target.value === 'true')}
              >
                <option value="true">Available</option>
                <option value="false">Not Available</option>
              </select>
            </div>

            <button type="button" className="update-profile-btn" onClick={handleProfileUpdate}>
              Update Profile
            </button>
          </form>
          {message && <p className="text-info">{message}</p>}
        </div><div className="right-sidebar">
              <div className="sidebar-ad">
            <small>Ad </small>
            <p>Master Web Development</p>
            <div>
              <im src={`${process.env.REACT_APP_BASE_URL}/${profileImage}`} alt="user" />
              <img src="assets/images/mi-logo.png" alt="mi logo" />
            </div>
            <b>Brand and Demand in Xiaomi</b>
            <a href="#" className="ad-link">Learn More</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoachProfile;