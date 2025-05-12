import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate,Link } from "react-router-dom";
import './Home.css';
import Notifications from './Notifications'
import CustomVideoPlayer from './CustomVideoPlayer';
import RecommendationSidebar from './RecommendationSidebar';

import MentionInput from './MentionInput'; 

const Home = ({ header , footer}) => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false); // For potential mobile menu
  const [isActivityOpen, setIsActivityOpen] = useState(false); // For "RECENT", "GROUPS" sidebar

  const [posts, setPosts] = useState([]);
  const [text, setText] = useState(''); // For new post content
  const [image, setImage] = useState(null); // For new post image
  const [video, setVideo] = useState(null); // For new post video
  const [mentionedUsersInPost, setMentionedUsersInPost] = useState([]); // Users mentioned in new post

  const [users, setUsers] = useState({}); // Stores fetched user data (e.g., { userId: {profile_image: '...'} })
  const [error, setError] = useState(null);
  const [comments, setComments] = useState([]);
  const [metaBalance, setMetaBalance] = useState(null);
  const [metaCoinMessage, setMetaCoinMessage] = useState(false);
  const [checkingBalance, setCheckingBalance] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null); // For managing the selected post
  const [showReactions, setShowReactions] = useState(null);
const reactions = [
  { name: "like", icon: "assets/images/post-like.png" },
  { name: "love", icon: "assets/images/love.png" },
  { name: "laugh", icon: "assets/images/haha.png" },
  { name: "wow", icon: "assets/images/wow.png" },
  { name: "sad", icon: "assets/images/sad.png" },
  { name: "angry", icon: "assets/images/angry.png" },
];
const [sortOption, setSortOption] = useState('date-desc'); // Default sort option
const [filterType, setFilterType] = useState('all'); // Default filter type
const [allPosts, setAllPosts] = useState([]);
const token = Cookies.get('token');
let decodedToken = null;
let exp = null;

const [selectedPostForComments, setSelectedPostForComments] = useState(null); // Post whose comments are being viewed
 const [isCommentsVisible, setIsCommentsVisible] = useState(false); // Comments modal visibility

