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

    fetchSavedPosts();
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
        {/* You can reuse the left and right sidebar structure from Home.js if desired */}
        {/* For simplicity, this example focuses on the main content area */}
        <div className="main-content">
          <h2>My Saved Posts</h2>
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
                {/* 
                  Displaying full reactions, comments, and comment input 
                  would require the /users/<id>/saved_posts endpoint to return more data 
                  or making additional calls. For now, this is a simplified view.
                */}
                <div className="post-activity">
                  {/* Simplified activity: Link to original post or view comments could be added here */}
                  {/* Example: <a href={`/post/${post.id}`}>View Post Details</a> */}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default SavedPosts;