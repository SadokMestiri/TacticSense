import React, { useState, useEffect } from 'react';
import './Header.css';
import axios from 'axios';

const Header = () => {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const user_id = localStorage.getItem('user_id');
  const [error, setError] = useState(null);
  const [user, setUser] = useState({});

  const toggleDropdown = () => {
    console.log('toggleDropdown invoked');
    setDropdownOpen(!isDropdownOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('user_id');
    // Redirect to login or home page once logged out
    window.location.href = '/login';
  };

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${user_id}`);
      setUser(response.data);
    } catch (error) {
      setError(error.response?.data?.message || 'Error fetching user data');
    }
  };

  useEffect(() => {
    fetchUser();
  }, [user_id]);

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
              <a href="/players">
                <img src="assets/images/network.png" alt="network" /> <span>Players</span>
              </a>
            </li>
            <li>
              <a href="#">
                <img src="assets/images/jobs.png" alt="jobs" /> <span>Jobs</span>
              </a>
            </li>
            <li>
              <a href="/gpt">
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
              <a href="#" className="profile-btn">See your profile</a>
              <a href="#" className="logout-btn" onClick={handleLogout}>Logout</a>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
};

export default Header;