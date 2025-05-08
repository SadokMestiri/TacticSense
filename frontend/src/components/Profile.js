import React, { useState, useEffect } from 'react';
import Header from './Header';
import { Tabs, Tab} from '@mui/material';
import './Profile.css';
import axios from 'axios';
import Cookies from 'js-cookie';

const Profile = () => {
  const [profileImage, setProfileImage] = useState('');
  const [username, setUsername] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [uploadedVideos, setUploadedVideos] = useState({});
  const [currentPage, setCurrentPage] = useState({});

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  useEffect(() => {
    const userCookie = Cookies.get('user');
    if (userCookie) {
      const parsedUser = JSON.parse(userCookie);
      setProfileImage(parsedUser.profile_image);
      setUsername(parsedUser.username);
      setName(parsedUser.name);
      setEmail(parsedUser.email);
    }
  }, []);

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('profile_image', file);

      try {
        const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setProfileImage(response.data.profile_image);
        setMessage('Profile image updated successfully');
      } catch (error) {
        setMessage('Error updating profile image');
      }
    }
  };

  const handleProfileUpdate = async () => {
    const updatedProfile = {
      username,
      name,
      email,
    };

    try {
      await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile_info`, updatedProfile, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setMessage('Profile updated successfully');
    } catch (error) {
      setMessage('Error updating profile information');
    }
  };

  const handleVideoUpload = (event, skill) => {
    const files = Array.from(event.target.files);
    const videoURLs = files.map((file) => URL.createObjectURL(file));

    setUploadedVideos((prev) => ({
      ...prev,
      [skill]: [...(prev[skill] || []), ...videoURLs].slice(0, 3), // Limit to 3 videos per skill
    }));
  };

  const handlePageChange = (skill, direction) => {
    console.log(
      'Videos for current page:',
      (uploadedVideos[skill] || []).slice(
        currentPage[skill] || 0,
        (currentPage[skill] || 0) + 1
      )
    );
    setCurrentPage((prev) => {
      const newPage = Math.max(0, (prev[skill] || 0) + direction);
      console.log(`Skill: ${skill}, New Page: ${newPage}`);
      return {
        ...prev,
        [skill]: newPage,
      };
    });
  };


  const MarketValuePredictor = () => {
    const [prediction, setPrediction] = useState(null);
  
    const predictMarketValue = async (inputData) => {
      try {
        const response = await axios.post('http://127.0.0.1:5000/predict', {
          input: inputData,
        });
        setPrediction(response.data.prediction);
        console.log('Prediction:', response.data.prediction);
      } catch (error) {
        console.error('Error making prediction:', error);
      }
    };
  
    return (
      <div>
        <h3>Market Value Predictor</h3>
        <button onClick={() => predictMarketValue([2.481939,-0.828362,
          -1.597527,-2.013867,-1.998466,-1.618861,-1.573948,-1.695989,-0.003764,
          -2.063420,-1.307850,-1.468429,-1.00975,-2.044530,-2.123675,-1.865531,
          -1.238116,-2.191793,0.438333,-1.591032,-1.444629,-0.909757,-0.489147,
          -2.136695,-0.833992,-1.855516,-1.526697,-2.019015,-1.803907,-1.574778,
          -1.657954,2.341630,2.356355,2.363265,2.358774,2.348967,93,2,1])}>
          Predict Market Value
        </button>
        {prediction && <p>Prediction: {prediction}</p>}
      </div>
    );
  };

  //export default MarketValuePredictor;

  const renderSkills = () => (
    <div>
      <div className="skills-section">
        {['Dribbling', 'Shooting', 'Goal Keeping'].map((skill) => (
          <div className="skill-container" key={skill}>
            <h3 style={{ color: '#333' }}>{skill} &nbsp;
            <button
              className="update-profile-btn"
              onClick={() => document.getElementById(`upload-${skill}`).click()}
            >
              {/* <img src="assets/images/upload-icon.png" alt="Upload" className="upload-icon" /> Upload Video */}
              Upload Video
            </button>
            <input
              id={`upload-${skill}`}
              type="file"
              accept="video/*"
              multiple
              style={{ display: 'none' }}
              onChange={(e) => handleVideoUpload(e, skill)}
            />
            </h3>
            <div className="uploaded-videos">
              <button
                className="pagination-button"
                onClick={() => handlePageChange(skill, -1)}
                disabled={(currentPage[skill] || 0) === 0}
              >
                <img src="assets/images/left-arrow.png" alt="Previous" />
              </button>
              {(uploadedVideos[skill] || []).slice(
                currentPage[skill] || 0,
                (currentPage[skill] || 0) + 1
              ).map((video, index) => (
                <video key={`${skill}-${index}-${currentPage[skill]}`} controls width="100%">
                  <source src={video} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              ))}
              <button
                className="pagination-button"
                onClick={() => handlePageChange(skill, 1)}
                disabled={
                  ((currentPage[skill] || 0) + 1) >= (uploadedVideos[skill]?.length || 0)
                }
              >
                <img src="assets/images/right-arrow.png" alt="Next" />
              </button>
            </div>
          <br/>
          </div>
        ))}
      </div>
    </div>
  );

  const tabs = [
    { id: 'personal', label: 'Personal Information', content: (
      <div>
        <form>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              className="form-control"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter new username"
            />
          </div>
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              className="form-control"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter full name"
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter email address"
            />
          </div>
          <button type="button" className="update-profile-btn" onClick={handleProfileUpdate}>
            Update Profile
          </button>
        </form>
        {message && <p className="text-info">{message}</p>}
      </div>
    ) },
    { id: 'skills', label: 'Skills', content: renderSkills() },
  ];

  return (
    <div>
      <Header />
      <div className="container">
        <div className="left-sidebar">
          <div className="sidebar-profile-box">
            <img src="assets/images/cover-pic.jpg" alt="cover" width="100%" />
            <div className="sidebar-profile-info">
              <div className="profile-image-wrapper">
                <img src={`${process.env.REACT_APP_BASE_URL}/${profileImage}`} alt="profile" className="profile-image" />
                <label htmlFor="profile-image-upload" className="edit-icon">
                  <img src="assets/images/edit-icon.png" alt="edit" className="edit-icon-image" />
                </label>
                <input
                  type="file"
                  id="profile-image-upload"
                  style={{ display: 'none' }}
                  accept="image/*"
                  onChange={handleImageChange}
                />
              </div>
              <h1>{name}</h1>
              <h3>{username}</h3>
              <ul>
                <li>Profile views <span>10K</span></li>
                <li>Post views <span>50K</span></li>
                <li>Connections <span>5K</span></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="main-content">
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="profile tabs">
            {tabs.map((tab, index) => (
              <Tab key={tab.id} label={tab.label} />
            ))}
          </Tabs>
          <div>{tabs[activeTab]?.content}</div>
        </div>
        <div className="right-sidebar">
          <div className="sidebar-news">
            <MarketValuePredictor />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;