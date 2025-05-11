import React from 'react';
import Header from './Header';
import './Profile.css';

const ManagerProfileView = ({
  profileImage,
  username,
  name,
  role,
  email,
  nationality,
  dateOfAppointment,
  dateOfEndContract,
  yearsOfExperience,
  qualification,
  availability,
  matches,
  wins,
  losses,
  draws,
  ppg
}) => {
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
            <div className="details-item">
              <label>Matches:</label>
              <span className="details-value">{matches || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Wins:</label>
              <span className="details-value">{wins || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Losses:</label>
              <span className="details-value">{losses || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Draws:</label>
              <span className="details-value">{draws || 'N/A'}</span>
            </div>
            <div className="details-item">
              <label>Points Per Game:</label>
              <span className="details-value">{ppg || 'N/A'}</span>
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

export default ManagerProfileView;