const date = exp ? new Date(exp * 1000) : null;
const now = new Date();
const [allowed, setAllowed] = useState(false);
const userCookie = Cookies.get('user');
const user = userCookie ? JSON.parse(userCookie) : null;
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
  const [commentText, setCommentText] = useState(''); // For new comment content
  const [mentionedUsersInComment, setMentionedUsersInComment] = useState([]); // Users mentioned in new comment
  const [isCommentingOnPostId, setIsCommentingOnPostId] = useState(null); // ID of post being commented on

  // Token and user setup
  useEffect(() => {
    const token = Cookies.get('token');
    const userCookie = Cookies.get('user');

    if (token && userCookie) {
      try {
        const decodedToken = jwt_decode(token);
        const exp = decodedToken?.exp;
        const date = exp ? new Date(exp * 1000) : null;
        const now = new Date();

        if (date && date.getTime() < now.getTime()) {
          Cookies.remove('token');
          Cookies.remove('user');
          navigate('/login');
        } else {
          setUser(JSON.parse(userCookie));
          setAllowed(true);
        }
      } catch (e) {
        console.error("Error decoding token or parsing user cookie:", e);
        Cookies.remove('token');
        Cookies.remove('user');
        navigate('/login');
      }
    } else {
      navigate('/login');
    }
  }, [navigate]);

  const constructMediaUrl = (urlPath) => {
    if (!urlPath) return '';
    if (urlPath.startsWith('http://') || urlPath.startsWith('https://')) {
      return urlPath;
    }
    // Assuming REACT_APP_BASE_URL is like 'http://localhost:5000' and urlPath might be '/uploads/image.jpg' or 'uploads/image.jpg'
    const baseUrl = process.env.REACT_APP_BASE_URL || '';
    return `${baseUrl}${urlPath.startsWith('/') ? '' : '/'}${urlPath}`;
  };

  const getTimeAgo = (createdAt) => {
    const now = new Date();
    const postDate = new Date(createdAt);
    const timeDiff = now - postDate; // Difference in milliseconds

    const seconds = Math.floor(timeDiff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const weeks = Math.floor(days / 7);
    const months = Math.floor(days / 30);
    const years = Math.floor(days / 365);

    if (years > 0) {
      return `${years} year${years > 1 ? 's' : ''} ago`;
    } else if (months > 0) {
      return `${months} month${months > 1 ? 's' : ''} ago`;
    } else if (weeks > 0) {
      return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else if (days > 0) {
      return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
      return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else {
      return `${seconds} second${seconds > 1 ? 's' : ''} ago`;
    }
  };

  const [isCommenting, setIsCommenting] = useState(false);
  const [comment, setComment] = useState(''); // Store comment text
  
  const renderContent = (content) => {
    return content.split(/(\s+)/).map((part, i) => {
      // Check if the part starts with a hashtag
      if (part.startsWith("#")) {
        const tag = part.slice(1);
        return (
          <Link
            key={i}
            to="/hashtag"
            state={{ hashtag: tag,type:"post" }} // Pass the hashtag as state
            style={{ color: "#0073b1" }}
          >
            {part}
          </Link>
        );
      } else {
        // For regular text, simply return the part
        return part;
      }
    });
  };
  


  const fetchUsersData = useCallback(async (userIds) => {
    const uniqueUserIds = Array.from(new Set(userIds.filter(id => id))); // Ensure unique, non-null IDs
    const usersToFetch = uniqueUserIds.filter(id => !users[id]);
    
    if (usersToFetch.length === 0) return;

    try {
      // In a real app, you might have a batch endpoint, or fetch one by one
      // For simplicity, fetching one by one here. Consider a batch endpoint for performance.
      const fetchedUsersData = {};
      for (const userId of usersToFetch) {
        try {
          const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${userId}`);
          if (response.data) {
            fetchedUsersData[userId] = response.data;
          }
        } catch (userError) {
          console.error(`Error fetching user data for ID ${userId}:`, userError);
          // Optionally, set a placeholder or skip this user
        }
      }
      setUsers(prevUsers => ({
        ...prevUsers,
        ...fetchedUsersData,
      }));
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  }, [users]); // Dependency: users state to avoid re-fetching already fetched users


  // Unified fetchPosts function
  const fetchPosts = useCallback(async () => {
    if (!allowed || !user) {
      // console.log("fetchPosts: Not allowed or no user, returning.");
      return;
    }
    try {
      const token = Cookies.get('token');
      // console.log("fetchPosts: Fetching with token...");
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_posts`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const postsData = response.data;

      if (Array.isArray(postsData)) {
        // console.log("fetchPosts: Posts data received", postsData.length);
        setAllPosts(postsData); // Store all fetched posts

        // Extract user IDs from posts and fetch their data
        const userIdsFromPosts = postsData.map(post => post.user_id).filter(id => id); // Filter out null/undefined
        if (userIdsFromPosts.length > 0) {
          // console.log("fetchPosts: Fetching user data for post authors");
          await fetchUsersData(userIdsFromPosts);
        }
        // The useEffect hook below will handle sorting, filtering, and setting the 'posts' state
      } else {
        console.error("Error fetching posts: API did not return an array.", postsData);
        setAllPosts([]);
        setPosts([]); // Clear displayable posts as well
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      if (error.response && error.response.status === 401) {
        Cookies.remove('token');
        Cookies.remove('user');
        navigate('/login');
      } else {
        setAllPosts([]);
        setPosts([]);
      }
    }
  }, [allowed, user, navigate, fetchUsersData]); // Dependencies for the fetchPosts callback

  // useEffect to call fetchPosts when user/auth status changes
  useEffect(() => {
    // console.log("useEffect (fetchPosts trigger): allowed, user changed", allowed, !!user);
    if (allowed && user) {
      fetchPosts();
    }
  }, [allowed, user, fetchPosts]); // fetchPosts is a dependency

  // useEffect to handle sorting and filtering whenever allPosts, sortOption, or filterType changes
  useEffect(() => {
    // console.log("useEffect (sorting/filtering): allPosts, sortOption, or filterType changed");
    if (allPosts && allPosts.length > 0) {
      let processedPosts = [...allPosts]; // Create a new array for processing
      processedPosts = filterPosts(processedPosts, filterType);
      processedPosts = sortPosts(processedPosts, sortOption);
      setPosts(processedPosts);
    } else {
      setPosts([]); // If allPosts is empty, ensure posts is also empty
    }
  }, [allPosts, sortOption, filterType, filterPosts, sortPosts]); // filterPosts and sortPosts should be stable or included if they can change


  // Fonction de tri
  const sortPosts = (postsData, option) => {
    switch (option) {
      case 'date-asc':
        return postsData.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      case 'date-desc':
        return postsData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      case 'popularity':
        return postsData.sort((a, b) => (b.likes || 0) - (a.likes || 0));
      default:
        return postsData;
    }
  };

  // Fonction de filtrage par type de post
  const filterPosts = (postsData, type) => {
    if (type === 'all') return postsData;
    return postsData.filter(post => {
      if (type === 'text') return !post.image_url && !post.video_url;
      if (type === 'image') return post.image_url;
      if (type === 'video') return post.video_url;
      return true;
    });
  };

  useEffect(() => {
    let filteredPosts = filterPosts([...allPosts], filterType);
    filteredPosts = sortPosts(filteredPosts, sortOption);
    setPosts(filteredPosts);
  }, [sortOption, filterType, allPosts]);

  useEffect(() => {
    fetchPosts();
  }, []);

  const handleSortChange = (e) => {
    setSortOption(e.target.value);
  };

  const handleFilterTypeChange = (e) => {
    setFilterType(e.target.value);
  };
  const handleReaction = async (postId, reactionType) => {
    if (!user) return;
    const token = Cookies.get('token');
    if (!token) { navigate('/login'); return; }
    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/react_to_post`, {
        // user_id: user.id, // Backend uses token
        post_id: postId,
        reaction_type: reactionType,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });

      console.log(`Reaction (${reactionType}) added:`, response.data);
      fetchPosts(); // Refresh posts to update reactions count
    } catch (error) {
      console.error('Error adding reaction:', error);
      alert('There was an error reacting to the post. ' + (error.response?.data?.error || ''));
    }
  };

  const handleSavePost = async (postId, isCurrentlySaved) => {
    if (!user) { navigate('/login'); return; }
    const token = Cookies.get('token');
    if (!token) { navigate('/login'); return; }
    try {
      const endpoint = isCurrentlySaved
        ? `${process.env.REACT_APP_BASE_URL}/posts/${postId}/unsave`
        : `${process.env.REACT_APP_BASE_URL}/posts/${postId}/save`;
      const method = isCurrentlySaved ? 'delete' : 'post';
      await axios({
        method, url: endpoint,
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(prevPosts =>
        prevPosts.map(p =>
          p.id === postId ? { ...p, is_saved: !isCurrentlySaved } : p
        )
      );
    } catch (error) {
      console.error('Error saving/unsaving post:', error);
      alert('Failed to update save status. ' + (error.response?.data?.error || ''));
    }
  };

  const fetchComments = useCallback(async (postId) => {
    if (!postId) return;
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_comments/${postId}`);
      const commentsData = response.data;
      if (Array.isArray(commentsData)) {
        setComments(commentsData);
        const userIdsFromComments = new Set(commentsData.map(comment => comment.user_id));
        fetchUsersData(userIdsFromComments);
      } else {
        setComments([]);
      }
    } catch (error) {
      console.error("Error fetching comments:", error);
      setComments([]);
    }
  }, [fetchUsersData]);

  const handleCommentSubmit = async (postId) => {
    if (commentText.trim() === '' || !user) return;
    const token = Cookies.get('token');
    if (!token) { navigate('/login'); return; }

    const mentionIds = mentionedUsersInComment.map(u => u.id);

    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/add_comment`, {
        post_id: postId,
        comment_text: commentText,
        mentioned_user_ids: mentionIds,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCommentText('');
      setMentionedUsersInComment([]);
      setIsCommentingOnPostId(null); // Close comment input for this post
      fetchComments(postId); // Refresh comments for the modal if open
      fetchPosts(); // Refresh posts to update comment counts etc.
    } catch (error) {
      console.error('Error adding comment:', error);
      alert('Error adding comment. ' + (error.response?.data?.error || ''));
    }
  };
  
  const checkBalance = async () => {
    setCheckingBalance(true);

  if (!allowed || !user) {
    // Or a loading spinner, or null if login redirect is fast enough
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading...</div>;
  }

    try {
        const response = await axios.get(
            `${process.env.REACT_APP_BASE_URL}/check_balance/${user.id}`,
        );

        if (response.status === 200 && response.data?.balance !== undefined) {
            setMetaBalance(response.data.balance);
        } else {
            setMetaCoinMessage("Failed to retrieve MetaCoin balance.");
        }
    } catch (error) {
        const errMsg = error.response?.data?.error || "Error checking balance.";
        setMetaCoinMessage(errMsg);
    } finally {
        setCheckingBalance(false);
    }
};

console.log(user)
  return (
    <div>
      <div className="container">
        <div className="left-sidebar">
          <div className="sidebar-profile-box">
            <img src="assets/images/cover-pic.jpg" alt="cover" width="100%" style={{height:"100%"}}/>
            <div className="sidebar-profile-info">
              <img src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`} alt="profile" />
              <h1>{user.name}</h1>
              <h3>{user.role}</h3>
              <ul>
                <li>Profile views <span>0</span></li>
                <li>Post views <span>0</span></li>
                <li>Connections <span>0</span></li>
              </ul>
            </div>
            <div className="sidebar-profile-link">
              <a href="#"><img src="assets/images/items.svg" alt="items" />My Items</a>
              <a href="#" onClick={checkBalance} style={{ width: "60px", cursor: "pointer" }}>
                <img src="assets/images/metacoin.png" alt="metacoin" style={{ width: "50px"}} />
                  {checkingBalance ? "Checking..." : metaBalance !== null ? `Balance: ${metaBalance} MC` : "Check MetaCoin Balance"}
                </a>
            </div>
          </div>

          <div className={`sidebar-activity ${isActivityOpen ? 'open-activity' : ''}`} id="sidebarActivity">
            <h3>RECENT</h3>
            {/* Add actual recent activity links */}
            <a href="#"><img src="/assets/images/recent.svg" alt="recent" />Sample Activity</a>
            <h3>GROUPS</h3>
            {/* Add actual group links */}
            <a href="#"><img src="/assets/images/group.svg" alt="group" />Sample Group</a>
            <h3>HASHTAG</h3>
            {/* Add actual hashtag links */}
            <a href="#"><img src="/assets/images/hashtag.svg" alt="hashtag" />#sampletag</a>
            <div className="discover-more-link">
              <a href="#">Discover More</a>
            </div>
          </div>
          <p id="showMoreLink" onClick={() => setIsActivityOpen(!isActivityOpen)} style={{ cursor: 'pointer' }}>
            {isActivityOpen ? 'Show less' : 'Show more'} <b>{isActivityOpen ? '-' : '+'}</b>
          </p>
        </div>

        <div className="main-content">
          {/* Create Post Section - Prioritizing origin/Sadok for MentionInput */}
          <div className="create-post">
            <div className="create-post-input">
              <img
                src={user.profile_image ? constructMediaUrl(user.profile_image) : '/assets/images/default-avatar.png'}
                alt="profile"
                onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
              />
              <MentionInput
                value={text}
                onChange={setText} 
                onMentionsChange={setMentionedUsersInPost} 
                placeholder="Write Something..."
                className="create-post-textarea-wrapper" 
              />
            </div>
            {mentionedUsersInPost.length > 0 && (
                <div style={{ fontSize: '0.8em', color: '#555', padding: '5px 0', marginLeft: '50px' /* Align with input */ }}>
                    Tagging: {mentionedUsersInPost.map(u => `@${u.username}`).join(', ')}
                </div>
            )}
            <div className="create-post-links">
              {/* Using IDs from origin/Sadok for consistency if MentionInput is kept */}
              <li onClick={() => document.getElementById('home-image-upload')?.click()}>
                <img src="/assets/images/photo.svg" alt="photo" /> Photo
                <input type="file" id="home-image-upload" onChange={handleImageChange} accept="image/*" style={{ display: 'none' }} />
              </li>
              <li onClick={() => document.getElementById('home-video-upload')?.click()}>
                <img src="/assets/images/video.svg" alt="video" /> Video
                <input type="file" id="home-video-upload" onChange={handleVideoChange} accept="video/*" style={{ display: 'none' }} />
              </li>
              <li><img src="/assets/images/event.svg" alt="event" /> Event</li>
              <li onClick={handleSubmitPost} style={{ cursor: 'pointer' }}>Post</li>
            </div>
            {image && <div className="uploaded-files-preview"><img src={URL.createObjectURL(image)} alt="Preview" style={{ maxWidth: '150px', marginTop: '10px' }} /></div>}
            {video && <div className="uploaded-files-preview"><video controls src={URL.createObjectURL(video)} style={{ maxWidth: '150px', marginTop: '10px' }} /></div>}
          </div>

          {/* Sorting & Filtering - Using HEAD's more detailed UI, but ensure it works with origin/Sadok's post fetching if that's chosen */}
          <div className="sort-by">
            <hr />
            <p>
              Sort by :
              <select value={sortOption} onChange={handleSortChange}>
                <option value="date-desc">Newest</option>
                <option value="date-asc"> Oldest</option>
                <option value="popularity">Popularity</option>
              </select>
              
              &nbsp;&nbsp;Filter by type:
              <select value={filterType} onChange={handleFilterTypeChange}>
                <option value="all">All</option>
                <option value="text">Text</option>
                <option value="image">Image</option>
                <option value="video">Video</option>
              </select>
            </p>
          </div>

          {/* Display "No posts to show" message from origin/Sadok if posts array is empty */}
          {posts.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
              <p>No posts to show.</p>
              <p>Follow other users or create your own posts!</p>
            </div>
          )}

          {/* Posts List - Combining elements from both, prioritizing origin/Sadok for post structure and HEAD for comments modal */}
          {posts.map((post) => ( // Assuming 'posts' state is correctly populated by the unified fetchPosts
            // Using post.id || post.post_id from origin/Sadok for key
            <div key={post.id || post.post_id} className="post">
              <div className="post-author">
                <img
                  // Using origin/Sadok's user image logic with constructMediaUrl
                  src={users[post.user_id]?.profile_image ? constructMediaUrl(users[post.user_id].profile_image) : '/assets/images/default-avatar.png'}
                  alt={post.user_name || 'User'}
                  onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                />
                <div>
                  {/* Using Link from origin/Sadok */}
                  <Link to={`/profile/${post.username}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                    <h1>{post.user_name}</h1>
                  </Link>
                  <small>{getTimeAgo(post.created_at)}</small>
                </div>
                {/* Save button from origin/Sadok */}
                <button
                  onClick={() => handleSavePost(post.id || post.post_id, post.is_saved)}
                  className={`save-button ${post.is_saved ? 'saved' : ''}`}
                  style={{ marginLeft: 'auto', padding: '5px 10px', cursor: 'pointer', background: 'none', border: 'none', fontSize: '1.2em' }}
                  title={post.is_saved ? 'Unsave Post' : 'Save Post'}
                >
                  {post.is_saved ? '❤️' : '🤍'}
                </button>
              </div>

              {/* Content rendering - Using origin/Sadok's renderContentWithMentions */}
              {renderContentWithMentions(post.content, post.mentions)}

              {/* Image and Video display - Using origin/Sadok's structure with constructMediaUrl */}
              {post.image_url && <img src={constructMediaUrl(post.image_url)} alt="post content" style={{ width: '100%', marginTop: '10px', borderRadius: '4px' }} />}
              {post.video_url && (
                // If you keep CustomVideoPlayer from HEAD, ensure it's compatible.
                // Otherwise, use origin/Sadok's simpler video tag:
                <video autoPlay muted controls style={{ width: '100%', marginTop: '10px', borderRadius: '4px' }}>
                  <source src={constructMediaUrl(post.video_url)} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                // OR if CustomVideoPlayer is preferred and compatible:
                // <CustomVideoPlayer 
                //   videoUrl={constructMediaUrl(post.video_url)}
                //   postId={post.id || post.post_id}
                //   srtUrl={post.srt_url ? constructMediaUrl(post.srt_url) : undefined}
                // />
              )}
            
              <div className="post-stats">
                {/* Reactions display - from HEAD, assuming post object has like, love, etc. counts */}
                <div className="post-reactions">
                  {Object.entries({
                    "post-like": post.likes, // Ensure these fields (post.likes, post.loves) exist on the post object
                    love: post.loves,
                    clap: post.claps,
                    haha: post.laughs,
                    wow: post.wows,
                    angry: post.angrys,
                    sad: post.sads
                  })
                    .filter(([_, count]) => count > 0)
                    .map(([reaction, count]) => (
                      <div key={reaction} className="reaction">
                        <img
                          src={`/assets/images/${reaction}.png`} // Assuming assets are in public folder
                          alt={reaction}
                          className="post-reaction-icon"
                        />
                      </div>
                    ))}
                  <span className="total-reactions">
                    {Object.values({
                      "post-like": post.likes || 0,
                      love: post.loves || 0,
                      clap: post.claps || 0,
                      haha: post.laughs || 0,
                      wow: post.wows || 0,
                      angry: post.angrys || 0,
                      sad: post.sads || 0
                    }).reduce((acc, count) => acc + (count || 0), 0)} reactions
                  </span>
                </div>

                <div>
                  {/* Comments count and modal trigger - adapting HEAD's logic */}
                  <span
                    onClick={() => {
                      // Use selectedPostForComments from origin/Sadok if that's the state for the modal
                      setSelectedPostForComments(post); // or setSelectedPost(post) if using HEAD's state variable
                      setIsCommentsVisible(true);
                      fetchComments(post.id || post.post_id); 
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    {/* Use comments_count from origin/Sadok or post.comments.length from HEAD */}
                    {`${post.comments_count || (post.comments && post.comments.length) || 0} comments`}
                  </span>
                </div>
              </div>

              {/* Post Activity (Like, Comment buttons) - from origin/Sadok */}
              <div className="post-activity">
                <div>
                  <img
                    src={user.profile_image ? constructMediaUrl(user.profile_image) : '/assets/images/default-avatar.png'}
                    className="post-activity-user-icon" alt="user-icon"
                    onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                  />
                  {/* Removed down-arrow from HEAD as it wasn't in origin/Sadok here */}
                </div>
                <div className="reaction-container" 
                     onMouseEnter={() => setShowReactions(post.id || post.post_id)} 
                     onMouseLeave={() => setShowReactions(null)}>
                  <div className="post-activity-link" onClick={() => handleReaction(post.id || post.post_id, 'like') /* Default to 'like' or make it dynamic */}>
                    <img src="/assets/images/like.png" alt="like-icon" />
                    <span>Like</span>
                  </div>
                  {showReactions === (post.id || post.post_id) && (
                    <div className="reactions-bar">
                      {reactions.map((reaction) => ( // Ensure 'reactions' array is defined (from HEAD)
                        <img 
                            key={reaction.name} 
                            src={reaction.icon} // Ensure these icons are in /public/assets/images
                            alt={reaction.name} 
                            className="reaction-icon" 
                            onClick={() => handleReaction(post.id || post.post_id, reaction.name)} />
                      ))}
                    </div>
                  )}
                </div>
                <div className="post-activity-link" onClick={() => { setIsCommentingOnPostId(post.id || post.post_id); setCommentText(''); setMentionedUsersInComment([]); }}>
                  <img src="/assets/images/comment.png" alt="comment-icon" />
                  <span>Comment</span>
                </div>
                {/* Share and Send from HEAD can be added here if desired */}
                {/* 
                <div className="post-activity-link" onClick={() => console.log('Shared post')}>
                  <img src="/assets/images/share.png" alt="share-icon" />
                  <span>Share</span>
                </div>
                <div className="post-activity-link" onClick={() => console.log('Sent post')}>
                  <img src="/assets/images/send.png" alt="send-icon" />
                  <span>Send</span>
                </div>
                */}
              </div>
                
              {/* Comment Input - from origin/Sadok (inline with post) */}
              {isCommentingOnPostId === (post.id || post.post_id) && (
                <div className="comment-input-wrapper">
                  <MentionInput
                    value={commentText}
                    onChange={setCommentText}
                    onMentionsChange={setMentionedUsersInComment}
                    placeholder="Write a comment..."
                    className="comment-textarea-wrapper"
                  />
                 {mentionedUsersInComment.length > 0 && (
                    <div style={{ fontSize: '0.7em', color: '#555', padding: '3px 0' }}>
                        Tagging: {mentionedUsersInComment.map(u => `@${u.username}`).join(', ')}
                    </div>
                  )}
                  <button onClick={() => handleCommentSubmit(post.id || post.post_id)} className="comment-send-btn">
                    <img src="/assets/images/send-comment.png" alt="send" className="send-icon" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* Right Sidebar - Taking structure from origin/Sadok, content from HEAD where applicable */}
        <div className="right-sidebar">
          <RecommendationSidebar token={token} /> {/* From origin/Sadok */}
          <div className="sidebar-news">
            <img src="/assets/images/more.svg" className="info-icon" alt="more" />
            <h3>Trending News</h3>
            {/* Placeholder news items */}
            <a href="#">Sample News 1</a><span>1d ago</span>
            <a href="#">Sample News 2</a><span>2d ago</span>
            <a href="#" className="read-more-link">Read More</a>
          </div>
          <div className="sidebar-ad">
            <small>Ad &middot; &middot; &middot;</small>
            <p>Master Something</p>
            <div>
              <img
                src={user.profile_image ? constructMediaUrl(user.profile_image) : '/assets/images/default-avatar.png'}
                alt="user"
                onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
              />
              <img src="/assets/images/mi-logo.png" alt="ad logo" /> {/* Placeholder from origin/Sadok */}
            </div>
            <b>Some Ad Text Here</b>
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
            {/* Copyright from origin/Sadok */}
            <div className="copyright-msg">
              <img src="/assets/images/logo.png" alt="logo" />
              <p>MetaScout &#169; 2025. All Rights Reserved</p>
            </div>
          </div>
        </div>
      </div>

      {/* Comments Modal - from origin/Sadok (preferred if it handles mentions) or HEAD */}
      {/* This is the modal from origin/Sadok, which seems more integrated with mentions */}
      {isCommentsVisible && selectedPostForComments && (
        <div className="comments-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Comments on {selectedPostForComments.user_name}'s post</h3>
              <button className="modal-close" onClick={() => setIsCommentsVisible(false)}>✖</button>
            </div>
            <div className="modal-body">
              {comments.length === 0 ? <p>No comments yet.</p> : comments.map(comment => (
                <div key={comment.id || comment.comment_id} className="comment-item">
                  <img
                    src={users[comment.user_id]?.profile_image ? constructMediaUrl(users[comment.user_id].profile_image) : '/assets/images/default-avatar.png'}
                    alt={comment.user_name || 'User'}
                    className="comment-avatar"
                    onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                  />
                  <div className="comment-content">
                    <strong>{comment.user_name || "User"}</strong>
                    {renderContentWithMentions(comment.comment_text, comment.mentions)}
                  </div>
                  <div className="comment-meta">{getTimeAgo(comment.created_at)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {footer}
    </div>
  );
};