import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import './FollowButton.css'; // Create this CSS file

const FollowButton = ({ targetUserId, currentUserId }) => {
  const [isFollowing, setIsFollowing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const token = Cookies.get('token');

  const fetchFollowStatus = useCallback(async () => {
    if (!token || !currentUserId || currentUserId === targetUserId) {
      setIsLoading(false);
      if (currentUserId === targetUserId) setIsFollowing(null); // Special state for self
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_BASE_URL}/users/${targetUserId}/is-following`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setIsFollowing(response.data.is_following);
    } catch (err) {
      console.error("Error fetching follow status:", err.response?.data?.message || err.message);
      setError("Could not load follow status.");
    } finally {
      setIsLoading(false);
    }
  }, [targetUserId, currentUserId, token]);

  useEffect(() => {
    fetchFollowStatus();
  }, [fetchFollowStatus]);

  const handleFollowToggle = async () => {
    if (!token || !currentUserId || currentUserId === targetUserId) return;
    
    const previousFollowState = isFollowing;
    setIsFollowing(!isFollowing); 
    setIsLoading(true);
    setError(null);

    const endpoint = previousFollowState
      ? `${process.env.REACT_APP_BASE_URL}/users/${targetUserId}/unfollow`
      : `${process.env.REACT_APP_BASE_URL}/users/${targetUserId}/follow`;

    try {
      await axios.post(
        endpoint,
        {}, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // State is already updated optimistically
    } catch (err) {
      console.error(`Error ${previousFollowState ? 'unfollowing' : 'following'} user:`, err.response?.data?.message || err.message);
      setError(`Failed to ${previousFollowState ? 'unfollow' : 'follow'}.`);
      setIsFollowing(previousFollowState); // Revert on error
    } finally {
      setIsLoading(false);
    }
  };

  if (currentUserId === targetUserId || isFollowing === null) {
    return null; // Don't show button for self
  }

  return (
    <>
      <button
        onClick={handleFollowToggle}
        disabled={isLoading}
        className={`follow-button ${isFollowing ? 'unfollow' : 'follow'}`}
      >
        {isLoading ? '...' : (isFollowing ? 'Unfollow' : 'Follow')}
      </button>
      {error && <p style={{ color: 'red', fontSize: '0.8em', marginLeft: '10px' }}>{error}</p>}
    </>
  );
};

export default FollowButton;