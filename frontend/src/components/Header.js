import React, { useState, useEffect, useRef, useCallback } from 'react';
import './Header.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate,Link } from "react-router-dom";
import FollowButton from './FollowButton';

const Header = () => {
  const navigate = useNavigate();
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
              <a href="#">
                <img src="/assets/images/notification.png" alt="notification" /> <span>Notifications</span>
              </a>
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
