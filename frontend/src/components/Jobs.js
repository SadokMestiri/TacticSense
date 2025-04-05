import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";

const Jobs = ({ header,footer }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);
  const [selectedJobTypes, setSelectedJobTypes] = useState([]);
  const [locationFilter, setLocationFilter] = useState('');
  const [selectedExperience, setSelectedExperience] = useState([]);
  const [postedWithin, setPostedWithin] = useState(null);
  const [searchQuery, setSearchQuery] = useState(''); // State to store the search query
  const [currentPage, setCurrentPage] = useState(1);
  const jobsPerPage = 7;
  const [sortOption, setSortOption] = useState(""); // track the selected sort option



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
console.log(response.data);  // Check what the response looks like

    } catch (error) {
      setError('Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };
  const isJobPostedWithin = (datePosted, range) => {
    const jobDate = new Date(datePosted);
    const currentDate = new Date();
    const diffInDays = Math.floor((currentDate - jobDate) / (1000 * 60 * 60 * 24));
  
    switch (range) {
      case 'today':
        return diffInDays === 0;
      case 'last2':
        return diffInDays <= 2;
      case 'last3':
        return diffInDays <= 3;
      case 'last5':
        return diffInDays <= 5;
      case 'last10':
        return diffInDays <= 10;
      default:
        return true;
    }
  };
  

  const filteredJobs = jobs.filter((job) => {
    const matchSearchQuery = searchQuery === '' || // If search query is empty, match all jobs
      job.title.toLowerCase().includes(searchQuery) || // Match job title
      job.posted_by.name.toLowerCase().includes(searchQuery); // Match poster name

    const matchJobType = selectedJobTypes.length > 0
      ? selectedJobTypes.includes(job.job_type)
      : true;

    const matchLocation = locationFilter
      ? job.location.toLowerCase().includes(locationFilter.toLowerCase())
      : true;

    const matchExperience = selectedExperience.length > 0
      ? selectedExperience.includes(job.experience)
      : true;

    // Handle the posted date filter
    const matchDatePosted = postedWithin
      ? isJobPostedWithin(job.date_posted, postedWithin)
      : true; // If postedWithin is null, match all

    return matchSearchQuery && matchJobType && matchLocation && matchExperience && matchDatePosted;
  });
  
  


  useEffect(() => {
    if (jobs.length === 0) {  // Only fetch if jobs are not already populated
      fetchJobs();
    }
  }, []); // Trigger when either conversationId or isGroupConversation changes
  
  const sortJobs = (option) => {
    let sortedJobs = [...filteredJobs]; // Make sure to keep a copy of the filtered jobs
    // Check if filteredJobs is available before trying to sort
    if (!filteredJobs || filteredJobs.length === 0) {
      return; // No jobs to sort, exit early
    }
  
    // Sorting logic
    if (option === "date") {
      sortedJobs = sortedJobs.sort((a, b) => new Date(b.date_posted) - new Date(a.date_posted));
    } else if (option === "alphabetical") {
      sortedJobs = sortedJobs.sort((a, b) => a.title.localeCompare(b.title)); // Sort by title alphabetically
    }
  
    // If "None" is selected, don't apply any sorting (this effectively resets to the original order)
    if (option === "none") {
      sortedJobs = [...jobs]; // Reset to original filtered jobs, before sorting
    }
  
    // Reapply pagination after sorting
    const indexOfLastJob = currentPage * jobsPerPage;
    const indexOfFirstJob = indexOfLastJob - jobsPerPage;
    const currentJobs = sortedJobs.slice(indexOfFirstJob, indexOfLastJob); // Reapply pagination
  
    setJobs(sortedJobs); // Optionally update jobs state, if needed
  };
  
  useEffect(() => {
    sortJobs(sortOption);
  }, [sortOption, currentPage]); // Trigger sort when sortOption or currentPage changes
  useEffect(() => {
    // Reset sorting when any of the filters change (job type, location, experience, postedWithin)
    setSortOption("none"); // Reset to "None" sorting
  }, [selectedJobTypes, locationFilter, selectedExperience, postedWithin]);
  
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
  const handleNavigateApply = (id) => {
    navigate('/postJob');
  };
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value.toLowerCase()); // Update search query to lowercase for case-insensitive search
  };
  const handleJobTypeChange = (e) => {
    const { value, checked } = e.target;
  
    if (checked) {
      setSelectedJobTypes((prev) => [...prev, value]);
    } else {
      setSelectedJobTypes((prev) => prev.filter((type) => type !== value));
    }
  };
  const handleExperienceChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setSelectedExperience((prev) => [...prev, value]);
    } else {
      setSelectedExperience((prev) => prev.filter((range) => range !== value));
    }
  };
 
 
  
  
  const handlePageClick = (page) => {
    setCurrentPage(page);
  };
  const indexOfLastJob = currentPage * jobsPerPage;
  const indexOfFirstJob = indexOfLastJob - jobsPerPage;
  const currentJobs = filteredJobs.slice(indexOfFirstJob, indexOfLastJob);

  // Calculate total number of pages
  const totalPages = Math.ceil(filteredJobs.length / jobsPerPage);

  // Create page numbers
  const pageNumbers = [];
  for (let i = 1; i <= totalPages; i++) {
    pageNumbers.push(i);
  }

  
  


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
                            <div className="apply-btn2">
  <a 
    className="btn" 
    onClick={() => handleNavigateApply()} 
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
    >+ Post a job</a>
    </div> 
                            
    <div className="select-Categories pt-80 pb-50">
    <div className="single-listing">
                            
                            <aside className="left_widgets p_filter_widgets price_rangs_aside sidebar_box_shadow">
      <div className="small-section-tittle2">
        <h4>Filter Jobs</h4>
      </div>
      <div className="widgets_inner">
      <div className="range_item">
      <div id="slider-range"></div> 
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}  // Update the search query on change
            placeholder="Type job or company name"
            style={{borderColor: "#ccc",borderRadius: "5px" ,color: "#999",width:"210px",paddingLeft:"5px",marginBottom:"25px"}}
          />
        </div>
      </div>
    </aside>
                            </div>
                       
  <div className="small-section-tittle2">
    <h4>Job Type</h4>
  </div>

  <label className="container">Full Time
    <input
      type="checkbox"
      value="Full Time"
      onChange={handleJobTypeChange}
    />
    <span className="checkmark"></span>
  </label>

  <label className="container">Part Time
    <input
      type="checkbox"
      value="Part Time"
      onChange={handleJobTypeChange}
    />
    <span className="checkmark"></span>
  </label>
