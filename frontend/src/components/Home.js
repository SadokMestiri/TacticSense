import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate, Link } from "react-router-dom";
import './Home.css';
import MentionInput from './MentionInput'; 

const Home = ({ header }) => {
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

  const [comments, setComments] = useState([]); // Comments for the selected post
  const [selectedPostForComments, setSelectedPostForComments] = useState(null); // Post whose comments are being viewed
  const [isCommentsVisible, setIsCommentsVisible] = useState(false); // Comments modal visibility

  const [commentText, setCommentText] = useState(''); // For new comment content
  const [mentionedUsersInComment, setMentionedUsersInComment] = useState([]); // Users mentioned in new comment
  const [isCommentingOnPostId, setIsCommentingOnPostId] = useState(null); // ID of post being commented on

  const [showReactions, setShowReactions] = useState(null); // ID of post whose reactions are shown
  const reactions = [
    { name: "like", icon: "assets/images/post-like.png" },
    { name: "love", icon: "assets/images/love.png" },
    { name: "laugh", icon: "assets/images/haha.png" },
    { name: "wow", icon: "assets/images/wow.png" },
    { name: "sad", icon: "assets/images/sad.png" },
    { name: "angry", icon: "assets/images/angry.png" },
  ];

  const [allowed, setAllowed] = useState(false);
  const [user, setUser] = useState(null); // Logged-in user details

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

  // Helper function to render content with mentions as links
  const renderContentWithMentions = (content, mentions) => {
    if (!content) return <p></p>;
    let processedContent = content;
    if (mentions && mentions.length > 0) {
      mentions.forEach(mention => {
        if (mention && mention.username) {
          const mentionTag = `@${mention.username}`;
          const regex = new RegExp(mentionTag.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![^<]*?>|[^<>]*?</\\w+>)', 'g');
          processedContent = processedContent.replace(regex, `<a href="/profile/${mention.username}" class="mention-link">${mentionTag}</a>`);
        }
      });
    }
    return <p dangerouslySetInnerHTML={{ __html: processedContent }} />;
  };

  const fetchUsersData = useCallback(async (userIds) => {
    const usersToFetch = Array.from(userIds).filter(id => !users[id] && id);
    if (usersToFetch.length === 0) return;

    try {
      // In a real app, you might have a batch endpoint, or fetch one by one
      for (const userId of usersToFetch) {
        const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${userId}`);
        if (response.data) {
          setUsers(prevUsers => ({
            ...prevUsers,
            [userId]: response.data, // Store the whole user object or specific fields
          }));
        }
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  }, [users]);


  const fetchPosts = useCallback(async () => {
    if (!allowed || !user) return;
    try {
      const token = Cookies.get('token');
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_posts`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const postsData = response.data;

      if (Array.isArray(postsData)) {
        setPosts(postsData);
        const userIdsFromPosts = new Set(postsData.map(post => post.user_id));
        fetchUsersData(userIdsFromPosts);
      } else {
        console.error("Error fetching posts: API did not return an array.", postsData);
        setPosts([]);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      if (error.response && error.response.status === 401) {
        Cookies.remove('token'); Cookies.remove('user'); navigate('/login');
      } else {
        setPosts([]);
      }
    }
  }, [allowed, user, navigate, fetchUsersData]);

  useEffect(() => {
    if (allowed && user) {
      fetchPosts();
    }
  }, [allowed, user, fetchPosts]);

  const handleTextChange = (e) => setText(e.target.value);
  const handleImageChange = (e) => setImage(e.target.files[0]);
  const handleVideoChange = (e) => setVideo(e.target.files[0]);

  const handleSubmitPost = async (e) => {
    e.preventDefault();
    if (!user || text.trim() === '') return;
    const token = Cookies.get('token');
    if (!token) { navigate('/login'); return; }

    const formData = new FormData();
    formData.append('text', text);
    if (image) formData.append('image', image);
    if (video) formData.append('video', video);

    const mentionIds = mentionedUsersInPost.map(u => u.id);
    formData.append('mentioned_user_ids', JSON.stringify(mentionIds));

    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/create_post`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`,
        },
      });
      setText(''); setImage(null); setVideo(null);
      setMentionedUsersInPost([]);
      fetchPosts();
    } catch (error) {
      console.error('Error creating post:', error);
      alert('There was an error creating the post. ' + (error.response?.data?.error || ''));
    }
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
      fetchPosts();
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

  if (!allowed || !user) {
    // Or a loading spinner, or null if login redirect is fast enough
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading...</div>;
  }

  return (
    <div>
      {header}
      <div className="container">
        <div className="left-sidebar">
          <div className="sidebar-profile-box">
            <img src="/assets/images/cover-pic.jpg" alt="cover" width="100%" />
            <div className="sidebar-profile-info">
              <img
                src={user.profile_image ? constructMediaUrl(user.profile_image) : '/assets/images/default-avatar.png'}
                alt="profile"
                onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
              />
              <h1>{user.name}</h1>
              <h3>@{user.username}</h3> {/* Or a bio field */}
              {/* Example stats, replace with actual data if available */}
              <ul>
                <li>Profile views <span>0</span></li>
                <li>Post views <span>0</span></li>
                <li>Connections <span>0</span></li>
              </ul>
            </div>
            <div className="sidebar-profile-link">
              <a href="#"><img src="/assets/images/items.svg" alt="items" />My Items</a>
              <a href="#"><img src="/assets/images/premium.png" alt="premium" />Try Premium</a>
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

          <div className="sort-by">
            <hr />
            <p>Sort by : <span>top <img src="/assets/images/down-arrow.png" alt="down-arrow" /></span> </p>
          </div>

          {posts.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
              <p>No posts to show.</p>
              <p>Follow other users or create your own posts!</p>
            </div>
          )}

          {posts.map((post) => (
            <div key={post.id || post.post_id} className="post">
              <div className="post-author">
                <img
                  src={users[post.user_id]?.profile_image ? constructMediaUrl(users[post.user_id].profile_image) : '/assets/images/default-avatar.png'}
                  alt={post.user_name || 'User'}
                  onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                />
                <div>
                  <Link to={`/profile/${post.username}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                    <h1>{post.user_name}</h1>
                  </Link>
                  <small>{getTimeAgo(post.created_at)}</small>
                </div>
                <button
                  onClick={() => handleSavePost(post.id || post.post_id, post.is_saved)}
                  className={`save-button ${post.is_saved ? 'saved' : ''}`}
                  style={{ marginLeft: 'auto', padding: '5px 10px', cursor: 'pointer', background: 'none', border: 'none', fontSize: '1.2em' }}
                  title={post.is_saved ? 'Unsave Post' : 'Save Post'}
                >
                  {post.is_saved ? '❤️' : '🤍'}
                </button>
              </div>
              {renderContentWithMentions(post.content, post.mentions)}
              {post.image_url && <img src={constructMediaUrl(post.image_url)} alt="post content" style={{ width: '100%', marginTop: '10px', borderRadius: '4px' }} />}
              {post.video_url && <video autoPlay muted controls style={{ width: '100%', marginTop: '10px', borderRadius: '4px' }}><source src={constructMediaUrl(post.video_url)} type="video/mp4" />Your browser does not support the video tag.</video>}

              <div className="post-stats">
                <div>
                  <span>
                    {Object.values({ like: post.likes, love: post.loves, laugh: post.laughs, wow: post.wows, angry: post.angrys, sad: post.sads })
                      .reduce((acc, count) => acc + (count || 0), 0)} reactions
                  </span>
                </div>
                <div>
                  <span onClick={() => { setSelectedPostForComments(post); setIsCommentsVisible(true); fetchComments(post.id || post.post_id); }} style={{ cursor: 'pointer' }}>
                    {`${post.comments_count || 0} comments`}
                  </span>
                </div>
              </div>

              <div className="post-activity">
                <div>
                  <img
                    src={user.profile_image ? constructMediaUrl(user.profile_image) : '/assets/images/default-avatar.png'}
                    className="post-activity-user-icon" alt="user-icon"
                    onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                  />
                </div>
                <div className="reaction-container" onMouseEnter={() => setShowReactions(post.id || post.post_id)} onMouseLeave={() => setShowReactions(null)}>
                  <div className="post-activity-link"><img src="/assets/images/like.png" alt="like-icon" /><span>Like</span></div>
                  {showReactions === (post.id || post.post_id) && (
                    <div className="reactions-bar">
                      {reactions.map((reaction) => (
                        <img key={reaction.name} src={reaction.icon} alt={reaction.name} className="reaction-icon" onClick={() => handleReaction(post.id || post.post_id, reaction.name)} />
                      ))}
                    </div>
                  )}
                </div>
                <div className="post-activity-link" onClick={() => { setIsCommentingOnPostId(post.id || post.post_id); setCommentText(''); setMentionedUsersInComment([]); }}>
                  <img src="/assets/images/comment.png" alt="comment-icon" /><span>Comment</span>
                </div>
                {/* Add Share and Send functionality if needed */}
              </div>

              {isCommentingOnPostId === (post.id || post.post_id) && (
                <div className="comment-input-wrapper">
                  <MentionInput
                    value={commentText}
                    onChange={setCommentText} // Passes the raw text back
                    onMentionsChange={setMentionedUsersInComment} // Passes selected user objects
                    placeholder="Write a comment..."
                    className="comment-textarea-wrapper" // Optional: for styling
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

        <div className="right-sidebar">
          <div className="sidebar-news">
            <img src="/assets/images/more.svg" className="info-icon" alt="more" />
            <h3>Trending News</h3>
            {/* Replace with dynamic news items */}
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
              <img src="/assets/images/mi-logo.png" alt="ad logo" /> {/* Placeholder */}
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
            <div className="copyright-msg">
              <img src="/assets/images/logo.png" alt="logo" />
              <p>MetaScout &#169; 2025. All Rights Reserved</p>
            </div>
          </div>
        </div>
      </div>

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
    </div>
  );
};

export default Home;