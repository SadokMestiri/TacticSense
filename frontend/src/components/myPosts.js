import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useNavigate, useParams, Link } from "react-router-dom";
import './Home.css'; // Assuming common styles are here
import './UserListModal.css'; // Styles for the new modal
import './Profile.css'; // Create or use an existing CSS file for profile specific styles
import MentionInput from './MentionInput'; // Add this import

const MyPosts = () => {
  const navigate = useNavigate();
  const { username: profileUsername } = useParams(); // Get username from URL

  const [profileUser, setProfileUser] = useState(null); // User whose profile is being viewed
  const [loggedInUser, setLoggedInUser] = useState(null); // Currently logged-in user
  
  const [followersCount, setFollowersCount] = useState(0);
  const [followingCount, setFollowingCount] = useState(0);
  const [myPosts, setMyPosts] = useState([]);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // States for follow functionality
  const [isFollowing, setIsFollowing] = useState(false);
  const [followInProgress, setFollowInProgress] = useState(false);

  // States for post creation
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [video, setVideo] = useState(null);
  const [mentionedUsersInPost, setMentionedUsersInPost] = useState([]); // For new post

  // States for comments and reactions
  const [comments, setComments] = useState([]);
  const [selectedPostForComments, setSelectedPostForComments] = useState(null);
  const [isCommentsVisible, setIsCommentsVisible] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [mentionedUsersInComment, setMentionedUsersInComment] = useState([]); 
  const [isCommentingOnPost, setIsCommentingOnPost] = useState(null); // Stores post ID
  const [showReactions, setShowReactions] = useState(null); // Stores post ID
  const reactions = [
    { name: "like", icon: "assets/images/post-like.png" },
    { name: "love", icon: "assets/images/love.png" },
    { name: "laugh", icon: "assets/images/haha.png" },
    { name: "wow", icon: "assets/images/wow.png" },
    { name: "sad", icon: "assets/images/sad.png" },
    { name: "angry", icon: "assets/images/angry.png" },
  ];

  // State for user list modal (followers/following)
  const [isUserListModalVisible, setIsUserListModalVisible] = useState(false);
  const [userList, setUserList] = useState([]);
  const [userListTitle, setUserListTitle] = useState('');
  const [isUserListLoading, setIsUserListLoading] = useState(false);

  // Get loggedInUser from cookies
  useEffect(() => {
    const userCookie = Cookies.get('user');
    if (userCookie) {
      try {
        const parsedUser = JSON.parse(userCookie);
        setLoggedInUser(parsedUser);
      } catch (e) {
        console.error("Failed to parse user cookie:", e);
        Cookies.remove('user');
        Cookies.remove('token');
        navigate('/login');
      }
    } else {
      navigate('/login');
    }
  }, [navigate]);

  // Helper function to render content with mentions as links
  const renderContentWithMentions = (content, mentions) => {
    if (!content) return <p></p>; // Return empty paragraph or null if content is empty
    let processedContent = content;
    if (mentions && mentions.length > 0) {
        mentions.forEach(mention => {
            if (mention && mention.username) {
                const mentionTag = `@${mention.username}`;
                // Regex to match @username not inside an HTML tag
                const regex = new RegExp(mentionTag.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![^<]*?>|[^<>]*?</\\w+>)', 'g');
                processedContent = processedContent.replace(regex, `<a href="/profile/${mention.username}" class="mention-link">${mentionTag}</a>`);
            }
        });
    }
    return <p dangerouslySetInnerHTML={{ __html: processedContent }} />;
  };

  // Fetch profile user data based on username from URL
  useEffect(() => {
    if (!profileUsername) return;
    
    setIsLoading(true);
    setError(null);
    setProfileUser(null);
    setMyPosts([]);
    setFollowersCount(0);
    setFollowingCount(0);
    setIsFollowing(false);

    const fetchProfileData = async () => {
      try {
        const userRes = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/username/${profileUsername}`);
        if (!userRes.data) {
            throw new Error(`User "${profileUsername}" not found.`);
        }
        const fetchedProfileUser = userRes.data;
        setProfileUser(fetchedProfileUser);

        if (!fetchedProfileUser || !fetchedProfileUser.id) {
            setError("User data not available for profile.");
            setIsLoading(false);
            return;
        }

        const followersRes = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${fetchedProfileUser.id}/followers`);
        setFollowersCount(followersRes.data.length);

        const followingRes = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${fetchedProfileUser.id}/following`);
        setFollowingCount(followingRes.data.length);

        const token = Cookies.get('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const postsRes = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${fetchedProfileUser.id}/posts`, { headers });
        
        const userPosts = postsRes.data.map(p => ({
          ...p, 
          user_name: fetchedProfileUser.name,
          user_profile_image: fetchedProfileUser.profile_image,
          username: fetchedProfileUser.username
        }));
        setMyPosts(userPosts);

      } catch (err) {
        console.error("Error fetching profile data:", err);
        if (err.response && err.response.status === 404) {
            setError(`User "${profileUsername}" not found.`);
        } else {
            setError("Failed to load profile data. Please try again.");
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfileData();
    
  }, [profileUsername, navigate]);

  // Effect to check follow status
  useEffect(() => {
    const checkFollowingStatus = async () => {
      if (loggedInUser && profileUser && loggedInUser.id !== profileUser.id) {
        setFollowInProgress(true);
        try {
          const token = Cookies.get('token');
          const response = await axios.get(
            `${process.env.REACT_APP_BASE_URL}/users/${profileUser.id}/is-following`,
            { headers: { Authorization: `Bearer ${token}` } }
          );
          setIsFollowing(response.data.is_following);
        } catch (error) {
          console.error("Error fetching follow status:", error);
          setIsFollowing(false);
        } finally {
          setFollowInProgress(false);
        }
      } else {
        setIsFollowing(false); 
      }
    };

    if (profileUser && loggedInUser) {
      checkFollowingStatus();
    }
  }, [loggedInUser, profileUser]);


  const handleFollowToggle = async () => {
    if (!loggedInUser || !profileUser || loggedInUser.id === profileUser.id || followInProgress) {
      return;
    }
    setFollowInProgress(true);
    const token = Cookies.get('token');
    const headers = { Authorization: `Bearer ${token}` };
    const action = isFollowing ? 'unfollow' : 'follow';
    const url = `${process.env.REACT_APP_BASE_URL}/users/${profileUser.id}/${action}`;

    try {
      await axios.post(url, {}, { headers });
      setIsFollowing(!isFollowing);
      setFollowersCount(prevCount => action === 'follow' ? prevCount + 1 : Math.max(0, prevCount - 1));
    } catch (error) {
      console.error(`Error ${action}ing user:`, error);
      alert(`Could not ${action} user. Please try again.`);
    } finally {
      setFollowInProgress(false);
    }
  };

  const handleShowFollowers = async () => {
    if (!profileUser || !profileUser.id) return;
    setIsUserListLoading(true);
    setUserListTitle('Followers');
    setIsUserListModalVisible(true);
    try {
      const res = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${profileUser.id}/followers`);
      setUserList(res.data);
    } catch (err) {
      console.error("Error fetching followers list:", err);
      setUserList([]);
    } finally {
      setIsUserListLoading(false);
    }
  };

  const handleShowFollowing = async () => {
    if (!profileUser || !profileUser.id) return;
    setIsUserListLoading(true);
    setUserListTitle('Following');
    setIsUserListModalVisible(true);
    try {
      const res = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${profileUser.id}/following`);
      setUserList(res.data);
    } catch (err) {
      console.error("Error fetching following list:", err);
      setUserList([]);
    } finally {
      setIsUserListLoading(false);
    }
  };
  
  const closeUserListModal = () => {
    setIsUserListModalVisible(false);
    setUserList([]);
    setUserListTitle('');
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

  const fetchPostsAgain = useCallback(async () => {
    if (!profileUser || !profileUser.id) return;
    const token = Cookies.get('token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    try {
        const postsRes = await axios.get(`${process.env.REACT_APP_BASE_URL}/users/${profileUser.id}/posts`, { headers });
        const userPosts = postsRes.data.map(p => ({
                ...p, 
                user_name: profileUser.name, 
                user_profile_image: profileUser.profile_image,
                username: profileUser.username
            }));
        setMyPosts(userPosts);
    } catch (error) {
        console.error("Error refetching posts for profile:", error);
    }
  }, [profileUser]);

  const handleReaction = async (postId, reactionType) => {
    if (!loggedInUser) return;
    const token = Cookies.get('token');
    if (!token) { navigate('/login'); return; }
    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/react_to_post`, {
        // user_id: loggedInUser.id, // Backend uses token
        post_id: postId,
        reaction_type: reactionType,
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchPostsAgain();
    } catch (error) {
      console.error('Error adding reaction:', error);
      alert('Failed to react to post. ' + (error.response?.data?.error || ''));
    }
  };

  const handleCommentSubmit = async (postId) => {
    if (commentText.trim() === '' || !loggedInUser) return;
    const token = Cookies.get('token');
    if (!token) { navigate('/login'); return; }

    const mentionIds = mentionedUsersInComment.map(user => user.id);

    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/add_comment`, {
        post_id: postId,
        // user_id: loggedInUser.id, // Backend uses token
        comment_text: commentText,
        mentioned_user_ids: mentionIds,
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setCommentText('');
      setMentionedUsersInComment([]);
      setIsCommentingOnPost(null);
      fetchComments(postId);
      fetchPostsAgain(); // To update comment count on the post
    } catch (error) {
      console.error('Error adding comment:', error);
      alert('Failed to add comment. ' + (error.response?.data?.error || ''));
    }
  };
  
  const fetchComments = async (postId) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_comments/${postId}`);
      // Assuming get_comments already returns user details with each comment
      setComments(response.data);
    } catch (error) {
      console.error("Error fetching comments:", error);
      setComments([]);
    }
  };

  const handleSavePost = async (postId, isCurrentlySaved) => {
    if (!loggedInUser) { navigate('/login'); return; }
    const token = Cookies.get('token');
    try {
      const endpoint = isCurrentlySaved 
        ? `${process.env.REACT_APP_BASE_URL}/posts/${postId}/unsave`
        : `${process.env.REACT_APP_BASE_URL}/posts/${postId}/save`;
      const method = isCurrentlySaved ? 'delete' : 'post';
      await axios({ method, url: endpoint, headers: { 'Authorization': `Bearer ${token}` } });
      setMyPosts(prevPosts => 
        prevPosts.map(p => 
          p.id === postId ? { ...p, is_saved: !isCurrentlySaved } : p
        )
      );
    } catch (error) {
      console.error('Error saving/unsaving post:', error);
      alert('Failed to save/unsave post. ' + (error.response?.data?.error || ''));
    }
  };

  const handleTextChange = (e) => setText(e.target.value);
  const handleImageChange = (e) => setImage(e.target.files[0]);
  const handleVideoChange = (e) => setVideo(e.target.files[0]);

  const handleSubmitPost = async (e) => {
    e.preventDefault();
    if (!loggedInUser || text.trim() === '') return;
    const token = Cookies.get('token');
    if (!token) { navigate('/login'); return; }

    const formData = new FormData();
    // formData.append('user_id', loggedInUser.id); // Backend uses token
    formData.append('text', text);
    if (image) formData.append('image', image);
    if (video) formData.append('video', video);

    const mentionIds = mentionedUsersInPost.map(user => user.id);
    formData.append('mentioned_user_ids', JSON.stringify(mentionIds));

    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/create_post`, formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}` 
        },
      });
      setText(''); setImage(null); setVideo(null);
      setMentionedUsersInPost([]);
      fetchPostsAgain();
    } catch (error) {
      console.error('Error creating post:', error);
      alert('There was an error creating the post. ' + (error.response?.data?.error || ''));
    }
  };

  if (isLoading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading profile...</div>;
  if (error) return <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>Error: {error}</div>;
  if (!profileUser) return <div style={{ textAlign: 'center', marginTop: '50px' }}>User not found.</div>;
  
  const isMyProfile = loggedInUser && profileUser && loggedInUser.id === profileUser.id;

  const constructMediaUrl = (urlPath) => {
    if (!urlPath) return '';
    if (urlPath.startsWith('http://') || urlPath.startsWith('https://')) {
        return urlPath; // Already a full URL
    }
    return `${process.env.REACT_APP_BASE_URL}${urlPath.startsWith('/') ? '' : '/'}${urlPath}`;
  };

  // TODO: Implement UI for selecting users to mention (e.g., a dropdown when typing @)
  // For now, mentionedUsersInPost and mentionedUsersInComment would be populated by such a UI.

  return (
    <div>
      
      <div className="container">
        <div className="left-sidebar">
          <div className="sidebar-profile-box">
            <img src="/assets/images/cover-pic.jpg" alt="cover" width="100%" />
            <div className="sidebar-profile-info">
              <img 
                src={profileUser.profile_image ? constructMediaUrl(profileUser.profile_image) : '/assets/images/default-avatar.png'} 
                alt="profile" 
                onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
              />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px', width: '100%' }}>
                <h1 style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0 }}>
                  {profileUser.name}
                </h1>
                {!isMyProfile && loggedInUser && profileUser && (
                  <button
                    onClick={handleFollowToggle}
                    disabled={followInProgress}
                    style={{
                      padding: '6px 12px',
                      cursor: 'pointer',
                      backgroundColor: isFollowing ? '#6c757d' : '#007bff', 
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '0.9rem',
                      fontWeight: 'bold',
                      whiteSpace: 'nowrap',
                      flexShrink: 0 
                    }}
                  >
                    {followInProgress ? '...' : (isFollowing ? 'Unfollow' : 'Follow')}
                  </button>
                )}
              </div>
              <h3>@{profileUser.username}</h3>
              <ul>
                <li onClick={handleShowFollowers} style={{cursor: 'pointer', userSelect: 'none'}}>Followers <span>{followersCount}</span></li>
                <li onClick={handleShowFollowing} style={{cursor: 'pointer', userSelect: 'none'}}>Following <span>{followingCount}</span></li>
                <li>Posts <span>{myPosts.length}</span></li>

              </ul>
            </div>
          </div>
        </div>
        <div className="main-content">
          {isMyProfile && loggedInUser && (
            <div className="create-post">
              <div className="create-post-input">
                <img 
                  src={loggedInUser.profile_image ? constructMediaUrl(loggedInUser.profile_image) : '/assets/images/default-avatar.png'} 
                  alt="profile" 
                  onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                />
                <MentionInput
                  value={text}
                  onChange={setText}
                  onMentionsChange={setMentionedUsersInPost}
                  placeholder="Write Something..."
                  className="create-post-textarea-wrapper" // Optional
                />
              </div>
              {/* Placeholder for mention selection UI */}
              {/* <div>Selected mentions for post: {mentionedUsersInPost.map(u => u.username).join(', ')}</div> */}
              <div className="create-post-links">
                {mentionedUsersInPost.length > 0 && (
                  <div style={{ fontSize: '0.8em', color: '#555', padding: '5px 0' }}>
                      Tagging: {mentionedUsersInPost.map(u => `@${u.username}`).join(', ')}
                  </div>
                )}
                <li onClick={() => document.getElementById('profile-image-upload')?.click()}>
                  <img src="/assets/images/photo.svg" alt="photo" /> Photo
                  <input type="file" id="profile-image-upload" onChange={handleImageChange} accept="image/*" style={{ display: 'none' }} />
                </li>
                <li onClick={() => document.getElementById('profile-video-upload')?.click()}>
                  <img src="/assets/images/video.svg" alt="video" /> Video
                  <input type="file" id="profile-video-upload" onChange={handleVideoChange} accept="video/*" style={{ display: 'none' }} />
                </li>
                <li><img src="/assets/images/event.svg" alt="event" /> Event</li>
                <li onClick={handleSubmitPost} style={{cursor: 'pointer'}}>Post</li>
              </div>
                {image && <div className="uploaded-files-preview"><img src={URL.createObjectURL(image)} alt="Uploaded Preview" style={{ maxWidth: '150px', marginTop: '10px' }} /></div>}
                {video && <div className="uploaded-files-preview"><video controls src={URL.createObjectURL(video)} style={{ maxWidth: '150px', marginTop: '10px' }} /></div>}
            </div>
          )}
          <div className="sort-by">
            <hr />
            <p>Sort by : <span>top <img src="/assets/images/down-arrow.png" alt="down-arrow" /></span> </p>
          </div>
          {myPosts.length === 0 && <p style={{textAlign: 'center', marginTop: '20px'}}>No posts yet.</p>}

          {myPosts.map((post) => (
            <div key={post.id || post.post_id} className="post">
              <div className="post-author">
                <img 
                  src={post.user_profile_image ? constructMediaUrl(post.user_profile_image) : '/assets/images/default-avatar.png'} 
                  alt="user" 
                  onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                />
                <div>
                  <Link to={`/profile/${post.username}`} style={{textDecoration: 'none', color: 'inherit'}}>
                     <h1>{post.user_name}</h1>
                  </Link>
                  <small>{getTimeAgo(post.created_at)}</small>
                </div>
                {loggedInUser && (
                    <button 
                        onClick={() => handleSavePost(post.id || post.post_id, post.is_saved)}
                        className={`save-button ${post.is_saved ? 'saved' : ''}`}
                        style={{ marginLeft: 'auto', padding: '5px 10px', cursor: 'pointer', background: 'none', border: 'none', fontSize: '1.2em' }}
                        title={post.is_saved ? 'Unsave Post' : 'Save Post'}
                    >
                        {post.is_saved ? '❤️' : '🤍'}
                    </button>
                )}
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
                {loggedInUser && (
                <div>
                  <img src={loggedInUser.profile_image ? constructMediaUrl(loggedInUser.profile_image) : '/assets/images/default-avatar.png'} className="post-activity-user-icon" alt="user-icon" onError={(e) => e.target.src = '/assets/images/default-avatar.png'} />
                </div>
                )}
                <div className="reaction-container" onMouseEnter={() => setShowReactions(post.id || post.post_id)} onMouseLeave={() => setShowReactions(null)}>
                  <div className="post-activity-link"><img src="/assets/images/like.png" alt="like-icon" /><span>Like</span></div>
                  {showReactions === (post.id || post.post_id) && (
                    <div className="reactions-bar">
                      {reactions.map((reaction) => (
                        <img key={reaction.name} src={`/assets/images/${reaction.name}.png`} alt={reaction.name} className="reaction-icon" onClick={() => handleReaction(post.id || post.post_id, reaction.name)} />
                      ))}
                    </div>
                  )}
                </div>
                <div className="post-activity-link" onClick={() => { setIsCommentingOnPost(post.id || post.post_id); setCommentText(''); setMentionedUsersInComment([]); }}>
                  <img src="/assets/images/comment.png" alt="comment-icon" /><span>Comment</span>
                </div>
              </div>
              {isCommentingOnPost === (post.id || post.post_id) && (
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

        <div className="right-sidebar">
          <div className="sidebar-news">
            <img src="/assets/images/more.svg" className="info-icon" alt="more" />
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
            <small>Ad &middot; &middot; &middot;</small>
            <p>Master Web Development</p>
            <div>
              <img 
                src={loggedInUser?.profile_image ? constructMediaUrl(loggedInUser.profile_image) : '/assets/images/default-avatar.png'}  
                alt="user" 
                onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
              />
              <img src="/assets/images/mi-logo.png" alt="mi logo" />
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
              <h3>Comments on {selectedPostForComments.user_name || (profileUser && profileUser.name)}'s post</h3>
              <button className="modal-close" onClick={() => setIsCommentsVisible(false)}>✖</button>
            </div>
            <div className="modal-body">
              {comments.length === 0 ? <p>No comments yet.</p> : comments.map(comment => (
                <div key={comment.id || comment.comment_id} className="comment-item">
                  <img src={comment.user_profile_image ? constructMediaUrl(comment.user_profile_image) : '/assets/images/default-avatar.png'} alt="User" className="comment-avatar" onError={(e) => e.target.src = '/assets/images/default-avatar.png'}/>
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

      {isUserListModalVisible && (
        <div className="user-list-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{userListTitle}</h3>
              <button className="modal-close" onClick={closeUserListModal}>✖</button>
            </div>
            <div className="modal-body">
              {isUserListLoading ? (
                <p style={{textAlign: 'center'}}>Loading...</p>
              ) : userList.length === 0 ? (
                <p style={{textAlign: 'center'}}>No users to display.</p>
              ) : (
                <ul className="user-list-items">
                  {userList.map(user => (
                    <li key={user.id} className="user-list-item">
                      <Link to={`/profile/${user.username}`} onClick={closeUserListModal} className="user-list-link">
                        <img 
                          src={user.profile_image ? constructMediaUrl(user.profile_image) : '/assets/images/default-avatar.png'} 
                          alt={user.name} 
                          className="user-list-avatar"
                          onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                        />
                        <div className="user-list-info">
                          <span className="user-list-name">{user.name}</span>
                          <span className="user-list-username">@{user.username}</span>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}

  </div>
  );
};

export default MyPosts;