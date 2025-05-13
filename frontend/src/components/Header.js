import React, { useState, useEffect, useRef, useCallback } from 'react';
import './Header.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate,Link, useLocation } from "react-router-dom";
import FollowButton from './FollowButton';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isNotificationDropdownOpen, setNotificationDropdownOpen] = useState(false);
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const user =  JSON.parse(Cookies.get('user'));
  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [isSearchResultsVisible, setIsSearchResultsVisible] = useState(false);
  const searchContainerRef = useRef(null); // For detecting clicks outside
  const notificationDropdownRef = useRef(null); // Ref for notification dropdown

  // Notification State
  const [notifications, setNotifications] = useState([]);
  const [isLoadingNotifications, setIsLoadingNotifications] = useState(false);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);


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

  // Debounce function
    const debounce = (func, delay) => {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
      };
    };

    // API call for searching users
    const fetchUsers = async (query) => {
      if (!query.trim()) {
        setSearchResults([]);
        setIsSearchResultsVisible(false);
        return;
      }
      setIsSearchLoading(true);
      setIsSearchResultsVisible(true);
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BASE_URL}/users/search?q=${encodeURIComponent(query)}`
          // No token needed for public search as per backend, but include if your API requires it
          // { headers: { Authorization: `Bearer ${token}` } }
        );
        setSearchResults(response.data || []);
      } catch (err) {
        console.error("Error searching users:", err);
        setSearchResults([]);
        // setError("Failed to search users."); // You can use an error state if needed
      } finally {
        setIsSearchLoading(false);
      }
    };

  // Debounced version of fetchUsers
  const debouncedFetchUsers = useCallback(debounce(fetchUsers, 500), []); // 500ms debounce

  useEffect(() => {
    debouncedFetchUsers(searchQuery);
  }, [searchQuery, debouncedFetchUsers]);

  // Handle click outside for search results
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setIsSearchResultsVisible(false);
      }
      // Close notification dropdown if click is outside
      if (notificationDropdownRef.current && !notificationDropdownRef.current.contains(event.target) && !event.target.closest('.navbar-center li a[href="#"] > img[alt="notification"]')) {
        setNotificationDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);


  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    
  };

  const handleResultClick = () => {
    setIsSearchResultsVisible(false); // Hide results when a user is clicked
    setSearchQuery(''); // Optionally clear search query
  };

  // Handle dropdown toggle for user profile
  const toggleDropdown = () => {
    setDropdownOpen(!isDropdownOpen);
    setNotificationDropdownOpen(false);
  };

  // New handler for notification dropdown
  const toggleNotificationDropdown = () => {
    const willOpen = !isNotificationDropdownOpen;
    setNotificationDropdownOpen(willOpen);
    if (willOpen) {
      fetchNotifications(); // Fetch notifications when dropdown is opened
    }
    setDropdownOpen(false);
  };
  // Fetch Notifications
  const fetchNotifications = async () => {
    if (!token) return;
    setIsLoadingNotifications(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/api/notifications`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications(response.data.notifications || []);
      setUnreadNotificationCount(response.data.unread_count || 0);
    } catch (err) {
      console.error("Error fetching notifications:", err);
      // Handle error (e.g., show a message)
    } finally {
      setIsLoadingNotifications(false);
    }
  };
  // Fetch initial unread count on load
  useEffect(() => {
    const fetchInitialUnreadCount = async () => {
        if (!token) return;
        try {
            // Assuming your backend has an endpoint for just the count or it's part of a user profile fetch
            // For now, we'll rely on the count from the full fetchNotifications or you can add a dedicated endpoint
            // This is a placeholder, adjust if you have a specific endpoint for unread count
            const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/api/notifications/unread_count`, {
                 headers: { Authorization: `Bearer ${token}` },
            });
            setUnreadNotificationCount(response.data.unread_count || 0);
        } catch (err) {
            console.error("Error fetching unread notification count:", err);
        }
    };
    if (user) { // Only fetch if user is loaded
        fetchInitialUnreadCount();
        // Optional: Set up a poller or WebSocket for real-time updates
        const intervalId = setInterval(fetchInitialUnreadCount, 60000); // Poll every 60 seconds
        return () => clearInterval(intervalId);
    }
  }, [token, user]);
  const handleNotificationClick = async (notification) => {
    setNotificationDropdownOpen(false);

    let targetPostId = notification.post_id;
    let targetCommentId = notification.type === 'mention_comment' ? notification.comment_id : null;
    let targetHash = '';

    if (notification.type === 'new_follower' && notification.sender_username) {
      navigate(`/profile/${notification.sender_username}`);
    } else if (targetPostId) { // For mention_post or mention_comment
      targetHash = `#post-${targetPostId}`;
      navigate(
        location.pathname + location.search + targetHash,
        { 
          state: { 
            scrollToCommentId: targetCommentId, 
            fromNotification: true 
          } 
        }
      );
    }
    // else: Handle other notification types here if they don't involve navigation or have custom logic

    // Mark as read on the backend
    if (!notification.is_read) {
      try {
        await axios.post(`${process.env.REACT_APP_BASE_URL}/api/notifications/${notification.id}/read`, {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setNotifications(prev => prev.map(n => n.id === notification.id ? { ...n, is_read: true } : n));
        setUnreadNotificationCount(prev => Math.max(0, prev - 1));
      } catch (err) {
        console.error("Error marking notification as read:", err);
      }
    }
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
            <img src="/assets/images/logo.png" alt="logo" />
          </a>
          <div className="search-box" ref={searchContainerRef}>
            <img src="/assets/images/search.png" alt="search" />
            <input
              type="text"
              placeholder="Search for users..."
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={() => searchQuery && setIsSearchResultsVisible(true)} // Show on focus if query exists
            />
            {isSearchResultsVisible && (
              <div className="search-results-dropdown">
                {isSearchLoading ? (
                  <div className="search-result-item">Loading...</div>
                ) : searchResults.length > 0 ? (
                  searchResults.map(resultUser => (
                    <div key={resultUser.id} className="search-result-item">
                      <Link to={`/profile/${resultUser.username}`} onClick={handleResultClick} className="search-result-link">
                        <img
                          src={resultUser.profile_image ? `${process.env.REACT_APP_BASE_URL}/${resultUser.profile_image}` : '/assets/images/default-avatar.png'}
                          alt={resultUser.name}
                          className="search-result-avatar"
                          onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                        />
                        <div className="search-result-info">
                          <span className="search-result-name">{resultUser.name}</span>
                          <span className="search-result-username">@{resultUser.username}</span>
                        </div>
                      </Link>
                      {user && user.id !== resultUser.id && (
                        <FollowButton targetUserId={resultUser.id} currentUserId={user.id} />
                      )}
                    </div>
                  ))
                ) : (
                  searchQuery && <div className="search-result-item">No users found.</div>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="navbar-center">
          <ul>
            <li>
              <a href="/" className="active-link"> {/* Changed href to / for home */}
                <img src="/assets/images/home.png" alt="home" /> <span>Home</span>
              </a>
            </li>
            <li>
              <a href="#">
                <img src="/assets/images/network.png" alt="network" /> <span>My Network</span>
              </a>
            </li>
            <li>
              <a href="#">
                <img src="/assets/images/jobs.png" alt="jobs" /> <span>Jobs</span>
              </a>
            </li>
            <li>
              <a href="/Chat">
                <img src="/assets/images/message.png" alt="message" /> <span>Messaging</span>
              </a>
            </li>
            <li>
              <a href="#" onClick={toggleNotificationDropdown} className={`notification-icon-anchor ${isNotificationDropdownOpen ? 'active-link' : ''}`}>
                <img src="/assets/images/notification.png" alt="notification" />
                {unreadNotificationCount > 0 && (
                  <span className="notification-badge">{unreadNotificationCount}</span>
                )}
                <span>Notifications</span>
              </a>
              {isNotificationDropdownOpen && (
                <div className="drop-menu notification-dropdown" ref={notificationDropdownRef}>
                  <div className="dropdown-header-simple">
                    <h3>Notifications</h3>
                  </div>
                  {isLoadingNotifications ? (
                    <div className="dropdown-item">Loading...</div>
                  ) : notifications.length > 0 ? (
                    notifications.map(notif => (
                      <div
                        key={notif.id}
                        className={`dropdown-item notification-item ${!notif.is_read ? 'unread' : ''}`}
                        onClick={() => handleNotificationClick(notif)}
                      >
                        <img
                          src={notif.sender_profile_image ? `${process.env.REACT_APP_BASE_URL}/${notif.sender_profile_image}` : '/assets/images/default-avatar.png'}
                          alt={notif.sender_name}
                          className="notification-avatar"
                          onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                        />
                        <div className="notification-content">
                          <p>
                            <strong>{notif.sender_name}</strong>
                            {notif.type === 'mention_post' && ' mentioned you in a post.'}
                            {notif.type === 'mention_comment' && ' mentioned you in a comment.'}
                            {notif.type === 'new_follower' && ' started following you.'} {/* New notification type message */}
                            {/* Add other notification types as needed */}
                          </p>
                          <small className="notification-time">{new Date(notif.created_at).toLocaleString()}</small>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="dropdown-item">No new notifications.</div>
                  )}
                </div>
              )}
            </li>
          </ul>
        </div>
        
        <div className="navbar-right" id="nav-right">
          <div className="online">
            <img
              src={user.profile_image ? `${process.env.REACT_APP_BASE_URL}/${user.profile_image}` : '/assets/images/default-avatar.png'}
              className="nav-profile-img"
              alt="profile"
              onClick={toggleDropdown}
              onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
            />
          </div>
          
          {isDropdownOpen && (
            <div className="drop-menu">
              <div className="dropdown-header">
                <img
                  src={user.profile_image ? `${process.env.REACT_APP_BASE_URL}/${user.profile_image}` : '/assets/images/default-avatar.png'}
                  alt="Profile"
                  className="dropdown-avatar"
                  onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                />
                <div className="dropdown-info">
                  <div className="name">{user.name}</div>
                  <div className="desc">{"Professional footballer"}</div> {/* Consider making this dynamic */}
                </div>
              </div>
                <Link to={`/profile/${user.username}`} className="profile-btn" onClick={() => setDropdownOpen(false)}>See your profile</Link>
                <Link to="/saved-posts" className="profile-btn" onClick={() => setDropdownOpen(false)}>Saved Posts</Link>
                <a href="#" className="logout-btn" onClick={handleLogout}>Logout</a>
              </div>
          )}
        </div>
      </nav>
    </div>
  );
};

export default Header;
