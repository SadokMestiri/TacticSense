import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import './ProfileCard.css'; // Create this for custom styles
import Header from './Header'; // Import your Header component
import './Header.css';

const ProfileCard = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  //const [isFollowing, setIsFollowing] = useState(false);
  const currentUser = JSON.parse(Cookies.get('user'));
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
  const [header, setHeader] = useState(null);

  // Token expiration check
  useEffect(() => {
    if (!token || !decodedToken) {
      navigate('/login');
    } else if (date && date.getTime() < now.getTime()) {
      Cookies.remove('token');
      navigate('/login');
    } else {
      setAllowed(true);
      setHeader(<Header />);
    }
  }, [token, decodedToken, navigate, date]);

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/user/${username}`);
        setUser(response.data);
        // Check if current user is following this profile
        /*if (currentUser) {
          const followCheck = await axios.get(`http://localhost:5000/is_following`, {
            params: { follower_id: currentUser.id, followed_id: response.data.id }
          });
          setIsFollowing(followCheck.data.is_following);
        }*/
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    if (allowed) {
      fetchUserProfile();
    }
  }, [username, currentUser?.id, allowed]);

  /*const handleFollow = async () => {
    try {
      if (isFollowing) {
        await axios.post('http://localhost:5000/unfollow', {
          follower_id: currentUser.id,
          followed_id: user.id
        });
      } else {
        await axios.post('http://localhost:5000/follow', {
          follower_id: currentUser.id,
          followed_id: user.id
        });
      }
      setIsFollowing(!isFollowing);
    } catch (err) {
      console.error('Follow action failed:', err);
    }
  };*/
    

  if (loading) return <div className="loading-spinner">Loading...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!user) return <div className="not-found">User not found</div>;
  
  const getUserImageUrl = (path) => {
    if (!path) return `${process.env.PUBLIC_URL}/assets/images/default-profile.png`;
    return path.startsWith('http') ? path : `${process.env.REACT_APP_BASE_URL || 'http://localhost:5000'}${path}`;
  };  
  
  return (
    <div>
      {header}
      <div className="profile-container">
        <div className="cover-photo">
          <img 
            src={`${process.env.PUBLIC_URL}/assets/images/background.jpg`} 
            alt="Cover" 
            className="cover-image"
          />
        </div>  
        
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            <img 
              src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`}
              alt={user.name} 
              className="avatar-image"
            />
          </div>
        </div>

        {/* Profile Content */}
        <div className="profile-content">
          <h1 className="profile-name">{user.username}</h1>
          <h1 className="profile-name">{user.name}</h1>
          <p className="profile-location">
            {user.location || 'Location not specified'} · 
            <span className="profile-connections"> 0 followers</span>
          </p>

          <div className="profile-bio">
            <h3>About</h3>
            <p>{user.bio || 'No bio available'}</p>
          </div>

           
          <div className="profile-actions">
              {/*
            {currentUser && currentUser.id !== user.id && (
              <button 
                className={`follow-btn ${isFollowing ? 'following' : ''}`}
                onClick={handleFollow}
              >
                {isFollowing ? 'Following' : '+ Follow'}
              </button>
            )}
            */}

            <button className="action-btn connect-btn">Follow</button>
            <button className="action-btn message-btn">Message</button>
            <button className="action-btn more-btn">More</button>
          </div>

          {/* Profile Sections */}
          <div className="profile-sections">
            <div className="section experience">
              <h3>Experience</h3>
              {user.experiences?.length > 0 ? (
                user.experiences.map((exp, index) => (
                  <div key={index} className="experience-item">
                    <h4>{exp.title}</h4>
                    <p>{exp.company}</p>
                    <p>{exp.duration}</p>
                  </div>
                ))
              ) : (
                <p>No experience added</p>
              )}
            </div>
          </div>
          <div className="profile-sections">
            <div className="section experience">
              <h3>Posts</h3>
              {user.experiences?.length > 0 ? (
                user.experiences.map((exp, index) => (
                  <div key={index} className="experience-item">
                    <h4>{exp.title}</h4>
                    <p>{exp.company}</p>
                    <p>{exp.duration}</p>
                  </div>
                ))
              ) : (
                <p>No posts added</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileCard;