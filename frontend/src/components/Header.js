import React, { useState, useEffect } from 'react';
import './Header.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate, useLocation } from "react-router-dom";
import useDebounce from '../hooks/useDebounce';

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

  const user = JSON.parse(Cookies.get('user'));
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

  const debouncedSearchQuery = useDebounce(searchQuery, 300);

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

  useEffect(() => {
    const recent = getRecentSearches();
    if (recent.length > 0) setSuggestedUsers(recent);
  }, []);

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
    Cookies.remove('token');
    Cookies.remove('user');
    navigate('/login');
  };

  const getUserImageUrl = (path) => {
    if (!path) return `${process.env.PUBLIC_URL}/assets/images/default-profile.png`;
    return path.startsWith('http') ? path : `${process.env.REACT_APP_BASE_URL || 'http://localhost:5000'}${path}`;
  };

  const handleUserClick = (user) => {
    addSearch(user);
    navigate(`/user/${user.username}`);
    setSearchQuery('');
    setSearchResults([]);
    setSearchHovered(false);
  };

  const handleClearRecent = () => {
    setSuggestedUsers(clearRecentSearches());
  };

  if (!user) return <div>Loading...</div>;

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-left">
          <a href="/" className="meta-logo">
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
                            e.target.onerror = null;
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
                          key={index} 
                          className="user-suggestion-item"
                          onClick={() => handleUserClick(user)}
                        >
                          <img 
                            src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`}
                            alt={user.username}
                            className="user-profile-image"
                            onError={(e) => {
                              e.target.onerror = null;
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
              <a 
                href="/" 
                className={location.pathname === '/' ? 'active-link' : ''}
                onClick={(e) => {
                  e.preventDefault();
                  navigate('/');
                }}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/home.png`} alt="home" /> 
                <span>Home</span>
              </a>
            </li>
            <li>
              <a 
                href="/network" 
                className={location.pathname === '/network' ? 'active-link' : ''}
                onClick={(e) => {
                  e.preventDefault();
                  navigate('/network');
                }}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/network.png`} alt="network" /> 
                <span>My Network</span>
              </a>
            </li>
            <li>
              <a 
                href="/jobs" 
                className={location.pathname === '/jobs' ? 'active-link' : ''}
                onClick={(e) => {
                  e.preventDefault();
                  navigate('/jobs');
                }}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/jobs.png`} alt="jobs" /> 
                <span>Jobs</span>
              </a>
            </li>
            <li>
              <a 
                href="/chat" 
                className={location.pathname === '/chat' ? 'active-link' : ''}
                onClick={(e) => {
                  e.preventDefault();
                  navigate('/chat');
                }}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/message.png`} alt="message" /> 
                <span>Messaging</span>
              </a>
            </li>
            <li>
              <a 
                href="/notifications" 
                className={location.pathname === '/notifications' ? 'active-link' : ''}
                onClick={(e) => {
                  e.preventDefault();
                  navigate('/notifications');
                }}
              >
                <img src={`${process.env.PUBLIC_URL}/assets/images/notification.png`} alt="notification" /> 
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
                  <div className="desc">{user.title || 'Professional footballer'}</div>
                </div>
              </div>
              <a 
                href={`/user/${user.username}`} 
                className="profile-btn"
                onClick={(e) => {
                  e.preventDefault();
                  navigate(`/user/${user.username}`);
                }}
              >
                See your profile
              </a>
              <a 
                href="#" 
                className="logout-btn" 
                onClick={handleLogout}
              >
                Logout
              </a>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
};

export default Header;