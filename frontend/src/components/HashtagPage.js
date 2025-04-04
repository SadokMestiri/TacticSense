import React, { useEffect, useState } from "react";
import { useLocation} from "react-router-dom";
import axios from "axios";
import SinglePost from "./SinglePost"; // Import SinglePost component

const HashtagPage = ({ header, footer }) => {
    const location = useLocation();
  const { hashtag } = location.state || {}; // Get hashtag from state

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
  }, [hashtag]);

  const fetchPosts = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/hashtag/${hashtag}`);
      const postsData = response.data;
      setPosts(postsData);
    } catch (error) {
      console.error("Error fetching posts:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {header}
      <div className="hashtag-page">
        <h2>Posts with #{hashtag}</h2>
        {loading ? (
          <p>Loading...</p>
        ) : (
          posts.map((post) => (
            <SinglePost key={post.id} postId={post.id} header={header} /> // Use SinglePost for each post
          ))
        )}
      </div>
      {footer}
    </div>
  );
};

export default HashtagPage;
