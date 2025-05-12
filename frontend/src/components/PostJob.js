import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";

const PostJob = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({
    title: '',
    description: '',
    location: '',
    salary: '',
    job_type: '',
    experience: '',
    category: '',
  });
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
  useEffect(() => {
    if (!token || !decodedToken || (date && date.getTime() < now.getTime())) {
      Cookies.remove('token');
      navigate('/'); // This will navigate to the login page
    }
  }, [token, decodedToken, date, now, navigate]); // Dependencies should be static, avoid including "navigate"

  if (loading) {
    return <div>Loading...</div>;
  }

  // If there's an error fetching the jobs, show an error message
  if (error) {
    return <div>{error}</div>;
  }
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...form,
      user_id: user.id,
    };

    try {
      const res = await axios.post(`${process.env.REACT_APP_BASE_URL}/post-job`, payload, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      alert('Job posted successfully!');
      setForm({
        title: '',
        description: '',
        location: '',
        salary: '',
        job_type: '',
        experience: '',
        category: '',
      });
      navigate('/jobs');
    } catch (err) {
      console.error(err);
      alert('Error posting job');
    }
  };

  
  return (
    <div className="job-post-wrapper">

  <div className="job-post-content">
    <div className="job-post-inner">
      <h2 className="text-center mb-4">Post a New Job</h2>
      <form onSubmit={handleSubmit} className="job-post-form">
        <input type="text" name="title" placeholder="Job Title" value={form.title} onChange={handleChange} required />
        <textarea name="description" placeholder="Job Description" value={form.description} onChange={handleChange} required />
        <input type="text" name="location" placeholder="Location" value={form.location} onChange={handleChange} required />
        <input type="text" name="salary" placeholder="Salary" value={form.salary} onChange={handleChange} required />
        <select
  name="job_type"
  value={form.job_type}
  onChange={handleChange}
  required
  style={{ padding: "10px", borderRadius: "5px",marginBottom:"12px", borderColor: "#ccc", color: form.job_type ? "#000" : "#999" }}
>
  <option value="" disabled>Select Job Type</option>
  <option value="Full Time">Full Time</option>
  <option value="Part Time">Part Time</option>
</select>
<select
              name="experience"
              value={form.experience}
              onChange={handleChange}
              required
              style={{
                padding: "10px",
                borderRadius: "5px",
                marginBottom: "12px",
                borderColor: "#ccc",
                color: form.experience ? "#000" : "#999",
                marginLeft:"10px"              }}
            >
              <option value="" disabled>Select Experience Level</option>
              <option value="1-2">1-2 Years</option>
              <option value="2-3">2-3 Years</option>
              <option value="3-6">3-6 Years</option>
              <option value="6+">6+ Years</option>
            </select>
        <input type="text" name="category" placeholder="Category (optional)" value={form.category} onChange={handleChange} />
        <button type="submit" className="btn">Submit Job</button>
      </form>
    </div>
  </div>
  <div style={{ marginBottom: "100px" }}></div> {/* Spacing before footer */}
</div>

  );
};

export default PostJob;
