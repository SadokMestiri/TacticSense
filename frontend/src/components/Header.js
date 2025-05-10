import React, { useState, useEffect } from 'react';
import './Header.css';
import axios from 'axios';

const Header = () => {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const user_id = localStorage.getItem('user_id');
  const [error, setError] = useState(null);
  const [user, setUser] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [playerId, setPlayerId] = useState(null);


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


  const unreadCount = notifications.filter(n => !n.is_read).length;

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