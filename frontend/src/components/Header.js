import React, { useState, useEffect } from 'react';
import './Header.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const [error, setError] = useState(null);
  const user =  JSON.parse(Cookies.get('user'));
  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;

  if (token) {
    decodedToken = jwt_decode(token);
    exp = decodedToken?.exp;
  }

  const date = exp ? new Date(exp * 1000) : null;
  const now = new Date();
  const [allowed, setAllowed] = useState(false);

  // Token expiration check
  useEffect(() => {
    if (!token || !decodedToken) {
      navigate('/login');
    } else if (date && date.getTime() < now.getTime()) {
      Cookies.remove('token');
      navigate('/login');
    } else {
      setAllowed(true);
    }
  }, [token, decodedToken, navigate, date]);



  // Handle dropdown toggle for user profile
  const toggleDropdown = () => {
    setDropdownOpen(!isDropdownOpen);
  };

  // Handle user logout
  const handleLogout = () => {
    Cookies.remove('token'); // Remove token cookie
    Cookies.remove('user');  // Remove user cookie
    navigate('/login'); // Redirect to login page
  };

  // Conditionally render based on user data availability
  if (!user) {
    return <div>Loading...</div>; // Show loading if user data is not fetched
  }

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-left">
          <a href="/" className="meta-logo">
            <img src="assets/images/logo.png" alt="logo" />
          </a>
          <div className="search-box">
            <img src="assets/images/search.png" alt="search" />
            <input type="text" placeholder="Search for anything" />
          </div>
        </div>
        <div className="navbar-center">
          <ul>
            <li>
              <a href="#" className="active-link">
                <img src="assets/images/home.png" alt="home" /> <span>Home</span>
              </a>
            </li>
            <li>
              <a href="#">
                <img src="assets/images/network.png" alt="network" /> <span>My Network</span>
              </a>
            </li>
            <li>
              <a href="#">
                <img src="assets/images/jobs.png" alt="jobs" /> <span>Jobs</span>
              </a>
            </li>
            <li>
              <a href="/Chat">
                <img src="assets/images/message.png" alt="message" /> <span>Messaging</span>
              </a>
            </li>
            <li>
              <a href="#">
                <img src="assets/images/notification.png" alt="notification" /> <span>Notifications</span>
              </a>
            </li>
          </ul>
        </div>
        <div className="navbar-right" id="nav-right">
          <div className="online">
            <img
              src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`}
              className="nav-profile-img"
              alt="profile"
              onClick={toggleDropdown}
            />
          </div>

          {isDropdownOpen && (
            <div className="drop-menu">
              <div className="dropdown-header">
                <img
                  src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`}
                  alt="Profile"
                  className="dropdown-avatar"
                />
                <div className="dropdown-info">
                  <div className="name">{user.name}</div>
                  <div className="desc">{"Professional footballer"}</div>
                </div>
              </div>
              <a href="/Profile" className="profile-btn">See your profile</a>
              <a href="#" className="logout-btn" onClick={handleLogout}>Logout</a>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
};

export default Header;
