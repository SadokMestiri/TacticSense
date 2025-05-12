import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";
import { useLocation } from 'react-router-dom';

const JobApplications = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [applications, setApplications] = useState([]);
  const [error, setError] = useState(null);
  const location = useLocation();
  const jobId = location.state?.jobId; // Get the jobId from the route state
  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;

  if (token) {
    decodedToken = jwt_decode(token);
    exp = decodedToken?.exp;
  }
  const date = exp ? new Date(exp * 1000) : null;
  const now = new Date();

  // Effect to handle token validation and job applications fetching
  useEffect(() => {
    if (!token || !decodedToken || (date && date.getTime() < now.getTime())) {
      // If no token or token is expired, remove the token and navigate to login
      Cookies.remove('token');
      navigate('/'); // This will navigate to the login page
    }
  }, [token, decodedToken, date, now, navigate]);
console.log(jobId)
  // Fetch job applications for the given jobId
  useEffect(() => {
    if (jobId) {
      setLoading(true);
      axios
        .get(`http://127.0.0.1:5000/applications/${jobId}`)  // Flask route to get applications
        .then((response) => {
          if (response.data.applications) {
            setApplications(response.data.applications);
          } else {
            setError('No applications found for this job');
          }
        })
        .catch((err) => {
          setError('Failed to fetch applications');
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [jobId]); // Run this effect when jobId changes

  // Handle loading state
  if (loading) {
    return <div>Loading...</div>;
  }

  // Handle error state
  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <main>
        <div className="applications-listing-area pt-120 pb-120">
          <div className="container">
            <div className="row">
              <div className="col-lg-12">
                <h2>Applications for this Job :</h2>
                {applications.length === 0 ? (
                  <p>No applications for this job.</p>
                ) : (
                  applications.map((application) => (
                    <div className="application-box" key={application.application_id} style={{border: "1px solid #ddd", margin: "10px", padding: "20px", borderRadius: "8px"}}>
                      <h4>Applicant Name : {application.user_name}</h4>
                      <p>Application Date : {new Date(application.application_date).toLocaleDateString()}</p>
                      <p>Job Title : {application.job_title}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default JobApplications;