</div>

                            </div>
                            <div className="single-listing">
  <div className="small-section-tittle2">
    <h4>Job Location</h4>
  </div>
  <div className="select-job-items2">
    <select 
      name="locationFilter" 
      value={locationFilter}
      onChange={(e) => setLocationFilter(e.target.value)}
      style={{
        borderColor: "#ccc",
        borderRadius: "5px",
        padding: "2px",
        color: "#999"
      }}
    >
      <option value="">Select a location</option>
      <option value="Remote">Remote</option>
      <option value="Tunisia">Tunisia</option>
      <option value="France">France</option>
      <option value="Germany">Germany</option>
      <option value="USA">USA</option>
    </select>
  </div>


  <div className="select-Categories pt-80 pb-50">
  <div className="small-section-tittle2">
    <h4>Experience</h4>
  </div>
  
  <label className="container">1-2 Years
  <input 
    type="checkbox" 
    value="1-2"
    onChange={handleExperienceChange} 
  />
  <span className="checkmark"></span>
</label>

<label className="container">2-3 Years
  <input 
    type="checkbox" 
    value="2-3"
    onChange={handleExperienceChange} 
  />
  <span className="checkmark"></span>
</label>

<label className="container">3-6 Years
  <input 
    type="checkbox" 
    value="3-6"
    onChange={handleExperienceChange} 
  />
  <span className="checkmark"></span>
</label>

<label className="container">6+ Years
  <input 
    type="checkbox" 
    value="6+"
    onChange={handleExperienceChange} 
  />
  <span className="checkmark"></span>
