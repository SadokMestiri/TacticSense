import React, { useState, useEffect } from 'react';
import Header from './Header';
import { Tabs, Tab, Container} from '@mui/material';
import './Profile.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';

const CoachProfileView = () => {
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
              </div>
              <h1 className="profile-name">{name || 'N/A'}</h1>
              <h3 className="profile-username">{username || 'N/A'}</h3>
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
          <div className="info-section">
            <div className="info-item">
              <label>Username:</label>
              <span className="info-value">{username || 'N/A'}</span>
            </div>
            <div className="info-item">
              <label>Name:</label>
              <span className="info-value">{name || 'N/A'}</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span className="info-value">{email || 'N/A'}</span>
            </div>
            <div className="info-item">
              <label>Role:</label>
              <span className="info-value">{role || 'N/A'}</span>
            </div>
          </div>
          <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>
          <h2>Details</h2>
          <div className="details-section">
            <div className="details-item">
              <label>Nationality:</label>
              <span className="details-value">{nationality || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Club:</label>
              <span>
                {clubs.find((club) => club.id === club_id)?.name || 'No club selected'}
              </span>
            </div>
            <div className="details-item">
              <label>Date of Appointment:</label>
              <span className="details-value">{dateOfAppointment || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Date of End Contract:</label>
              <span className="details-value">{dateOfEndContract || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Years of Experience:</label>
              <span className="details-value">{yearsOfExperience || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Qualification:</label>
              <span className="details-value">{qualification || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Availability:</label>
              <span className="details-value">{availability ? 'Available' : 'Not Available'}</span>
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
export default CoachProfileView;
