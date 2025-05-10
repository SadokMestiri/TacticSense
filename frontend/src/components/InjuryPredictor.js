import React, { useState , useEffect} from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate} from "react-router-dom";
import { FaStar } from 'react-icons/fa';  // Import the star icon


function InjuryPredictor({header,footer}) {
    const navigate = useNavigate();
  const [formData, setFormData] = useState({
    Age: '',
    total_minutes_played: '',
    matches_played: '',
    Nationality: '',
    Position: '',
    total_yellow_cards: '',
    Team_Name: '',
    Season: '',
    total_red_cards: '',
    Date_of_Injury: '',
    Date_of_return: ''
  });
const [showPremiumPopup, setShowPremiumPopup] = useState(false);
const [burningCoin, setBurningCoin] = useState(false);
  const [topPredictions, setTopPredictions] = useState([]);
  const [researchInfo, setResearchInfo] = useState(null);  // Adjust to handle a single injury detail object
  const [loading, setLoading] = useState(false);
  const injuryType = topPredictions[0];
  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;
  
  if (token) {
    decodedToken = jwt_decode(token);
    exp = decodedToken?.exp;
  }
  
  const date = exp ? new Date(exp * 1000) : null;
  const now = new Date();
  const [allowed, setAllowed] = useState(false);
  const userCookie = Cookies.get('user');
  const user = userCookie ? JSON.parse(userCookie) : null;
  // Token expiration check
  useEffect(() => {
    if (!token || !decodedToken) {
      navigate('/');
    } else if (date && date.getTime() < now.getTime()) {
      Cookies.remove('token');
      navigate('/');
    } else {
      setAllowed(true);
    }
  }, [token, decodedToken, navigate, date]);
  
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...formData,
      Nationality: Number(formData.Nationality),
      Team_Name: Number(formData.Team_Name)
    };

    try {
      const res = await axios.post('http://localhost:5000/predict_injury_type', payload);
      setTopPredictions(res.data.top_3_predicted_injury_groups || []);
      console.log(res.data);
    } catch (error) {
      console.error(error);
      setTopPredictions(['Error during prediction']);
    }
  };
const handlePremiumFeature = async () => {
  setBurningCoin(true);

  try {
    const burnResponse = await axios.post(`http://localhost:5000/burn_metacoins`, {
      user_id: user.id,
      amount: 1,
    });

    if (burnResponse.status === 200) {
      // Burn successful, now activate the feature
      setShowPremiumPopup(false);
    } else {
      alert("Failed to burn MetaCoin.");
    }
  } catch (error) {
    const errMsg = error.response?.data?.error || "Error burning MetaCoin.";
    alert(errMsg);
  } finally {
    setBurningCoin(false);
    setShowPremiumPopup(false);
  }
};

  const handleFetchResearch = async () => {
    setLoading(true);
    const injuryType = topPredictions[0]; // Get the top predicted injury type
    
    try {
      const response = await axios.post('http://localhost:5000/get_injury_info', {
        injury_type: injuryType/* , email:"nounou.layouni.13@gmail.com" */ 
      });
console.log(response.data)
      setResearchInfo(response.data); 

    } catch (error) {
      console.error("Error fetching research data:", error);
      setResearchInfo({ injury_type: 'Unknown', details: 'No research found, please try again later.' });
    } finally {
      setLoading(false);
    }
  };
  return (
    <div>
    {header}
    <div style={{ backgroundColor: 'white', color: 'black', fontFamily: 'Arial, sans-serif', padding: '40px', borderRadius: '8px', boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)', maxWidth: '700px', marginTop: '50px', margin: 'auto', marginBottom: '100px' }}>
      <h2 style={{ textAlign: 'center', fontSize: '28px', marginBottom: '30px', color: '#333' }}>Injury Type Predictor</h2>
      <form onSubmit={handleSubmit}>
        {Object.entries(formData).map(([key, value]) => (
          <div key={key} style={{ marginBottom: '20px' }}>
            <label htmlFor={key} style={{ display: 'block', fontSize: '16px', marginBottom: '5px', color: '#333' }}>{key}:</label>
            <input
              type="text"
              name={key}
              value={value}
              onChange={handleChange}
              style={{
                width: '100%',
                padding: '10px',
                fontSize: '16px',
                borderRadius: '4px',
                border: '1px solid #ddd',
                boxSizing: 'border-box'
              }}
            />
          </div>
        ))}
        <button
          type="submit"
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '18px',
            borderRadius: '5px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
            transition: 'background-color 0.3s ease'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#45a049'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#4CAF50'}
        >
          Predict
        </button>
      </form>

      {topPredictions.length > 0 && (
        <div style={{ marginTop: '40px' }}>
          <h3 style={{ fontSize: '22px', marginBottom: '20px', color: '#333' }}>Top 3 Predicted Injury Types:</h3>
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {topPredictions.map((label, index) => (
              <li key={index} style={{ fontSize: '18px', marginBottom: '10px', color: '#555' }}>
                {index + 1}. <strong>{label}</strong>
              </li>
            ))}
          </ul>

<button
  onClick={() => setShowPremiumPopup(true)}
  style={{
    width: '100%',
    padding: '12px',
    fontSize: '18px',
    borderRadius: '5px',
    backgroundColor: '#EDC967',  // Gold color for premium
    color: 'white',
    border: 'none',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
    marginTop: '20px',
    display: 'flex',  // Flex to align the icon and text
    alignItems: 'center',  // Align vertically
    justifyContent: 'center',  // Center the content
  }}
>
  <FaStar style={{ marginRight: '10px' }} /> {/* Add the star icon */}
  Estimated Recovery Time based on medical evidence
</button>

{showPremiumPopup && (
  <div className="popup">
    <div className="popup-content">
      <h4>Premium Feature</h4>
      <p>This is a premium feature. Burn 1 MetaCoin to unlock?</p>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '15px' }}>
        <button
          onClick={handlePremiumFeature}
          disabled={burningCoin}
          style={{ padding: '10px', backgroundColor: '#4CAF50', color: 'white', border: 'none' }}
        >
          {burningCoin ? "Processing..." : "Yes"}
        </button>
        <button
          onClick={() => setShowPremiumPopup(false)}
          style={{ padding: '10px', backgroundColor: '#ccc', border: 'none' }}
        >
          No
        </button>
      </div>
    </div>
  </div>
)}

        </div>
      )}

      {loading && <p>Loading research data...</p>}

      {researchInfo && !loading && (
        <div style={{ marginTop: '40px' }}>
          <h3 style={{ fontSize: '22px', marginBottom: '20px', color: '#333' }}>Research on {researchInfo.injury_type}:</h3>
          <div style={{ fontSize: '18px', marginBottom: '10px', color: '#555' }}>
            <h4>Details:</h4>
            <p>{researchInfo.details}</p>
          </div>
        </div>
      )}
{/*
      {researchInfo && !loading && (
        <div style={{ marginTop: '40px' }}>
          <h3 style={{ fontSize: '22px', marginBottom: '20px', color: '#333' }}>{researchInfo}</h3>
        </div>
      )}*/}
    </div>
    {footer}
    </div>
  );
}

export default InjuryPredictor;
