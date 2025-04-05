import React from 'react';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate,} from "react-router-dom";

const JobCard = ({ job }) => {
const navigate = useNavigate();
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
     console.log(job)
  const handleNavigate = (id) => {
    navigate('/jobDetails', { state: { jobId: id } });
  };
  return (
    <div className="job-card-container">
    <div className="single-job-items mb-30" key={job.job_id} style={{
        maxWidth: '100%',
        minWidth: '100%',
        boxSizing: 'border-box'
      }}
      onClick={() => handleNavigate(job.job_id)}>
        <div className="job-items" onClick={() => handleNavigate(job.job_id)} style={{ cursor: 'pointer' }} >
          <div className="company-img">
            <a href="#">
              <img 
                src={`${process.env.REACT_APP_BASE_URL}/${job.profile_image}`} 
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
              <li>{job.name}</li>
              <li><i className="fas fa-map-marker-alt"></i>{job.location}</li>
              <li>{job.salary}</li>
            </ul>
          </div>
        </div>
        <div className="items-link items-link2 f-right">
          <a onClick={() => handleNavigate(job.job_id)} style={{ cursor: 'pointer' }}>
            {job.type}
          </a>
          <span>{new Date(job.posted_at).toLocaleDateString()}</span>
        </div>
      </div>
   
                                 
     
 {/*    <div className="job-card">

      <h4>{job.title}</h4>
      <p>{job.description}</p>
      <p>{job.location}</p>
      <p>{job.salary}</p>
      <p>{job.job_type} | {job.experience}</p>
    </div>  */}
    </div>
  );
};

export default JobCard;
