import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './PlayerPredictor.css'; // Assuming styles are shared or specific
import { useNavigate, Link } from 'react-router-dom';

const ExistingPlayerPredictor = () => {
  const [players, setPlayers] = useState([]);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState({ position: '', team: '', age: '' });
  const [page, setPage] = useState(1);
  const pageSize = 10; // Increased page size for better view with sidebar
  const navigate = useNavigate();
  const [loadingPlayers, setLoadingPlayers] = useState(true);
  const [errorPlayers, setErrorPlayers] = useState('');

  useEffect(() => {
    setLoadingPlayers(true);
    setErrorPlayers('');
    axios.get('http://localhost:5000/players') // Ensure this is your correct API endpoint
      .then(res => {
        setPlayers(res.data);
      })
      .catch(err => {
        console.error("Error fetching players list:", err);
        setErrorPlayers('Failed to load players. Please try again.');
      })
      .finally(() => {
        setLoadingPlayers(false);
      });
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

  const uniquePositions = [...new Set(players.map(p => p.position).filter(Boolean))].sort((a, b) => a.localeCompare(b));
  const uniqueTeams = [...new Set(players.map(p => p.team).filter(Boolean))].sort((a, b) => a.localeCompare(b));
  const uniqueAges = [...new Set(players.map(p => p.age))]
        .filter(age => age !== null && age !== undefined)
        .sort((a, b) => a - b);

  return (
    <div className="predictor-container existing-players-layout"> {/* Added class for layout */}
      <div className="existing-players-main-content">
        <h2>Player Database & Predictions</h2>
      
        <div className="filters-container" style={{display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap'}}>
          <input
            type="text"
            placeholder="Search by name"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input"
            style={{minWidth: 180, flexGrow: 1}}
          />
          <select value={filter.position} onChange={e => setFilter(f => ({...f, position: e.target.value}))} className="filter-select">
            <option value="">All Positions</option>
            {uniquePositions.map(pos => <option key={pos} value={pos}>{pos}</option>)}
          </select>
          <select value={filter.team} onChange={e => setFilter(f => ({...f, team: e.target.value}))} className="filter-select">
            <option value="">All Teams</option>
            {uniqueTeams.map(team => <option key={team} value={team}>{team}</option>)}
          </select>
          <select value={filter.age} onChange={e => setFilter(f => ({...f, age: e.target.value}))} className="filter-select">
            <option value="">All Ages</option>
            {uniqueAges.map(age => <option key={age} value={age}>{age}</option>)}
          </select>
        </div>

        {loadingPlayers && <p>Loading players...</p>}
        {errorPlayers && <p className="error-message">{errorPlayers}</p>}
        
        {!loadingPlayers && !errorPlayers && (
          <>
            <div className="players-list-container" style={{maxHeight: 500, overflowY: 'auto', marginBottom: '1.5rem'}}>
            {filteredPlayers.length > 0 ? (
              filteredPlayers
                .slice((page - 1) * pageSize, page * pageSize)
                .map(p => (
                    <div
                      key={p.name}
                      className="player-list-item" // Changed class for better targeting
                      onClick={() => navigate(`/analysis-hub/players/${encodeURIComponent(p.name)}`)}
                    >
                      <div className="player-item-info">
                          <div className="player-item-name">{p.name}</div>
                          <div className="player-item-details">
                            Age: {p.age || 'N/A'} &nbsp;|&nbsp; Position: {p.position || 'N/A'} &nbsp;|&nbsp; Team: {p.team || 'N/A'}
                          </div>
                      </div>
                    </div>
                ))
              ) : (
                <p>No players found matching your criteria.</p>
              )}
            </div>

            {filteredPlayers.length > pageSize && (
              <div className="pagination-controls" style={{display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '1rem'}}>
              <button
                    className="pagination-btn"
                    onClick={() => setPage(pg => Math.max(1, pg - 1))}
                    disabled={page === 1}
                    >
                    Previous
                    </button>
                    <span>Page {page} of {Math.ceil(filteredPlayers.length / pageSize)}</span>
                    <button
                    className="pagination-btn"
                    onClick={() => setPage(pg => pg < Math.ceil(filteredPlayers.length / pageSize) ? pg + 1 : pg)}
                    disabled={page >= Math.ceil(filteredPlayers.length / pageSize)}
                    >
                    Next
                    </button>
                </div>
            )}
          </>
        )}
      </div>

      <div className="existing-players-sidebar">
        <div className="add-player-prompt">
          <h4>Can't find a player?</h4>
          <p>If a player is not in our database, you can add their details for a new prediction.</p>
          <Link to="/analysis-hub/players/new" className="add-player-link">
            Add New Player
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ExistingPlayerPredictor;