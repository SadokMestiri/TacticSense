import React, { useEffect, useState } from 'react';
import { useParams,useNavigate } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PlayerProfile = () => {
  const { name } = useParams();
  const navigate = useNavigate();
  const [info, setInfo] = useState(null);
  const [career, setCareer] = useState([]);
  const [predicted, setPredicted] = useState(false);
  const [probability, setProbability] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:5000/player/${encodeURIComponent(name)}/career`)
      .then(res => {
        setInfo(res.data.info);
        // Clean and merge career data
        const cleaned = res.data.career.map(season => ({
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
        setPredicted(false); // Reset prediction state on player change
      });
  }, [name]);

  if (!info) return <div>Loading...</div>;

  // Custom dot for predicted points
  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    if (payload.animate) {
      return <circle cx={cx} cy={cy} r={6} fill="red" stroke="black" strokeWidth={1} />;
    }
    return <circle cx={cx} cy={cy} r={4} fill="#0073b1" />;
  };

  return (
    <div className="profile-container">
      <button
        className="submit-btn"
        style={{ marginBottom: '1.5rem', background: '#e6f0fa', color: '#0073b1', border: '1px solid #0073b1' }}
        onClick={() => navigate('/StatPredictions/existing')}
      >
        ← Back to Players List
      </button>  
      <div className="profile-header">
        <div className="profile-avatar">
          {info.player_name ? info.player_name[0] : info.name[0]}
        </div>
        <div className="profile-info">
          <h2>{info.player_name || info.name}</h2>
          <div>
            <b>Age:</b> {info.age} &nbsp;|&nbsp; <b>Position:</b> {info.position} &nbsp;|&nbsp; <b>Team:</b> {info.team}
          </div>
        </div>
      </div>
      <div className="dashboard-graphs">
        <div>
          <h4>Goals per Season</h4>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={career}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="season" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="goals" stroke="#0073b1" activeDot={{ r: 8 }} dot={<CustomDot />} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h4>Assists per Season</h4>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={career}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="season" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="assists" stroke="#28a745" activeDot={{ r: 8 }} dot={<CustomDot />} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h4>Matches per Season</h4>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={career}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="season" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="mp" stroke="#ff9800" activeDot={{ r: 8 }} dot={<CustomDot />} />
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
              <Line type="monotone" dataKey="minutes" stroke="#e91e63" activeDot={{ r: 8 }} dot={<CustomDot />} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      <button
        className="submit-btn"
        disabled={predicted}
        onClick={async () => {
            const res = await axios.get(`http://localhost:5000/predict/player/${encodeURIComponent(name)}`);
            const pred = res.data.predictions;
            const prob = res.data.probability_playing_next_season;
            const lastSeason = career[career.length-1]?.season;
            const nextStart = lastSeason ? parseInt(lastSeason) + 1 : new Date().getFullYear();
            const nextSeason = `${nextStart}-${nextStart+1}`;
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
          }}
      >
        Predict Next Season
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
            {(probability * 100).toFixed(1)}%
            </span>
        </div>
        )}
    </div>
  );
};

export default PlayerProfile;