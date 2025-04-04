import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";
import { useLocation } from 'react-router-dom';

const JobDetails = ({ header }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const location = useLocation();
  const jobId = location.state?.jobId; // Get jobId passed via navigation state
  console.log(jobId)
  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;

  if (token) {
    decodedToken = jwt_decode(token);
    exp = decodedToken?.exp;
  }
  const date = exp ? new Date(exp * 1000) : null;
  const now = new Date();
const userCookie = Cookies.get('user');
const user = userCookie ? JSON.parse(userCookie) : null;
  // Effect to handle token validation and job fetching
  useEffect(() => {
    if (!token || !decodedToken || (date && date.getTime() < now.getTime())) {
      // If no token or token is expired, remove the token and navigate to login
      Cookies.remove('token');
      navigate('/'); // This will navigate to the login page
    }
  }, [token, decodedToken, date, now, navigate]); // Dependencies should be static, avoid including "navigate"

  // Fetch jobs function
  const fetchJob = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://127.0.0.1:5000/job/${jobId}`,{userId:user.id}); // Assuming you have an API endpoint to fetch jobs
      setJob(response.data);
    } catch (error) {
      setError('Failed to fetch job');
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    if (job == null) {  // Only fetch if jobs are not already populated
      fetchJob();
    }
  }, []); // Trigger when either conversationId or isGroupConversation changes
  
console.log(job)
  // If jobs are loading, show a loading state
  if (loading) {
    return <div>Loading...</div>;
  }

  // If there's an error fetching the jobs, show an error message
  if (error) {
    return <div>{error}</div>;
  }
  console.log(user)
  const handleApply = async () => {
    // Validate if Job ID and Token exist
    if (!jobId || !user) {
      alert('Job ID or user is missing');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await axios.post(
        `http://127.0.0.1:5000/apply/${jobId}`,
        { current_user: user.id }, // Sending user ID in the request body
      );
      
      // Show success alert with message from the server response
      alert(response.data.message); 
  
      // Navigate to the home page after successful application
      navigate('/home');
      
    } catch (error) {
      // Handle error properly: show the error message if available
      if (error.response && error.response.data && error.response.data.error) {
        alert(`Error: ${error.response.data.error}`);
      } else {
        alert('Failed to apply for the job'); // Default error message
      }
      
    } finally {
      setLoading(false);  // Stop loading state
    }
  };
  const viewApplications = () => {
    navigate('/jobApplications', { state: { jobId: jobId } });
  };
  return (
    <div >
 {header}
 <main>
   { job &&(
    <div>
 <div className="slider-area ">
        <div className="single-slider section-overly slider-height2 d-flex align-items-center"  style={{ backgroundImage: "url('jobassets/img/hero/deal.jpg')" }}>
            <div className="container">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="hero-cap text-center">
                            <h2>{job.title}</h2>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </div>
        <div className="job-post-company pt-120 pb-120">
            <div className="container">
                <div className="row justify-content-between">
                    <div className="col-xl-7 col-lg-8">
                        <div className="single-job-items mb-50">
                            <div className="job-items">
                                <div className="company-img company-img-details">
                                    <a href="#">  <img 
    src={`${process.env.REACT_APP_BASE_URL}/${job.posted_by.profile_image}`} 
    height="85px" 
    width="85px" 
    alt=""
    style={{ borderColor: '#136d15', borderWidth: '2px', borderStyle: 'solid' }} 
  /></a>
                                </div>
                                <div className="job-tittle">
                                    <a href="#">
                                        <h4>{job.title}</h4>
                                    </a>
                                    <ul>
                                        <li>{job.posted_by.name}</li>
                                        <li><i className="fas fa-map-marker-alt"></i>{job.location}</li>
                                        <li>{job.salary}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                       
                        <div className="job-post-details">
                            <div className="post-details1 mb-50">
                                <div className="small-section-tittle">
                                    <h4>Job Description</h4>
                                </div>
                                <p>{job.description}</p>
                            </div>
                            <div className="post-details2  mb-50">
                                <div className="small-section-tittle">
                                    <h4>Required Experience and job type</h4>
                                </div>
                               <ul>
                                   <li>{job.experience}</li>
                                   <li>{job.job_type}</li>
                                   <li>Research and code , libraries, APIs and frameworks</li>
                                   <li>Strong knowledge on software development life cycle</li>
                                   <li>Strong problem solving and debugging skills</li>
                               </ul>
                            </div>
                            <div className="post-details2  mb-50">
                                <div className="small-section-tittle">
                                    <h4>Education + Experience</h4>
                                </div>
                               <ul>
                                   <li>3 or more years of professional design experience</li>
                                   <li>Direct response email experience</li>
                                   <li>Ecommerce website design experience</li>
                                   <li>Familiarity with mobile and web apps preferred</li>
                                   <li>Experience using Invision a plus</li>
                               </ul>
                            </div>
                        </div>

                    </div>
                    <div className="col-xl-4 col-lg-4">
                        <div className="post-details3  mb-50">
                           <div className="small-section-tittle">
                               <h4>Job Overview</h4>
                           </div>
                          <ul>
                              <li>Posted date : <span>{job.date_posted}</span></li>
                              <li>Location : <span>{job.location}</span></li>
                              <li>Job nature : <span>{job.job_type}</span></li>
                              <li>Salary :  <span>{job.salary}</span></li>
                              <li>Application date : <span>12 Sep 2020</span></li>
                          </ul>
                          <div className="apply-btn2">
  <a 
    onClick={() => handleApply()}
    className="btn" 
    style={{
      backgroundColor: 'darkgrey',
      borderColor: 'green',
      borderRadius: '8px', 
      padding: '10px 20px',
      color: 'white',
      textDecoration: 'none', // Optional: Removes underline
      transition: 'background-color 0.3s ease', // Smooth transition for hover
    }} 
    onMouseEnter={(e) => e.target.style.backgroundColor = 'white'} // Hover effect
    onMouseLeave={(e) => e.target.style.backgroundColor = 'darkgrey'} // Reset to original color
  >
    Apply Now
  </a>
</div>
<div className="apply-btn2">
  <a 
    onClick={() => viewApplications()}
    className="btn" 
    style={{
      marginTop:"10px",
      backgroundColor: 'darkgrey',
      borderColor: 'green',
      borderRadius: '8px', 
      padding: '10px 20px',
      color: 'white',
      textDecoration: 'none', // Optional: Removes underline
      transition: 'background-color 0.3s ease', // Smooth transition for hover
    }} 
    onMouseEnter={(e) => e.target.style.backgroundColor = 'white'} // Hover effect
    onMouseLeave={(e) => e.target.style.backgroundColor = 'darkgrey'} // Reset to original color
  >
    View Applications
  </a>
</div>
                       </div>
                        <div className="post-details4  mb-50">
                           <div className="small-section-tittle">
                               <h4>Company Information</h4>
                           </div>
                              <span>{job.posted_by.username}</span>
                              <p>It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
                            <ul>
                                <li>Name: <span>{job.posted_by.username}</span></li>
                                <li>Web : <span> colorlib.com</span></li>
                                <li>Email: <span>{job.posted_by.email}</span></li>
                            </ul>
                       </div>
                    </div>
                </div>
            </div>
        </div>
      
        </div>
        
)}
      </main>
      </div>
  );
};

export default JobDetails;
