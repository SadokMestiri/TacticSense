import React, { useState, useEffect } from 'react';
import Header from './Header';
import { Tabs, Tab, Container} from '@mui/material';
import './Profile.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';

const Profile = () => {
  const [profileImage, setProfileImage] = useState('');
  const [username, setUsername] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [uploadedVideos, setUploadedVideos] = useState({});
  const [currentPage, setCurrentPage] = useState({});
  const [age, setAge] = useState({});
  const [nationality, setNationality] = useState({});
  const [position, setPosition] = useState({});
  const [matches, setMatches] = useState({});
  const [minutes, setMinutes] = useState({});
  const [goals, setGoals] = useState({});
  const [assists, setAssists] = useState({});
  const [club, setClub] = useState({});
  const [market_value, setMarket_value] = useState({});
  const [total_yellow_cards, setTotal_yellow_cards] = useState({});
  const [total_red_cards, setTotal_red_cards] = useState({});
  const [performance_metrics, setPerformance_metrics] = useState({});
  const [media_sentiment, setMedia_sentiment] = useState({});
  const [aggression, setAggression] = useState(50);
  const [reactions, setReecation] = useState(50);
  const [long_pass, setLong_pass] = useState(50);
  const [stamina, setStamina] = useState(50);
  const [strength, setStrength] = useState(50);
  const [sprint_speed, setSprint_speed] = useState(50);
  const [agility, setAgility] = useState(50);
  const [jumping, setJumping] = useState(50);
  const [heading, setHeading] = useState(50);
  const [free_kick_accuracy, setFree_kick_accuracy] = useState(50);
  const [volleys, setVolleys] = useState(50);
  const [ratings, setRatings] = useState({}); // State to store ratings for each skill
  const [averageRatings, setAverageRatings] = useState({}); // State to store average ratings for each skill

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  useEffect(() => {
    const fetchUserData = async () => {
      const userCookie = Cookies.get('user');
      if (userCookie) {
        const parsedUser = JSON.parse(userCookie);
        const userId = parsedUser.id; // Assuming `id` is stored in the cookie

        try {
          const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${userId}`, {
            headers: {
              Authorization: `Bearer ${Cookies.get('token')}`, // Include the token for authentication
            },
          });

          const userData = response.data;

          // Update state with the fetched user data
          setProfileImage(userData.profile_image);
          setUsername(userData.username);
          setName(userData.name);
          setEmail(userData.email);
          setRole(userData.role);
          setAge(userData.age);
          setNationality(userData.nationality);
          setPosition(userData.position);
          setMatches(userData.matches);
          setMinutes(userData.minutes);
          setGoals(userData.goals);
          setAssists(userData.assists);
          setClub(userData.club);
          setMarket_value(userData.market_value);
          setTotal_yellow_cards(userData.total_yellow_cards);
          setTotal_red_cards(userData.total_red_cards);
          setPerformance_metrics(userData.performance_metrics);
          setMedia_sentiment(userData.media_sentiment);
          setAggression(userData.aggression);
          setReecation(userData.reactions);
          setLong_pass(userData.long_pass);
          setStamina(userData.stamina);
          setStrength(userData.strength);
          setSprint_speed(userData.sprint_speed);
          setAgility(userData.agility);
          setJumping(userData.jumping);
          setHeading(userData.heading);
          setFree_kick_accuracy(userData.free_kick_accuracy);
          setVolleys(userData.volleys);
          console.log('User data:', userData);
        } catch (error) {
          console.error('Error fetching user data:', error);
          setMessage('Failed to fetch user data. Please try again.');
        }
      }
    };

    fetchUserData();
  }, []);

  useEffect(() => {
    const fetchAverageRatings = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/average_rating`);
        if (response.status === 200) {
          setAverageRatings(response.data.average_rating); // Assuming the API returns an object with skill names as keys
        }
      } catch (error) {
        console.error('Error fetching average ratings:', error);
      }
    };

    fetchAverageRatings();
  }, []);

  const handleImageChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setProfileImage(imageUrl); // Set the new image locally
      setMessage('Profile image updated locally. Save changes to update in the database.');
    }
  };

  const handleProfileUpdate = async () => {
  const token = Cookies.get('token');
  if (!token) {
    setMessage('No token found. Please log in again.');
    return;
  }

  // Create a FormData object to include the profile image and other fields
  const formData = new FormData();
  formData.append('username', username);
  formData.append('name', name);
  formData.append('email', email);
  formData.append('role', role);
  formData.append('age', age);
  formData.append('nationality', nationality);
  formData.append('position', position);
  formData.append('matches', matches);
  formData.append('minutes', minutes);
  formData.append('goals', goals);
  formData.append('assists', assists);
  formData.append('club', club);
  formData.append('market_value', market_value);
  formData.append('total_yellow_cards', total_yellow_cards);
  formData.append('total_red_cards', total_red_cards);
  formData.append('performance_metrics', performance_metrics);
  formData.append('media_sentiment', media_sentiment);
  formData.append('aggression', aggression);
  formData.append('reactions', reactions);
  formData.append('long_pass', long_pass);
  formData.append('stamina', stamina);
  formData.append('strength', strength);
  formData.append('sprint_speed', sprint_speed);
  formData.append('agility', agility);
  formData.append('jumping', jumping);
  formData.append('heading', heading);
  formData.append('free_kick_accuracy', free_kick_accuracy);
  formData.append('volleys', volleys);

  // Add the profile image if it is a local blob URL
  if (profileImage.startsWith('blob:')) {
    const response = await fetch(profileImage);
    const blob = await response.blob();
    formData.append('profile_image', blob, 'profile_image.jpg');
  }

  try {
    const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        // Do not set 'Content-Type' manually
      },
    });

    if (response.status === 200) {
      setMessage('Profile updated successfully');
    } else {
      setMessage('Unexpected response from the server.');
    }
  } catch (error) {
    if (error.response) {
      if (error.response.status === 401) {
        setMessage('Unauthorized. Please log in again.');
      } else {
        setMessage(`Error: ${error.response.data.message || 'Failed to update profile.'}`);
      }
    } else {
      setMessage('Network error. Please try again later.');
    }
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

  const handleDeleteVideo = (skill, index) => {
    setUploadedVideos((prev) => {
      const updatedVideos = [...(prev[skill] || [])];
      updatedVideos.splice(index, 1); // Remove the video at the specified index

      // Adjust the current page if necessary
      setCurrentPage((prevPage) => {
        const currentPageIndex = prevPage[skill] || 0;
        const newPageIndex = Math.min(currentPageIndex, Math.max(0, updatedVideos.length - 1));
        return {
          ...prevPage,
          [skill]: newPageIndex,
        };
      });

      return {
        ...prev,
        [skill]: updatedVideos,
      };
    });
  };

  const handlePageChange = (skill, direction) => {
    setCurrentPage((prev) => {
      const newPage = Math.max(0, (prev[skill] || 0) + direction);
      const maxPage = (uploadedVideos[skill]?.length || 0) - 1;
      return {
        ...prev,
        [skill]: Math.min(newPage, maxPage),
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
        {['Long passes', 'Free kicks', 'Goal Keeping'].map((skill) => (
          <div className="skill-container" key={skill}>
            <h3 style={{ color: '#333' }}>{skill}</h3>
            <div
              className="uploaded-videos"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                width: '100%',
                height: '100%',
              }}
            >
              {uploadedVideos[skill]?.[currentPage[skill] || 0] ? (
                <video
                  key={`${skill}-${currentPage[skill]}-${uploadedVideos[skill]?.length}`}
                  controls
                  width="100%"
                >
                  <source
                    src={uploadedVideos[skill][currentPage[skill] || 0]}
                    type="video/mp4"
                  />
                  Your browser does not support the video tag.
                </video>
              ) : (
                <button
                  className="upload-placeholder"
                  onClick={() =>
                    document.getElementById(`upload-${skill}`).click()
                  }
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#007bff',
                    cursor: 'pointer',
                  }}
                >
                  + Upload Video
                </button>
              )}
              <div
                style={{
                  marginTop: '10px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  width: '100%',
                }}
              >
                <button
                  onClick={() => handlePageChange(skill, -1)}
                  disabled={(currentPage[skill] || 0) === 0}
                  style={{
                    background: '#007bff',
                    color: '#fff',
                    border: 'none',
                    padding: '5px 10px',
                    cursor: 'pointer',
                    borderRadius: '5px',
                  }}
                >
                  Previous
                </button>
                {(uploadedVideos[skill]?.length < 3 ) && uploadedVideos[skill]?.[currentPage[skill] || 0] && (
                  <button
                    className="upload-placeholder"
                    onClick={() =>
                      document.getElementById(`upload-${skill}`).click()
                    }
                    //disabled={(currentPage[skill] || 0) === 0}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#007bff',
                      cursor: 'pointer',
                    }}
                  >
                    + Upload Video
                  </button>
                )}
                {uploadedVideos[skill]?.[currentPage[skill] || 0] && (
                  <button
                    className="remove-placeholder"
                    onClick={() => handleDeleteVideo(skill, currentPage[skill] || 0)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'red',
                      cursor: 'pointer',
                    }}
                  >
                    - Remove Video
                  </button>
                )}
                <button
                  onClick={() => handlePageChange(skill, 1)}
                  disabled={
                    (currentPage[skill] || 0) >=
                    (uploadedVideos[skill]?.length || 0) - 1
                  }
                  style={{
                    background: '#007bff',
                    color: '#fff',
                    border: 'none',
                    padding: '5px 10px',
                    cursor: 'pointer',
                    borderRadius: '5px',
                  }}
                >
                  Next
                </button>
              </div>
              <div style={{ marginTop: '20px' }}>
                <p>Rating: {averageRatings[skill] || 'Not rated yet'}</p>
              </div>
            </div>
            <input
              id={`upload-${skill}`}
              type="file"
              accept="video/*"
              multiple
              style={{ display: 'none' }}
              onChange={(e) => handleVideoUpload(e, skill)}
            />
            <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>

          </div>

        ))}          
        <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>

      </div>
    </div>

  );

  const tabs = [
    { id: 'personal', label: 'Personal Information', content: (
      <div>
        <h2>Account Info</h2>
        <div className="info-section">
          <div className="info-item">
            <label>Username:</label>
            <span className="info-value">{username || 'N/A'}</span>
          </div>
          <div className="info-item">
            <label>Name:</label>
            <span className="info-value">{name || 'N/A'}</span>
          </div>
          <div className="info-item">
            <label>Email:</label>
            <span className="info-value">{email || 'N/A'}</span>
          </div>
        </div>
        <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>
        <h2>Details</h2>
        <div className="details-section">
          <div className="details-item">
            <label>Nationality:</label>
            <span className="details-value">{nationality || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Age:</label>
            <span className="details-value">{age || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Club:</label>
            <span className="details-value">{club || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Position:</label>
            <span className="details-value">{position || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Market Value:</label>
            <span className="details-value">{market_value || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Matches Played:</label>
            <span className="details-value">{matches || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Minutes Played:</label>
            <span className="details-value">{minutes || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Goals:</label>
            <span className="details-value">{goals || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Assists:</label>
            <span className="details-value">{assists || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Total Yellow Cards:</label>
            <span className="details-value">{total_yellow_cards || 'N/A'}</span>
          </div>
          <div className="details-item">
            <label>Total Red Cards:</label>
            <span className="details-value">{total_red_cards || 'N/A'}</span>
          </div>
        </div>
        <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>
        <h2>Stats</h2>
        <div className="form-group">
          <label>Aggression</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={aggression}
              readOnly
            />
            <span className="slider-value" style={{ left: `${aggression}%` }}>{aggression}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Reactions</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={reactions}
              readOnly
            />
            <span className="slider-value" style={{ left: `${reactions}%` }}>{reactions}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Long Passes</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={long_pass}
              readOnly
            />
            <span className="slider-value" style={{ left: `${long_pass}%` }}>{long_pass}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Stamina</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={stamina}
              readOnly
            />
            <span className="slider-value" style={{ left: `${stamina}%` }}>{stamina}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Strength</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={strength}
              readOnly
            />
            <span className="slider-value" style={{ left: `${strength}%` }}>{strength}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Sprint Speed</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={sprint_speed}
              readOnly
            />
            <span className="slider-value" style={{ left: `${sprint_speed}%` }}>{sprint_speed}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Agility</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={agility}
              readOnly
            />
            <span className="slider-value" style={{ left: `${agility}%` }}>{agility}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Jumping</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={jumping}
              readOnly
            />
            <span className="slider-value" style={{ left: `${jumping}%` }}>{jumping}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Heading</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={heading}
              readOnly
            />
            <span className="slider-value" style={{ left: `${heading}%` }}>{heading}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Free Kick Accuracy</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={free_kick_accuracy}
              readOnly
            />
            <span className="slider-value" style={{ left: `${free_kick_accuracy}%` }}>{free_kick_accuracy}</span>
          </div>
        </div>
        <div className="form-group">
          <label>Volleys</label>
          <div className="slider-container">
            <input
              type="range"
              className="form-control slider"
              min="0"
              max="100"
              step="1"
              value={volleys}
              readOnly
            />
            <span className="slider-value" style={{ left: `${volleys}%` }}>{volleys}</span>
          </div>
        </div>
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
            <img src="assets/images/cover-pic.jpg" alt="cover" className="cover-image" />
            <div className="sidebar-profile-info">
              <div className="profile-image-wrapper">
                <img
                  src={profileImage.startsWith('blob:') ? profileImage : `${process.env.REACT_APP_BASE_URL}/${profileImage}`}
                  alt="profile"
                  className="profile-image"
                />
                {/* <label htmlFor="profile-image-upload" className="edit-icon">
                  <img
                    src="assets/images/edit-icon.png"
                    alt="edit"
                    className="edit-icon-image"
                  />
                </label>
                <input
                  type="file"
                  id="profile-image-upload"
                  style={{ display: 'none' }}
                  accept="image/*"
                  onChange={handleImageChange}
                /> */}
              </div>
              <h1 className="profile-name">{name}</h1>
              <h3 className="profile-username">{username}</h3>
              <ul className="profile-stats">
                <li>
                  Profile views <span className="stat-value">10K</span>
                </li>
                <li>
                  Post views <span className="stat-value">50K</span>
                </li>
                <li>
                  Connections <span className="stat-value">5K</span>
                </li>
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