import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Home.css';
import Notifications from './Notifications';

const Home = ({ header, footer }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isActivityOpen, setIsActivityOpen] = useState(false);
  const [posts, setPosts] = useState([]);
  const user_id = localStorage.getItem('user_id');
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [video, setVideo] = useState(null);
  const [user, setUser] = useState({});
  const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);
  const [comments, setComments] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null); // For managing the selected post
  const [isCommentsVisible, setIsCommentsVisible] = useState(false); // To control visibility of the comments popup

  const [showReactions, setShowReactions] = useState(null);
  const reactions = [
    { name: "like", icon: "assets/images/post-like.png" },
    { name: "love", icon: "assets/images/love.png" },
    { name: "laugh", icon: "assets/images/haha.png" },
    { name: "wow", icon: "assets/images/wow.png" },
    { name: "sad", icon: "assets/images/sad.png" },
    { name: "angry", icon: "assets/images/angry.png" },
  ];

  const [sortOption, setSortOption] = useState('date-desc'); // 'date-desc', 'date-asc', 'popularity'
  const [filterType, setFilterType] = useState('all'); // 'all', 'text', 'image', 'video'
  const [allPosts, setAllPosts] = useState([]);

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

  // Handle comment input change
  const handleCommentChange = (event) => {
    setComment(event.target.value);
  };

  // Handle submitting the comment
  const handleCommentSubmit = async (postId) => {
    if (comment.trim() === '') return; // Don't submit empty comments

    try {
      // Send the comment to the backend via the /add_comment API
      const response = await axios.post(`${process.env.REACT_APP_BASE_URL}/add_comment`, {
        post_id: postId,  // Send the post_id in the request body
        user_id: user.id, // Pass the current user's ID
        comment_text: comment, // The actual comment content
        created_at: new Date().toISOString(), // Optional: Use the current timestamp
      });

      // Check if the response is successful (status code 200)
      if (response.status === 200) {
        console.log('Comment added:', response.data.message); // Assuming response has a message
        setComment(''); // Clear the input field
        setIsCommenting(false); // Close the input field after submission
      } else {
        console.error('Error adding comment:', response.data.message || 'Unknown error');
      }
    } catch (error) {
      console.error('Network error:', error);
    }
  };


  const fetchUsers = async (user_id) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${user_id}`);

      setUsers(prevUsers => ({
        ...prevUsers,
        [user_id]: response.data.profile_image
      }));
    } catch (error) {
      setError(error.response?.data?.message || 'Error fetching user data');
    }
  };
  const fetchUser = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${user_id}`);

      setUser(response.data);
    } catch (error) {
      setError(error.response?.data?.message || 'Error fetching user data');
    }
  };
  useEffect(() => {
    fetchUser();
  }, [user_id]);

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
    console.log('Selected image:', e.target.files[0]);
  };

  const handleVideoChange = (e) => {
    setVideo(e.target.files[0]);
    console.log('Selected video:', e.target.files[0]);
  };

  const handleSubmitPost = async (e) => {
    e.preventDefault();
    console.log('Submitting post with text:', text);

    const formData = new FormData();
    formData.append('user_id', user_id);
    formData.append('text', text);
    if (image) {
      formData.append('image', image);
    }
    if (video) {
      formData.append('video', video);
    }

    try {
      const response = await axios.post(`${process.env.REACT_APP_BASE_URL}/create_post`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Post created successfully:', response.data);
      alert('Post created successfully');
      setImage(null);
      setVideo(null);
      setText('');
      fetchPosts();
    } catch (error) {
      console.error('Error creating post:', error);
      alert('There was an error creating the post');
    }
  };

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

  const fetchPosts = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_posts`);
      let postsData = response.data;

      for (let post of postsData) {
        if (post.user_id) {
          await fetchUsers(post.user_id);
        }
      }

      postsData = sortPosts(postsData, sortOption);
      setAllPosts(postsData);
      setPosts(postsData);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
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
    try {
      const response = await axios.post(`${process.env.REACT_APP_BASE_URL}/react_to_post`, {
        user_id,
        post_id: postId,
        reaction_type: reactionType,
      });

      console.log(`Reaction (${reactionType}) added:`, response.data);
      fetchPosts(); // Refresh posts to update reactions count
    } catch (error) {
      console.error('Error adding reaction:', error);
      alert('There was an error reacting to the post');
    }
  };

  const fetchComments = async (postId) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_comments/${postId}`);
      const commentsData = response.data;
      for (let comment of commentsData) {
        if (comment.user_id) {
          await fetchUsers(comment.user_id);
        }
        setComments(commentsData);

      }
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  };


  return (
    <div>
      {header}

      <div className="container">
        <div className="left-sidebar">
          <div className="sidebar-profile-box">
            <img src="assets/images/cover-pic.jpg" alt="cover" width="100%" />
            <div className="sidebar-profile-info">
              <img src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`} alt="profile" />
              <h1>{user.name}</h1>
              <h3>{user.role}</h3>
              <ul>
                <li>Your profile views <span>24K</span></li>
                <li>Your post views <span>128K</span></li>
                <li>Your Connections <span>108K</span></li>
              </ul>
            </div>
            <div className="sidebar-profile-link">
              <a href="#"><img src="assets/images/items.svg" alt="items" />My Items</a>
              <a href="#"><img src="assets/images/premium.png" alt="premium" />Try Premium</a>
            </div>
          </div>

          {/* Activity */}
          <div className={`sidebar-activity ${isActivityOpen ? 'open-activity' : ''}`} id="sidebarActivity">
            <h3>RECENT</h3>
            <a href="#"><img src="assets/images/recent.svg" alt="recent" />Data Analysis</a>
            <a href="#"><img src="assets/images/recent.svg" alt="recent" />UI UX Design</a>
            <a href="#"><img src="assets/images/recent.svg" alt="recent" />Web Development</a>
            <a href="#"><img src="assets/images/recent.svg" alt="recent" />Object Oriented Programming</a>
            <a href="#"><img src="assets/images/recent.svg" alt="recent" />Operating Systems</a>
            <a href="#"><img src="assets/images/recent.svg" alt="recent" />Platform technologies</a>

            <h3>GROUPS</h3>
            <a href="#"><img src="assets/images/group.svg" alt="group" />Data Analyst group</a>
            <a href="#"><img src="assets/images/group.svg" alt="group" />Learn NumPy</a>
            <a href="#"><img src="assets/images/group.svg" alt="group" />Machine Learning group</a>
            <a href="#"><img src="assets/images/group.svg" alt="group" />Data Science Aspirants</a>

            <h3>HASHTAG</h3>
            <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />dataanalyst</a>
            <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />numpy</a>
            <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />machinelearning</a>
            <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />datascience</a>

            <div className="discover-more-link">
              <a href="#">Discover More</a>
            </div>
          </div>

          <p id="showMoreLink" >Show more <b>+</b></p>
        </div>

        <div className="main-content">
          {/* Create Post Section */}
          <div className="create-post">
            <div className="create-post-input">
              <img src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`} alt="profile" />
              <textarea rows="2" placeholder="Write Something"
                value={text}
                onChange={handleTextChange}
              ></textarea>
            </div>
            <div className="create-post-links">
              <li onClick={() => document.getElementById('image-upload').click()} >
                <img src="assets/images/photo.svg" alt="photo" /> Photo
                <input
                  type="file"
                  id="image-upload"
                  className="file-upload-input"
                  onChange={handleImageChange}
                  accept="image/*"
                  multiple
                  style={{ display: 'none' }}
                />
              </li>

              <li onClick={() => document.getElementById('video-upload').click()}>
                <img src="assets/images/video.svg" alt="video" /> Video
                <input
                  type="file"
                  id="video-upload"
                  className="file-upload-input"
                  onChange={handleVideoChange}
                  accept="video/*"
                  multiple
                  style={{ display: 'none' }}
                />
              </li>
              <li><img src="assets/images/event.svg" alt="event" /> Event</li>
              <li onClick={handleSubmitPost}>Post</li>
            </div>

            {image && (
              <div className="uploaded-files-preview">
                <img
                  src={URL.createObjectURL(image)}
                  alt="Uploaded"
                  style={{ maxWidth: '150px', marginTop: '10px' }}
                />

              </div>
            )}

            {video && (
              <div className="uploaded-files-preview">
                <video
                  controls
                  src={URL.createObjectURL(video)}
                  style={{ maxWidth: '150px', marginTop: '10px' }}
                />

              </div>
            )}
          </div>


          {/* Sorting & Filtering */}
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

          {/* Posts */}
          {posts.map((post, index) => (
            <div key={index} className="post">
              <div className="post-author">
                <img src={`${process.env.REACT_APP_BASE_URL}/${users[post.user_id]}`} alt="user" />
                <div>
                  <h1>{post.user_name}</h1>
                  {/* <small>{post.title}</small>*/}
                  <small>{getTimeAgo(post.created_at)}</small>
                </div>
              </div>
              <p>{post.content}</p>
              {post.image_url && (
                <img
                  src={`${process.env.REACT_APP_BASE_URL}${post.image_url}`}
                  alt="post"
                  style={{ width: '100%' }}
                />
              )}
              {post.video_url && (
                <video autoPlay muted controls style={{ width: '100%' }}>
                  <source src={`${process.env.REACT_APP_BASE_URL}${post.video_url}`} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              )}

              <div className="post-stats">
                <div className="post-reactions">
                  {Object.entries({
                    "post-like": post.likes,
                    love: post.loves,
                    clap: post.claps,
                    haha: post.laughs,
                    wow: post.wows,
                    angry: post.angrys,
                    sad: post.sads
                  })
                    .filter(([_, count]) => count > 0) // Show only reactions with a count > 0
                    .map(([reaction, count]) => (
                      <div key={reaction} className="reaction">
                        <img
                          src={`assets/images/${reaction}.png`}
                          alt={reaction}
                          className="post-reaction-icon" // Added CSS class for icons
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
                  {/*${post.shares}*/}
                  <span
                    onClick={() => {
                      setSelectedPost(post); // Set the clicked post
                      setIsCommentsVisible(true); // Show the comments popup
                      fetchComments(post.id);  // Fetch comments
                    }}
                  >
                    {`${post.comments.length} comments `}
                  </span>
                </div>
                {isCommentsVisible && selectedPost && (
                  <div className="comments-modal">
                    <div className="modal-content">
                      {/* Modal Header */}
                      <div className="modal-header">
                        <h3>Comments</h3>
                        <button className="modal-close" onClick={() => setIsCommentsVisible(false)}>✖</button>
                      </div>

                      {/* Modal Body - Comments List */}
                      <div className="modal-body">
                        {comments.length === 0 ? (
                          <p style={{ textAlign: "center", color: "#666" }}>No comments yet.</p>
                        ) : (
                          comments.map((comment) => (
                            <div key={comment.id} className="comment-item">
                              {/* User Avatar */}
                              <img
                                src={`${process.env.REACT_APP_BASE_URL}/${users[comment.user_id]}`}
                                alt="User"
                                className="comment-avatar"
                                onError={(e) => (e.target.src = "assets/images/user-5.png")}
                              />
                              {/* Comment Content */}
                              <div className="comment-content">
                                <strong>{comment.user_name}</strong>
                                <p>{comment.comment_text}</p>
                              </div>
                              <div className="comment-meta">{getTimeAgo(comment.created_at)}</div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                )}

              </div>
              <div className="post-activity">
                <div>
                  <img src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`} className="post-activity-user-icon" alt="user-icon" />
                  <img src="assets/images/down-arrow.png" className="post-activity-arrow-icon" alt="arrow-icon" />
                </div>
                <div
                  className="reaction-container"
                  onMouseEnter={() => setShowReactions(post.id)}
                  onMouseLeave={() => setShowReactions(null)}
                >
                  {/* Like Button */}
                  <div className="post-activity-link">
                    <img src="assets/images/like.png" alt="like-icon" />
                    <span>Like</span>
                  </div>

                  {/* Reactions Bar */}
                  {showReactions === post.id && (
                    <div className="reactions-bar">
                      {reactions.map((reaction) => (
                        <img
                          key={reaction.name}
                          src={reaction.icon}
                          alt={reaction.name}
                          className="reaction-icon"
                          onClick={() => handleReaction(post.id, reaction.name)}
                        />
                      ))}
                    </div>
                  )}
                </div>


                <div className="post-activity-link" onClick={() => setIsCommenting(true)}>
                  <img src="assets/images/comment.png" alt="comment-icon" />
                  <span>Comment</span>
                </div>

                <div className="post-activity-link" onClick={() => console.log('Shared post')}>
                  <img src="assets/images/share.png" alt="share-icon" />
                  <span>Share</span>
                </div>
                <div className="post-activity-link" onClick={() => console.log('Sent post')}>
                  <img src="assets/images/send.png" alt="send-icon" />
                  <span>Send</span>
                </div>

              </div>

              <div className="post-stats">
                {isCommenting && (
                  <div className="comment-input-wrapper">
                    <textarea
                      value={comment}
                      onChange={handleCommentChange}
                      placeholder="Write a comment..."
                      rows="2"
                      className="comment-input"
                    />
                    <button onClick={() => handleCommentSubmit(post.id)} className="comment-send-btn">
                      <img src="assets/images/send-comment.png" alt="send" className="send-icon" />
                    </button>
                  </div>
                )}
              </div>

            </div>
          ))}
        </div>

        {/* Right Sidebar */}
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
              <img src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`} alt="user" />
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
      {footer}
    </div>
  );
};

export default Home;
