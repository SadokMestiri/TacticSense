import React, { useState, useEffect } from 'react';
import './Header.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate, NavLink } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const [error, setError] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [playerId, setPlayerId] = useState(null);
  const user =  JSON.parse(Cookies.get('user'));
  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;
  const user_id = user.id;
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
      navigate('/');
    } else if (date && date.getTime() < now.getTime()) {
      Cookies.remove('token');
      navigate('/');
    } else {
      setAllowed(true);
    }
  }, [token, decodedToken, navigate, date]);
  

  useEffect(() => {
    const fetchPlayerId = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/player_id/${user_id}`);
        setPlayerId(response.data.player_id);
      } catch (error) {
        console.error("Erreur lors de la récupération du player ID:", error);
      }
    };

    if (user_id) {
      fetchPlayerId();
    }
  }, [user_id]);

  useEffect(() => {
        const fetchNotifications = async () => {
            if (!playerId) return;
            try {
                const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/notifications/${playerId}`);
                console.log("Notifications reçues:", response.data);
                setNotifications(response.data);
            } catch (error) {
                console.error("Error fetching notifications:", error);
            }
        };

        if (playerId) {
            console.log("Fetching notifications for player ID:", playerId);
            fetchNotifications();
        }
    }, [playerId]);

  // Handle dropdown toggle for user profile
  const toggleDropdown = () => {
    setDropdownOpen(!isDropdownOpen);
  };

  // Handle user logout
  const handleLogout = () => {
    Cookies.remove('token');
    Cookies.remove('user');
    navigate('/');  // Navigate to login page after logout
};

  // Conditionally render based on user data availability
  if (!user) {
    return <div>Loading...</div>; // Show loading if user data is not fetched
  }



  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-left">
          <NavLink to="/Home" className="meta-logo">
            <img src="assets/images/logo.png" alt="logo" />
          </NavLink>
          <div className="search-box">
            <img src="assets/images/search.png" alt="search" />
            <input type="text" placeholder="Search for anything" />
          </div>
        </div>
        <div className="navbar-center">
          <ul>
            <li>
              <NavLink 
                to="/home" 
                className={({ isActive }) => isActive ? 'active-link' : ''}
              >
                <img src="assets/images/home.png" alt="home" /> <span style={{color:"#000"}}>Home</span>
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/jobs" 
                className={({ isActive }) => isActive ? 'active-link' : ''}
              >
                <img src="assets/images/jobs.png" alt="jobs" /> <span style={{color:"#000"}}>Jobs</span>
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/Chat" 
                className={({ isActive }) => isActive ? 'active-link' : ''}
              >
                <img src="assets/images/message.png" alt="message" /> <span style={{color:"#000"}}>Messaging</span>
              </NavLink>
            </li>
            <li>
              <a href="/players">
                <img src="assets/images/network.png" alt="network" /> <span>Players</span>
              </a>
            </li>
            <li>
              <a href="/gpt">
                <img src="assets/images/message.png" alt="message" /> <span>Ask AI</span>
              </a>
            </li>
            <li className="notif-icon-wrapper">
              <a href="/notifications" className="notif-icon-link">
                <img src="assets/images/notification.png" alt="notification" />
                {unreadCount > 0 && (
                  <span className="notif-badge">{unreadCount}</span>
                )}
                <span>Notifications</span>
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
                  <div className="desc">{user.role}</div>
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
