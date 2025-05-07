import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './PlayerPredictor.css';
import { useNavigate } from 'react-router-dom';

const ExistingPlayerPredictor = () => {
  const [players, setPlayers] = useState([]);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState({ position: '', team: '', age: '' });
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 4;
  const navigate = useNavigate(); 
  useEffect(() => {
    axios.get('http://localhost:5000/players').then(res => setPlayers(res.data));
  }, []);
  useEffect(() => {
    setPage(1);
  }, [search, filter]);
  const filteredPlayers = players.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) &&
    (filter.position ? p.position === filter.position : true) &&
    (filter.team ? p.team === filter.team : true) &&
    (filter.age ? String(p.age) === filter.age : true)
  );

  const uniquePositions = [...new Set(players.map(p => p.position))].sort((a, b) => a.localeCompare(b));
    const uniqueTeams = [...new Set(players.map(p => p.team))].sort((a, b) => a.localeCompare(b));
    const uniqueAges = [...new Set(players.map(p => p.age))]
        .filter(age => age !== null && age !== undefined)
        .sort((a, b) => a - b);

  const predict = async (playerName) => {
    setLoading(true);
    setResult(null);
    setSelected(playerName);
    try {
      const res = await axios.get(`http://localhost:5000/predict/player/${encodeURIComponent(playerName)}`);
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.response?.data?.error || 'Prediction failed' });
    }
    setLoading(false);
  };

  return (
    <div className="predictor-container">
      <h2>Predict Existing Player</h2>
      <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap'}}>
        <input
          type="text"
          placeholder="Search by name"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="input"
          style={{minWidth: 180}}
        />
        <select value={filter.position} onChange={e => setFilter(f => ({...f, position: e.target.value}))}>
          <option value="">All Positions</option>
          {uniquePositions.map(pos => <option key={pos} value={pos}>{pos}</option>)}
        </select>
        <select value={filter.team} onChange={e => setFilter(f => ({...f, team: e.target.value}))}>
          <option value="">All Teams</option>
          {uniqueTeams.map(team => <option key={team} value={team}>{team}</option>)}
        </select>
        <select value={filter.age} onChange={e => setFilter(f => ({...f, age: e.target.value}))}>
          <option value="">All Ages</option>
          {uniqueAges.map(age => <option key={age} value={age}>{age}</option>)}
        </select>
      </div>
      <div style={{maxHeight: 400, overflowY: 'auto', marginBottom: '1.5rem'}}>
      {filteredPlayers
        .slice((page - 1) * pageSize, page * pageSize)
        .map(p => (
            <div
            key={p.name}
            className={`season-row`}
            style={{
                cursor: 'pointer',
                border: selected === p.name ? '2px solid #0073b1' : undefined,
                marginBottom: 12,
                background: '#f8fafc'
            }}
            onClick={() => navigate(`/player/${encodeURIComponent(p.name)}`)}
            >
            <div>
                <div style={{fontWeight: 600, fontSize: '1.1rem'}}>{p.name}</div>
                <div style={{fontSize: '0.95rem', color: '#555'}}>
                Age: {p.age} &nbsp;|&nbsp; Position: {p.position} &nbsp;|&nbsp; Team: {p.team}
                </div>
            </div>
            </div>
        ))
        }
      </div>
      <div style={{display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '1rem'}}>
      <button
            className="pagination-btn"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            >
            Previous
            </button>
            <span>Page {page} of {Math.ceil(filteredPlayers.length / pageSize)}</span>
            <button
            className="pagination-btn"
            onClick={() => setPage(p => p < Math.ceil(filteredPlayers.length / pageSize) ? p + 1 : p)}
            disabled={page >= Math.ceil(filteredPlayers.length / pageSize)}
            >
            Next
            </button>
        </div>
      {loading && <div>Loading prediction...</div>}
      {result && (
        <div className="prediction-result">
          {result.error ? (
            <div className="error">{result.error}</div>
          ) : (
            <>
              <h4>Prediction for {result.player_name}</h4>
              <ul>
                <li><b>Goals:</b> {result.predictions.goals.toFixed(1)}</li>
                <li><b>Assists:</b> {result.predictions.assists.toFixed(1)}</li>
                <li><b>Matches:</b> {result.predictions.matches.toFixed(1)}</li>
                <li><b>Minutes:</b> {result.predictions.minutes.toFixed(1)}</li>
                <li><b>Probability Playing Next Season:</b> {(result.probability_playing_next_season * 100).toFixed(1)}%</li>
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ExistingPlayerPredictor;