import React, { useState } from 'react';
import axios from 'axios';
import './PlayerPredictor.css'; // Create this for custom styles if needed

const defaultCareer = [
  { season: '2022-2023', age: 22, position: 'MF', matches: 30, minutes: 2200, goals: 5, assists: 7, team: 'Some FC' },
  { season: '2023-2024', age: 23, position: 'MF', matches: 32, minutes: 2500, goals: 8, assists: 10, team: 'Some FC' }
];

const PlayerPredictor = () => {
  const [name, setName] = useState('');
  const [careerStats, setCareerStats] = useState(defaultCareer);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (idx, field, value) => {
    const updated = [...careerStats];
    updated[idx][field] = value;
    setCareerStats(updated);
  };

  const addSeason = () => {
    setCareerStats([...careerStats, { season: '', age: '', position: '', matches: '', minutes: '', goals: '', assists: '', team: '' }]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await axios.post('http://localhost:5000/predict/new_player', {
        name,
        career_stats: careerStats
      });
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.response?.data?.error || 'Prediction failed' });
    }
    setLoading(false);
  };
  const removeSeason = (idx) => {
    if (careerStats.length === 1) return;
    setCareerStats(careerStats.filter((_, i) => i !== idx));
  };

  return (
    <div className="predictor-container">
      <h2>Player Career Prediction</h2>
      <form onSubmit={handleSubmit} className="predictor-form">
        <input
          type="text"
          placeholder="Player Name"
          value={name}
          onChange={e => setName(e.target.value)}
          required
          className="input"
        />
        <h4>Career Stats (edit or add seasons):</h4>
        {careerStats.map((season, idx) => (
            <div key={idx} className="season-row">
                <div className="season-header">Season {idx + 1}</div>
                <label>
                Season
                <input type="text" placeholder="Season" value={season.season} onChange={e => handleChange(idx, 'season', e.target.value)} required />
                </label>
                <label>
                Age
                <input type="number" placeholder="Age" value={season.age} onChange={e => handleChange(idx, 'age', e.target.value)} required />
                </label>
                <label>
                Position
                <input type="text" placeholder="Position" value={season.position} onChange={e => handleChange(idx, 'position', e.target.value)} required />
                </label>
                <label>
                Matches
                <input type="number" placeholder="Matches" value={season.matches} onChange={e => handleChange(idx, 'matches', e.target.value)} required />
                </label>
                <label>
                Minutes
                <input type="number" placeholder="Minutes" value={season.minutes} onChange={e => handleChange(idx, 'minutes', e.target.value)} required />
                </label>
                <label>
                Goals
                <input type="number" placeholder="Goals" value={season.goals} onChange={e => handleChange(idx, 'goals', e.target.value)} required />
                </label>
                <label>
                Assists
                <input type="number" placeholder="Assists" value={season.assists} onChange={e => handleChange(idx, 'assists', e.target.value)} required />
                </label>
                <label>
                Team
                <input type="text" placeholder="Team" value={season.team} onChange={e => handleChange(idx, 'team', e.target.value)} required />
                </label>
                <button
                type="button"
                className="remove-btn"
                onClick={() => removeSeason(idx)}
                style={{position: 'absolute', top: 10, right: 10}}
                disabled={careerStats.length === 1}
                title="Remove this season"
                >
                &times;
                </button>
            </div>
            ))}
        <button type="button" onClick={addSeason} className="add-btn">Add Season</button>
        <button type="submit" className="submit-btn" disabled={loading}>{loading ? 'Predicting...' : 'Predict'}</button>
      </form>
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

export default PlayerPredictor;