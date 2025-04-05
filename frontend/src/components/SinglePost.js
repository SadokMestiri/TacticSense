import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate ,Link} from "react-router-dom";

const SinglePost = ({ header,postId }) => {
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [user, setUser] = useState(null);
  const [comment, setComment] = useState('');
  const [isCommentsVisible, setIsCommentsVisible] = useState(false); // To control visibility of the comments popup
  const [showReactions, setShowReactions] = useState(null);
  const currentUser =  JSON.parse(Cookies.get('user'));
  const [loading, setLoading] = useState(true);
  const [profile_image, setProfileImage] = useState(null);
  const [isCommenting, setIsCommenting] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);

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

  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;

  if (token) {
    decodedToken = jwt_decode(token);
    exp = decodedToken?.exp;
  }

  const date = exp ? new Date(exp * 1000) : null;
  const now = new Date();

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
  
  
  const fetchPostData = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_post_by_id/${postId}`);
      setPost(response.data);
      const userResponse = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${response.data.user_id}`);
      setUser(userResponse.data);
      setProfileImage(userResponse.data.profile_image);
    } catch (error) {
      console.error("Error fetching post or user:", error);
    } finally {
      setLoading(false); // Set loading to false when both post and user data are ready
    }
  };

  useEffect(() => {
    if (!token || !decodedToken || (date && date.getTime() < now.getTime())) {
      Cookies.remove('token');
      navigate('/');
    } else {
      fetchPostData();
      fetchComments(postId);
    }
  }, [postId]);

  const fetchComments = async (postId) => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_comments/${postId}`);
      setComments(response.data);
      console.log(response.data)
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  };

  const handleCommentChange = (e) => {
    setComment(e.target.value);
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (comment.trim() === '') return;

    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/add_comment`, {
        post_id: postId,
        user_id: currentUser.id,
        comment_text: comment,
        created_at: new Date().toISOString(),
      });
      setComment('');
      fetchComments(postId); // Refresh comments after submission
    } catch (error) {
      console.error("Error submitting comment:", error);
    }
  };

  const handleReaction = async (reactionType) => {
    try {
      await axios.post(`${process.env.REACT_APP_BASE_URL}/react_to_post`, {
        user_id: currentUser.id,
        post_id: postId,
        reaction_type: reactionType,
      });
      fetchPostData(); // Refresh post reactions
    } catch (error) {
      console.error('Error adding reaction:', error);
    }
  };

  if (loading) {
    return <div>Loading...</div>; // Display loading indicator until both post and user data are fetched
  }

  if (!post || !user) {
    return <div>Error loading post or user data</div>; // Handle error case if either post or user data is missing
  }

  const reactions = [
    { name: "like", icon: "assets/images/post-like.png" },
    { name: "love", icon: "assets/images/love.png" },
    { name: "laugh", icon: "assets/images/haha.png" },
    { name: "wow", icon: "assets/images/wow.png" },
    { name: "sad", icon: "assets/images/sad.png" },
    { name: "angry", icon: "assets/images/angry.png" },
  ];
  return (
    <div>
      <div className="container">
    <div className="main-content">
    <div className="post">
    <div className="post-author">
      <img src={`${process.env.REACT_APP_BASE_URL}/${profile_image}`}  alt="user" />
      <div>
        <h1>{user.name}</h1>
       {/* <small>{post.title}</small>*/}
       <small>{getTimeAgo(post.created_at)}</small>
       </div>
    </div>
    <p>{renderContent(post.content)}</p>
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
{`${comments.length} comments `}
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
    {/* User Avatar 
    <img
      src={`${process.env.REACT_APP_BASE_URL}/${users[comment.user_id]}`}
      alt="User"
      className="comment-avatar"
      onError={(e) => (e.target.src = "assets/images/user-5.png")}
    />*/}
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
        <img src={`${process.env.REACT_APP_BASE_URL}/${profile_image}`}  className="post-activity-user-icon" alt="user-icon" />
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
</div>
</div>
<style>{`
    .container {
      display: flex;
      justify-content: center;  /* Center horizontally */
      align-items: center;      /* Center vertically */
      padding: 20px;            /* Optional: add padding around the content */
    }

    .main-content {
      background-color: white;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Optional: for styling */
      border-radius: 8px;        /* Optional: for rounded corners */
      width: 100%;
      max-width: 800px;          /* Optional: limit the maximum width */
      padding: 20px;             /* Add padding inside the content box */
    }
  `}</style>
</div>
  );
};

export default SinglePost;
