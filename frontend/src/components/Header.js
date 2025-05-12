import React, { useState, useEffect, useRef, useCallback } from 'react';
import './Header.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate, NavLink  ,Link} from "react-router-dom";
import {useLocation } from "react-router-dom";
import useDebounce from '../hooks/useDebounce';
import FollowButton from './FollowButton';

// Recent searches utility functions
function addSearch(user) {
  let recentSearches = JSON.parse(localStorage.getItem('recentSearches')) || [];
  recentSearches = recentSearches.filter(item => item.username !== user.username);
  recentSearches.unshift(user);
  recentSearches = recentSearches.slice(0, 5);
  localStorage.setItem('recentSearches', JSON.stringify(recentSearches));
}
function getRecentSearches() {
  return JSON.parse(localStorage.getItem('recentSearches')) || [];
}
const clearRecentSearches = () => {
  localStorage.removeItem('recentSearches');
  return [];
};

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const [isSearchHovered, setSearchHovered] = useState(false);
  const [suggestedUsers, setSuggestedUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [filter, setFilter] = useState('all'); // 👈 Filter state
  const [error, setError] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [showNotifPanel, setShowNotifPanel] = useState(false);
  const [playerId, setPlayerId] = useState(null);
  const user = Cookies.get('user') ? JSON.parse(Cookies.get('user')) : null;
  const token = Cookies.get('token');
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [isSearchResultsVisible, setIsSearchResultsVisible] = useState(false);
  const searchContainerRef = useRef(null); // For detecting clicks outside

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

  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  useEffect(() => {
    if (!token || !decodedToken) {
      navigate('/');
    } else if (date && date.getTime() < now.getTime()) {
      Cookies.remove('token');
      navigate('/');
    if (!token || !user) {
      console.log("User or token missing, potential redirect to /login");
    } else {
      const decodedToken = jwt_decode(token);
      const exp = decodedToken?.exp;
      const date = exp ? new Date(exp * 1000) : null;
      const now = new Date();
      if (date && date.getTime() < now.getTime()) {
        Cookies.remove('token');
        Cookies.remove('user');
        navigate('/login');
      } else {
        setAllowed(true);
      }
    }
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
 

  useEffect(() => {
    const recent = getRecentSearches();
    setSuggestedUsers(recent);
  }, [location.pathname]);

  useEffect(() => {
    const performSearch = async () => {
      if (!debouncedSearchQuery.trim()) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const response = await axios.get(
          `http://localhost:5000/search?q=${encodeURIComponent(debouncedSearchQuery)}&filter=${filter}`
        );
        setSearchResults(response.data);
      } catch (err) {
        console.error('Search failed:', err);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    };

    performSearch();
  }, [debouncedSearchQuery, filter]);

  const toggleDropdown = () => setDropdownOpen(!isDropdownOpen);
  const handleLogout = () => {
    navigate('/login');
    Cookies.remove('token');
    Cookies.remove('user');

  };

  // Conditionally render based on user data availability
  if (!user && !allowed) {
    return null;
  }
  const getUserImageUrl = (path) => {
    if (!path) return `${process.env.PUBLIC_URL}/assets/images/default-profile.png`;
    return path.startsWith('http') ? path : `${process.env.REACT_APP_BASE_URL || 'http://localhost:5000'}${path}`;
  };

  const handleUserClick = (user) => {
    addSearch(user);
    navigate('/profile_view', { state: { userId: user.id } });
    setSearchQuery('');
    setSearchResults([]);
    setSearchHovered(false);
  };

  const handleClearRecent = () => {
    setSuggestedUsers(clearRecentSearches());
  };

  if (!user) return <div>Loading...</div>;



  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-left">
          <a href="/home" className="meta-logo">
            <img 
              src={`${process.env.PUBLIC_URL}/assets/images/logo.png`} 
              alt="logo" 
              onError={(e) => e.target.src = `${process.env.PUBLIC_URL}/assets/images/default-profile.png`}
            />
          </a>

          <div 
            className="search-box"
            onMouseEnter={() => setSearchHovered(true)}
            onMouseLeave={() => setSearchHovered(false)}
          >
            <img 
              src={`${process.env.PUBLIC_URL}/assets/images/search.png`} 
              alt="search" 
            />
            <input 
              type="text" 
              placeholder="Search for anything" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setSearchHovered(true)}
              onBlur={() => setTimeout(() => setSearchHovered(false), 200)}
            />

            {/* 👇 Filter dropdown beside search input */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="search-filter-dropdown"
            >
              <option value="all">All</option>
              <option value="people">People</option>
              <option value="posts">Posts</option>
              {/* Add more options as needed */}
            </select>

             {(searchQuery || isSearchHovered) && (
              <div className="search-dropdown">
                {isSearching ? (
                  <div className="search-loading">Searching...</div>
                ) : searchResults.length > 0 ? (
                  <ul className="user-suggestions-list">
                    {searchResults.map((user) => (
                      <li
                        key={user.id}
                        className="user-suggestion-item"
                        onClick={() => handleUserClick(user)}
                      >
                        <img
                          src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`}
                          alt={user.username}
                          className="user-profile-image"
                          onError={(e) => {
                            e.target.onerror = null; // Prevents infinite loop if default also fails
                            e.target.src = `${process.env.PUBLIC_URL}/assets/images/default-profile.png`;
                          }}
                        />
                        <div className="user-info">
                          <span className="user-name">{user.name}</span>
                          <span className="username">{user.username}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : searchQuery ? (
                  <div className="search-empty">No results found</div>
                ) : (
                  <>
                    <div className="dropdown-header">
                      <span>Recent Searches</span>
                      {suggestedUsers.length > 0 && (
                        <button
                          className="clear-recent-btn"
                          onClick={handleClearRecent}
                        >
                          Clear all
                        </button>
                      )}
                    </div>
                    <ul className="user-suggestions-list">
                      {suggestedUsers.map((user, index) => (
                        <li
                          key={index} // Consider using a more stable key if available (e.g., user.id or user.username if unique for recent)
                          className="user-suggestion-item"
                          onClick={() => handleUserClick(user)}
                        >
                          <img
                            src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`}
                            alt={user.username}
                            className="user-profile-image"
                            onError={(e) => {
                              e.target.onerror = null; // Prevents infinite loop if default also fails
                              e.target.src = `${process.env.PUBLIC_URL}/assets/images/default-profile.png`;
                            }}
                          />
                          <div className="user-info">
                            <span className="user-name">{user.name}</span>
                            <span className="username">{user.username}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
          </div> 
        </div>
        <div className="navbar-center">
          <ul>
            <li>
              <NavLink
                to="/home"
                className={({ isActive }) => isActive ? 'active-link' : ''}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/home.png`} alt="home" /> <span style={{ color: "#000" }}>Home</span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/jobs"
                className={({ isActive }) => isActive ? 'active-link' : ''}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/jobs.png`} alt="jobs" /> <span style={{ color: "#000" }}>Jobs</span>
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/Chat"
                className={({ isActive }) => isActive ? 'active-link' : ''}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/message.png`} alt="message" /> <span style={{ color: "#000" }}>Messaging</span>
              </NavLink>
            </li>
            <li>
              {/* Assuming /players is a distinct page and not part of NavLink active state logic */}
              <Link to="/players">
                <img src={`${process.env.PUBLIC_URL}/assets/images/network.png`} alt="network" /> <span>Players</span>
              </Link>
            </li>
            <li>
              <Link to="/gpt">
                <img src={`${process.env.PUBLIC_URL}/assets/images/message.png`} alt="message" /> <span>Ask AI</span>
              </Link>
            </li>
            <li className="notif-icon-wrapper">
              <Link to="/notifications" className="notif-icon-link">
                <img src={`${process.env.PUBLIC_URL}/assets/images/notification.png`} alt="notification" />
                {unreadCount > 0 && (
                  <span className="notif-badge" style={{color:"#000"}}>{unreadCount}</span>
                )}
                <span>Notifications</span>
              </Link>
            </li>
            <li>
              <Link to="/analysis-hub" className={location.pathname.startsWith('/matches') || location.pathname.startsWith('/analysis-hub') ? 'active-link' : ''}>
                <img src={`${process.env.PUBLIC_URL}/assets/images/analysis.png`} alt="matches" /> <span>Analysis Hub</span>
              </Link>
            </li>
          </ul>
        </div>

        <div className="navbar-right" id="nav-right">
          {user && (
            <div className="online">
              <img
                src={user.profile_image ? `${process.env.REACT_APP_BASE_URL}/${user.profile_image}` : `${process.env.PUBLIC_URL}/assets/images/default-avatar.png`}
                className="nav-profile-img"
                alt="profile"
                onClick={toggleDropdown}
                onError={(e) => e.target.src = `${process.env.PUBLIC_URL}/assets/images/default-avatar.png`}
              />
            </div>
          )}

          {isDropdownOpen && user && (
            <div className="drop-menu">
              <div className="dropdown-header">
                <img
                  src={user.profile_image ? `${process.env.REACT_APP_BASE_URL}/${user.profile_image}` : `${process.env.PUBLIC_URL}/assets/images/default-avatar.png`}
                  alt="Profile"
                  className="dropdown-avatar"
                  onError={(e) => e.target.src = `${process.env.PUBLIC_URL}/assets/images/default-avatar.png`}
                />
                <div className="dropdown-info">
                  <div className="name">{user.name}</div>
                  <div className="desc">{user.role || "User"}</div> {/* Display role or a default */}
                </div>
              </div>
              {/* Choosing origin/Sadok version for profile links as it uses <Link> */}
              <Link to={`/profile/${user.username}`} className="profile-btn" onClick={() => setDropdownOpen(false)}>My posts</Link>
              <Link to="/saved-posts" className="profile-btn" onClick={() => setDropdownOpen(false)}>Saved Posts</Link>
              {user.role === "Player" ? (
                <a href="/Profile" className="profile-btn">See your profile</a>
              ) : ["Coach", "Staff", "Scout"].includes(user.role) ? (
                <a href="/CoachProfile" className="profile-btn">See your profile</a>
              ) : user.role === ("Manager") ? (
                <a href="/ManagerProfile" className="profile-btn">See your profile</a>
              ) : user.role === ("Agent") ? (
                <a href="/AgentProfile" className="profile-btn">See your profile</a>
              ) : user.role === ("Agency") ? (
                <a href="/AgencyProfile" className="profile-btn">See your profile</a>
              ) : user.role === ("Club") ? (
                <a href="/ClubProfile" className="profile-btn">See your profile</a>
              ) : (
                <a href="/Profile_View" className="profile-btn">See your profile</a>
              )}
              <a href="/" className="logout-btn" onClick={handleLogout}>Logout</a>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
};

export default Header;