</label>

</div>
</div>

<div className="single-listing">
  <div className="select-Categories pb-50">
    <div className="small-section-tittle2">
      <h4>Posted Within</h4>
    </div>
    <label className="container">Today
      <input
        type="checkbox"
        checked={postedWithin === 'today'}
        onChange={() => setPostedWithin(postedWithin === 'today' ? null : 'today')}
      />
      <span className="checkmark"></span>
    </label>

    <label className="container">Last 2 days
      <input
        type="checkbox"
        checked={postedWithin === 'last2'}
        onChange={() => setPostedWithin(postedWithin === 'last2' ? null : 'last2')}
      />
      <span className="checkmark"></span>
    </label>

    <label className="container">Last 3 days
      <input
        type="checkbox"
        checked={postedWithin === 'last3'}
        onChange={() => setPostedWithin(postedWithin === 'last3' ? null : 'last3')}
      />
      <span className="checkmark"></span>
    </label>

    <label className="container">Last 5 days
      <input
        type="checkbox"
        checked={postedWithin === 'last5'}
        onChange={() => setPostedWithin(postedWithin === 'last5' ? null : 'last5')}
      />
      <span className="checkmark"></span>
    </label>

    <label className="container">Last 10 days
      <input
        type="checkbox"
        checked={postedWithin === 'last10'}
        onChange={() => setPostedWithin(postedWithin === 'last10' ? null : 'last10')}
      />
      <span className="checkmark"></span>
    </label>
  </div>
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
                                            <select
  name="select"
  style={{
    borderColor: "#ccc",
    borderRadius: "5px",
    padding: "2px",
    color: "#999",
  }}
  onChange={(e) => {
    const selectedSortOption = e.target.value;
    setSortOption(selectedSortOption); // Update sort option state
    sortJobs(selectedSortOption); // Apply sorting based on the selected option
  }}
>
  <option value="none">None</option>
  <option value="date">Date</option>
  <option value="alphabetical">Alphabetically</option>
</select>

                                            </div>
                </div>
                                    </div>
                                </div>
                                {filteredJobs.length > 0 ? (
  currentJobs.map((job) => (
    <div className="single-job-items mb-30" key={job.id} style={{
      maxWidth: '100%',
      minWidth: '100%',
      boxSizing: 'border-box'
    }}>
      <div className="job-items" onClick={() => handleNavigate(job.id)} style={{ cursor: 'pointer' }} >
        <div className="company-img">
          <a href="#">
            <img 
              src={`${process.env.REACT_APP_BASE_URL}/${job.posted_by.profile_image}`} 
              height="auto" 
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
        <a onClick={() => handleNavigate(job.id)} style={{ cursor: 'pointer' }}>
          {job.job_type}
        </a>
        <span>{new Date(job.date_posted).toLocaleDateString()}</span>
      </div>
    </div>
  ))
) : (
  <div style={{ padding: '20px', textAlign: 'center', color: '#888', fontSize: '18px',height:"70px",backgroundColor:"white",width:"1000px",borderRadius:"5px" }}>
    No corresponding jobs found.
  </div>
)}

                               
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
                    <li
                      className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}
                    >
                      <a
                        className="page-link"
                        href="#"
                        onClick={() => handlePageClick(currentPage - 1)}
                      >
                        <span className="ti-angle-left"></span>
                      </a>
                    </li>

                    {pageNumbers.map((number) => (
                      <li
                        key={number}
                        className={`page-item ${currentPage === number ? 'active' : ''}`}
                      >
                        <a
                          className="page-link"
                          href="#"
                          onClick={() => handlePageClick(number)}
                        >
                          {String(number).padStart(2, '0')}
                        </a>
                      </li>
                    ))}

                    <li
                      className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}
                    >
                      <a
                        className="page-link"
                        href="#"
                        onClick={() => handlePageClick(currentPage + 1)}
                      >
                        <span className="ti-angle-right"></span>
                      </a>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
 </div>
      </main>
      {footer}
      </div>
  );
};

export default Jobs;