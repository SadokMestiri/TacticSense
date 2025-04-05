import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import SinglePost from "./SinglePost"; // Import SinglePost component
import JobCard from "./JobCard"; // Import JobCard component (for job listings)

const HashtagPage = ({ header, footer }) => {
  const location = useLocation();
  const { hashtag,type } = location.state || {}; // Get the hashtag from the state

  const [posts, setPosts] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetchContent();
  }, [hashtag]);

  // Fetch posts and jobs based on the hashtag
  const fetchContent = async () => {
    try {
      // Fetch posts with hashtag
      if (type==="post"){
      const postResponse = await axios.get(`${process.env.REACT_APP_BASE_URL}/hashtag/${hashtag}`);
      console.log(postResponse.data)
      setPosts(postResponse.data);
      }else if (type==="job"){
      // Fetch jobs with hashtag
      const jobResponse = await axios.get(`${process.env.REACT_APP_BASE_URL}/hashtag/jobs/${hashtag}`);
      console.log(jobResponse.data)
      setJobs(jobResponse.data);
      }
    } catch (error) {
      console.error("Error fetching content:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {header}
      <div className="hashtag-page">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <>
          {type === "post" && (
            <div className="posts-section">
              <h3>Posts with #{hashtag}</h3>
              {posts.length === 0 && <p>No posts found for this hashtag.</p>}
              {posts.map((post) => (
                <SinglePost key={post.id} postId={post.id} />
              ))}
            </div>
            )}
                        {type === "job" && (

            <div className="jobs-section">
              <h3>Jobs with #{hashtag}</h3>
              {jobs.length === 0 && <p>No jobs found for this hashtag.</p>}
              {jobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
                        )}
          </>
        )}
      </div>
      {footer}
    </div>
  );
};

export default HashtagPage;
