import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";
import './Home.css'; // Reuse Home.css for similar styling

const SavedPosts = ({ header }) => {
  const navigate = useNavigate();
  const [savedPosts, setSavedPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [followersCount, setFollowersCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);
  
  const userCookie = Cookies.get('user');
  const currentUser = useMemo(() => {
    return userCookie ? JSON.parse(userCookie) : null;
  }, [userCookie]);
  const token = Cookies.get('token');

  // Utility function like getTimeAgo from Home.js (or move to a utils file)
  const getTimeAgo = (createdAt) => {
    const now = new Date();
    const postDate = new Date(createdAt);
    const timeDiff = now - postDate;
    const seconds = Math.floor(timeDiff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return `${seconds} second${seconds > 1 ? 's' : ''} ago`;
  };

  useEffect(() => {
    if (!token || !currentUser) {
      navigate('/login');
      return;
    }

    const fetchSavedPosts = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `${process.env.REACT_APP_BASE_URL}/users/${currentUser.id}/saved_posts`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setSavedPosts(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching saved posts:', err);
        setError(err.response?.data?.message || 'Failed to load saved posts.');
        if (err.response?.status === 401) {
            Cookies.remove('token');
            Cookies.remove('user');
            navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
      const fetchFollowCounts = async () => {
      if (currentUser && currentUser.id) {
        try {
          // Assuming you have endpoints like these:
          const followersResponse = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${currentUser.id}/followers`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setFollowersCount(followersResponse.data.count || followersResponse.data.length); // Adjust based on your API response

          const followingResponse = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${currentUser.id}/following`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setFollowingCount(followingResponse.data.count || followingResponse.data.length); // Adjust based on your API response
        } catch (err) {
          console.error('Error fetching follow counts:', err);
          // Optionally set an error state for follow counts
        }
      }
    };

    fetchSavedPosts();
    fetchFollowCounts();
  }, [token, currentUser, navigate]);
  
  const handleUnsavePost = async (postId) => {
    if (!currentUser || !token) {
      alert('Please log in.');
      navigate('/login');
      return;
    }
    try {
      await axios.delete(
        `${process.env.REACT_APP_BASE_URL}/posts/${postId}/unsave`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      // Update UI by removing the unsaved post
      setSavedPosts(prevPosts => prevPosts.filter(p => p.id !== postId));
    } catch (err) {
      console.error('Error unsaving post:', err);
      alert('Failed to unsave post.');
    }
  };

  if (loading) {
    return <div>{header}<div className="container"><p>Loading saved posts...</p></div></div>;
  }

  if (error) {
    return <div>{header}<div className="container"><p>Error: {error}</p></div></div>;
  }

  return (
    <div>
      {header}
      <div className="container">
        <div className="left-sidebar">
          {currentUser && (
            <div className="sidebar-profile-box">
              {/* You can use a generic cover or remove it */}
              <img src="/assets/images/cover-pic.jpg" alt="cover" width="100%" />
              <div className="sidebar-profile-info">
                <img
                  src={currentUser.profile_image ? `${process.env.REACT_APP_BASE_URL}/${currentUser.profile_image}` : 'assets/images/default-avatar.png'}
                  alt="profile"
                  onError={(e) => e.target.src = 'assets/images/default-avatar.png'}
                />
                <h1>{currentUser.name}</h1>
                <ul>
                  {/* Assuming you want to display counts similar to Profile.js */}
                  {/* You might want to make these clickable to a list later */}
                  <li>Followers <span>{followersCount}</span></li>
                  <li>Following <span>{followingCount}</span></li>
                  <li>Saved Posts <span>{savedPosts.length}</span></li>
                </ul>
              </div>
            </div>
          )}
          {/* You can add other sections like 'sidebar-activity' from Home.js if needed */}
        </div>
        <div className="main-content">
          <h2 style={{ color: 'black' }}>My Saved Posts</h2>
          {savedPosts.length === 0 ? (
            <p>You haven't saved any posts yet.</p>
          ) : (
            savedPosts.map((post) => (
              <div key={post.id} className="post">
                <div className="post-author">
                  <img
                    src={post.user_profile_image ? `${process.env.REACT_APP_BASE_URL}/${post.user_profile_image}` : 'assets/images/default-avatar.png'}
                    alt="author"
                    onError={(e) => e.target.src = 'assets/images/default-avatar.png'}
                  />
                  <div>
                    <h1>{post.user_name}</h1>
                    <small>Original post from: {getTimeAgo(post.created_at)}</small>
                  </div>
                  <button
                    onClick={() => handleUnsavePost(post.id)}
                    className="save-button saved" // Always show as "saved" style, action is to unsave
                    style={{ marginLeft: 'auto', padding: '5px 10px', cursor: 'pointer' }}
                    title="Unsave Post"
                  >
                    ❤️ Unsave
                  </button>
                </div>
                <p>{post.content}</p>
                {post.image_url && (
                  <img
                    src={`${process.env.REACT_APP_BASE_URL}${post.image_url}`}
                    alt="post content"
                    style={{ width: '100%' }}
                  />
                )}
                {post.video_url && (
                  <video autoPlay muted controls style={{ width: '100%' }}>
                    <source src={`${process.env.REACT_APP_BASE_URL}${post.video_url}`} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                )}
                <div className="post-activity">
                  {/* Simplified activity: Link to original post or view comments could be added here */}
                  {/* Example: <a href={`/post/${post.id}`}>View Post Details</a> */}
                </div>
              </div>
            ))
          )}
        </div>
        <div className="right-sidebar">
          <div className="sidebar-news">
            <img src="assets/images/more.svg" className="info-icon" alt="more" />
            <h3>Trending News</h3>
            <a href="#">High Demand for Skilled Employees</a>
            <span>1d ago &middot; 10,934 readers</span>
            <a href="#">Inflation in Canada Affects the Workforce</a>
            <span>2d ago &middot; 7,043 readers</span>
            <a href="#">Mass Recruiters fire Employees</a>
            <span>4d ago &middot; 17,789 readers</span>
            <a href="#">Crypto predicted to Boom this year</a>
            <span>9d ago &middot; 2,436 readers</span>
            <a href="#" className="read-more-link">Read More</a>
          </div>

          <div className="sidebar-ad">
            <small>Ad &middot; &middot; &midd;</small>
            <p>Master Web Development</p>
            <div>
              <img 
                src={currentUser?.profile_image ? `${process.env.REACT_APP_BASE_URL}/${currentUser.profile_image}` : 'assets/images/default-avatar.png'}  
                alt="user" 
                onError={(e) => e.target.src = 'assets/images/default-avatar.png'}
              />
              <img src="assets/images/mi-logo.png" alt="mi logo" />
            </div>
            <b>Brand and Demand in Xiaomi</b>
            <a href="#" className="ad-link">Learn More</a>
          </div>

          <div className="sidebar-useful-links">
            <a href="#">About</a>
            <a href="#">Accessibility</a>
            <a href="#">Help Center</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Advertising</a>
            <a href="#">Get the App</a>
            <a href="#">More</a>
            <div className="copyright-msg">
              <img src="assets/images/logo.png" alt="logo" />
              <p>MetaScout &#169; 2025. All Rights Reserved</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SavedPosts;