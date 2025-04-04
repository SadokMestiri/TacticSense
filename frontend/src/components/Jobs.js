import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";

const Jobs = ({ header }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);

  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;

  if (token) {
    decodedToken = jwt_decode(token);
    exp = decodedToken?.exp;
  }
  const date = exp ? new Date(exp * 1000) : null;
  const now = new Date();

  // Effect to handle token validation and job fetching
  useEffect(() => {
    if (!token || !decodedToken || (date && date.getTime() < now.getTime())) {
      // If no token or token is expired, remove the token and navigate to login
      Cookies.remove('token');
      navigate('/'); // This will navigate to the login page
    }
  }, [token, decodedToken, date, now, navigate]); // Dependencies should be static, avoid including "navigate"

  // Fetch jobs function
  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://127.0.0.1:5000/jobs'); // Assuming you have an API endpoint to fetch jobs
      setJobs(response.data);
    } catch (error) {
      setError('Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    if (jobs.length === 0) {  // Only fetch if jobs are not already populated
      fetchJobs();
    }
  }, []); // Trigger when either conversationId or isGroupConversation changes
  
console.log(jobs)
  // If jobs are loading, show a loading state
  if (loading) {
    return <div>Loading...</div>;
  }

  // If there's an error fetching the jobs, show an error message
  if (error) {
    return <div>{error}</div>;
  }
  const handleNavigate = (id) => {
    navigate('/jobDetails', { state: { jobId: id } });
  };

  return (
    <div >
 {header}
 <main>
        <div className="job-listing-area pt-120 pb-120">
            <div className="container">
                <div className="row">
                    <div className="col-xl-3 col-lg-3 col-md-4">
                        <div className="row">
                            <div className="col-12">
                                    <div className="small-section-tittle2 mb-45">
                                    <div className="ion"> <svg 
                                        xmlns="http://www.w3.org/2000/svg"
                                        width="20px" height="12px">
                                    <path fillRule="evenodd"  fill="rgb(27, 207, 107)"
                                        d="M7.778,12.000 L12.222,12.000 L12.222,10.000 L7.778,10.000 L7.778,12.000 ZM-0.000,-0.000 L-0.000,2.000 L20.000,2.000 L20.000,-0.000 L-0.000,-0.000 ZM3.333,7.000 L16.667,7.000 L16.667,5.000 L3.333,5.000 L3.333,7.000 Z"/>
                                    </svg>
                                    </div>
                                    <h4>Filter Jobs</h4>
                                </div>
                            </div>
                        </div>
                        <div className="job-category-listing mb-50">
                            <div className="single-listing">
                               <div className="small-section-tittle2">
                                     <h4>Job Category</h4>
                               </div>
                                <div className="select-job-items2" >
                                    <select name="select" style={{borderColor: "#ccc",borderRadius: "5px",padding: "2px" ,color: "#999"}}>
                                        <option value="">All Category</option>
                                        <option value="">Category 1</option>
                                        <option value="">Category 2</option>
                                        <option value="">Category 3</option>
                                        <option value="">Category 4</option>
                                    </select>
                                </div>
                                <div className="select-Categories pt-80 pb-50">
                                    <div className="small-section-tittle2">
                                        <h4>Job Type</h4>
                                    </div>
                                    <label className="container">Full Time
                                        <input type="checkbox" />
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Part Time
                                        <input type="checkbox" defaultChecked="checked active"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Remote
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Freelance
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                </div>
                            </div>
                            <div className="single-listing">
                               <div className="small-section-tittle2">
                                     <h4>Job Location</h4>
                               </div>
                                <div className="select-job-items2">
                                    <select name="select" style={{borderColor: "#ccc",borderRadius: "5px",padding: "2px" ,color: "#999"}}>
                                        <option value="">Anywhere</option>
                                        <option value="">Category 1</option>
                                        <option value="">Category 2</option>
                                        <option value="">Category 3</option>
                                        <option value="">Category 4</option>
                                    </select>
                                </div>
                                <div className="select-Categories pt-80 pb-50">
                                    <div className="small-section-tittle2">
                                        <h4>Experience</h4>
                                    </div>
                                    <label className="container">1-2 Years
                                        <input type="checkbox" />
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">2-3 Years
                                        <input type="checkbox" defaultChecked="checked active"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">3-6 Years
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">6-more..
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                </div>
                            </div>
                            <div className="single-listing">
                                <div className="select-Categories pb-50">
                                    <div className="small-section-tittle2">
                                        <h4>Posted Within</h4>
                                    </div>
                                    <label className="container">Any
                                        <input type="checkbox" />
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Today
                                        <input type="checkbox" defaultChecked="checked active"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Last 2 days
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Last 3 days
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Last 5 days
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                    <label className="container">Last 10 days
                                        <input type="checkbox"/>
                                        <span className="checkmark"></span>
                                    </label>
                                </div>
                            </div>
                            <div className="single-listing">
                                <aside className="left_widgets p_filter_widgets price_rangs_aside sidebar_box_shadow">
                                    <div className="small-section-tittle2">
                                        <h4>Filter Jobs</h4>
                                    </div>
                                    <div className="widgets_inner">
                                        <div className="range_item">
                                             <div id="slider-range"></div> 
                                            <input type="text" className="js-range-slider" defaultValue="" style={{borderColor: "#ccc",borderRadius: "5px",margin: "5px" ,color: "#999",width:"170px"}}/>
                                       
                                        </div>
                                    </div>
                                </aside>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-9 col-lg-9 col-md-8">
                        <section className="featured-job-area">
                            <div className="container">
                                <div className="row">
                                    <div className="col-lg-12">
                                        <div className="count-job mb-35">
                                            <span>{jobs.length} Jobs found</span>
                                            <div className="select-job-items">
                                                <span>Sort by</span>
                                                <select name="select" style={{borderColor: "#ccc",borderRadius: "5px",padding: "2px" ,color: "#999"}}>
                                                    <option value="">None</option>
                                                    <option value="">job list</option>
                                                    <option value="">job list</option>
                                                    <option value="">job list</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                {jobs.map((job) => (
                      <div className="single-job-items mb-30" key={job.id}>
                        <div className="job-items" onClick={() => handleNavigate(job.id)}   style={{ cursor: 'pointer' }} >
                          <div className="company-img">
                          <a href="#">
  <img 
    src={`${process.env.REACT_APP_BASE_URL}/${job.posted_by.profile_image}`} 
    height="85px" 
    width="85px" 
    alt=""
    style={{ borderColor: '#136d15', borderWidth: '2px', borderStyle: 'solid' }} 
  />
</a>
                          </div>
                          <div className="job-tittle job-tittle2">
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
                        <div className="items-link items-link2 f-right">
                        <a 
  onClick={() => handleNavigate(job.id)} 
  style={{ cursor: 'pointer' }}
>
  {job.job_type}
</a>

                          <span>{new Date(job.date_posted).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
               
                               
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </div>
        <div className="pagination-area pb-115 text-center">
            <div className="container">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="single-wrap d-flex justify-content-center">
                            <nav aria-label="Page navigation example">
                                <ul className="pagination justify-content-start">
                                    <li className="page-item active"><a className="page-link" href="#">01</a></li>
                                    <li className="page-item"><a className="page-link" href="#">02</a></li>
                                    <li className="page-item"><a className="page-link" href="#">03</a></li>
                                <li className="page-item"><a className="page-link" href="#"><span className="ti-angle-right"></span></a></li>
                                </ul>
                            </nav>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    
      </main>
      </div>
  );
};

export default Jobs;
