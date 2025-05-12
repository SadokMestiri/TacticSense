import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PlayerPredictor.css'; // Assuming styles are shared or specific to player profile

const PlayerProfile = () => {
  const { name } = useParams();
  const navigate = useNavigate();
  const [info, setInfo] = useState(null);
  const [career, setCareer] = useState([]);
  const [predicted, setPredicted] = useState(false);
  const [probability, setProbability] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    axios.get(`http://localhost:5000/player/${encodeURIComponent(name)}/career`)
      .then(res => {
        if (res.data && res.data.info) {
          // Handle NaN values in info (from origin/Sadok)
          const infoData = {
            ...res.data.info,
            age: isNaN(res.data.info.age) ? 'Unknown' : res.data.info.age,
            team: res.data.info.team === null || res.data.info.team === undefined ? 'Unknown' : res.data.info.team,
          };
          setInfo(infoData);
        } else {
          // Fallback if info is not directly available but res.data exists (from HEAD)
          if (res.data) {
            setInfo(res.data); // Or handle specific structure if different
          } else {
            setError('Player info not found or in unexpected format.');
            setInfo({}); // Avoid null errors later
          }
        }

        // Clean and merge career data (combining logic)
        if (res.data && res.data.career && Array.isArray(res.data.career)) {
          // Filter out seasons with null/undefined season identifiers (from origin/Sadok)
          const filteredCareer = res.data.career.filter(season =>
            season.season !== null && season.season !== undefined
          );

          const cleaned = filteredCareer.map(season => ({
            ...season,
            minutes: Number(String(season.minutes).replace(/,/g, '')),
            goals: Number(season.goals),
            assists: Number(season.assists),
            mp: Number(season.mp)
          }));

          // Merge duplicate seasons
          const merged = [];
          cleaned.forEach(season => {
            const existing = merged.find(s => s.season === season.season);
            if (existing) {
              existing.goals += season.goals;
              existing.assists += season.assists;
              existing.minutes += season.minutes;
              existing.mp += season.mp;
            } else {
              merged.push({ ...season });
            }
          });
          setCareer(merged);
        } else {
          setCareer([]); // Initialize career to an empty array if data is missing
          if (res.data && !res.data.career) { // Only set error if info was found but career was not
            // setError('Player career data not found.'); // Optional: more specific error
          }
        }
        setPredicted(false);
        setProbability(null);
      })
      .catch(err => {
        console.error("Error fetching player profile:", err);
        setError(err.response?.data?.error || `Failed to load profile for ${name}.`);
        setInfo({}); // Ensure info is not null on error to prevent render issues
        setCareer([]);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [name]);

  if (loading) return <div className="predictor-container" style={{textAlign: 'center', padding: '50px'}}>Loading player profile...</div>;
  if (error && !info) return <div className="predictor-container error" style={{textAlign: 'center', padding: '50px'}}>{error}</div>; // Show error prominently if no info
  // If info is an empty object from an error case but no specific error message was set for "not found", show generic message
  if (!info || Object.keys(info).length === 0 && !error) return <div className="predictor-container" style={{textAlign: 'center', padding: '50px'}}>Player data not available.</div>;


  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    if (payload.animate) {
      return <circle cx={cx} cy={cy} r={6} fill="red" stroke="black" strokeWidth={1} className="recharts-dot animate" />;
    }
    return <circle cx={cx} cy={cy} r={4} fill="#0073b1" />;
  };

  const handlePredict = async () => {
    try {
        setLoading(true); // Indicate loading for prediction
        setError('');
        const res = await axios.get(`http://localhost:5000/predict/player/${encodeURIComponent(name)}`);
        const pred = res.data.predictions;
        const prob = res.data.probability_playing_next_season;
        const lastSeasonData = career.length > 0 ? career[career.length - 1] : null;
        const lastSeasonYear = lastSeasonData ? parseInt(lastSeasonData.season.split('-')[0]) : new Date().getFullYear() -1; // Fallback if no career data
        
        const nextStart = lastSeasonYear + 1;
        const nextSeason = `${nextStart}-${String(nextStart + 1).slice(-2)}`; // Ensure two digits for year
        
        const newPoint = {
          season: nextSeason,
          goals: pred.goals,
          assists: pred.assists,
          minutes: pred.minutes,
          mp: pred.matches,
          animate: true
        };
        setCareer(old => [...old, newPoint]);
        setPredicted(true);
        setProbability(prob);
    } catch (err) {
        console.error("Error predicting next season:", err);
        setError(err.response?.data?.error || "Failed to get prediction.");
    } finally {
        setLoading(false);
    }
  };


  return (
    <div className="profile-container">
      <button
        className="submit-btn" // Using submit-btn style, or create a specific "back-btn" style
        style={{ marginBottom: '1.5rem', background: '#e6f0fa', color: '#0073b1', border: '1px solid #0073b1' }}
        onClick={() => navigate('/analysis-hub/players')}
      >
        ← Back to Players List
      </button>  
      {info && (info.player_name || info.name) && ( // Ensure info and name exist before rendering header
        <div className="profile-header">
          <div className="profile-avatar">
            {/* Combined logic for avatar: check info, then player_name, then name, fallback to 'P', then toUpperCase */}
            {(info && (info.player_name || info.name) ? (info.player_name || info.name)[0] : 'P').toUpperCase()}
          </div>
          <div className="profile-info">
            <h2>{info.player_name || info.name}</h2>
            <div>
              <b>Age:</b> {info.age !== undefined ? info.age : 'N/A'} &nbsp;|&nbsp; 
              <b>Position:</b> {info.position || 'N/A'} &nbsp;|&nbsp; 
              <b>Team:</b> {info.team || 'N/A'}
            </div>
          </div>
        </div>
      )}
      {error && <div className="predictor-container error" style={{textAlign: 'center', padding: '20px', color: 'red'}}>{error}</div>} {/* Display error message if any */}
      
      <div className="dashboard-graphs">
        <div>
          <h4>Goals per Season</h4>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={career}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="season" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="goals" stroke="#0073b1" activeDot={{ r: 8 }} dot={<CustomDot />} name="Goals" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h4>Assists per Season</h4>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={career}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="season" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="assists" stroke="#28a745" activeDot={{ r: 8 }} dot={<CustomDot />} name="Assists" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h4>Matches per Season</h4>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={career}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="season" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="mp" stroke="#ff9800" activeDot={{ r: 8 }} dot={<CustomDot />} name="Matches Played" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h4>Minutes per Season</h4>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={career}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="season" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="minutes" stroke="#e91e63" activeDot={{ r: 8 }} dot={<CustomDot />} name="Minutes Played" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      <button
        className="submit-btn"
        disabled={predicted || loading || !info || Object.keys(info).length === 0} // Also disable if no player info
        onClick={handlePredict}
      >
        {loading && !predicted ? 'Loading Profile...' : (loading && predicted ? 'Predicting...' : (predicted ? 'Prediction Shown' : 'Predict Next Season'))}
      </button>
      {probability !== null && (
        <div style={{
            marginTop: '1.2rem',
            background: '#f8fafc',
            borderRadius: '8px',
            padding: '1rem 1.5rem',
            color: '#0073b1',
            fontWeight: 600,
            fontSize: '1.15rem',
            boxShadow: '0 1px 6px rgba(0,0,0,0.04)',
            display: 'inline-block'
        }}>
            Probability of playing next season:&nbsp;
            <span style={{color: '#e91e63', fontWeight: 700}}>
            {((probability || 0) * 100).toFixed(1)}%
            </span>
        </div>
        )}
    </div>
  );
};

export default PlayerProfile;