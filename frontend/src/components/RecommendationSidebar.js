import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RecommendationSidebar.css';

const RecommendationSidebar = ({ token }) => {
  const [clubRecs, setClubRecs] = useState([]);
  const [playerRecs, setPlayerRecs] = useState([]);
  const [agencyRecs, setagencyRecs] = useState([]);
  const [clubsToPlayerRecs, setClubsToPlayerRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    clubs: false,
    players: false,
    agencies: false,
    clubsToPlayer: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        // Fetch club recommendations to agency
        const clubResponse = await axios.post(
          'http://localhost:5000/api/recommend/clubs/toagency',
          { top_n: 3 },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setClubRecs(clubResponse.data.recommendations || clubResponse.data); // Fallback to direct data
  
        // Fetch player recommendations to agency
        const playerResponse = await axios.post(
          'http://localhost:5000/api/recommend/players/toagency',
          { top_n: 3 },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setPlayerRecs(playerResponse.data.recommendations || playerResponse.data);
  
        // Fetch agency recommendations to player
        const agencyResponse = await axios.post(
          'http://localhost:5000/api/recommend/agencies/toplayer',
          { top_n: 3 },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setagencyRecs(agencyResponse.data.recommendations || agencyResponse.data);
  
        // Fetch club recommendations to player
        const clubsToPlayerResponse = await axios.post(
          'http://localhost:5000/api/recommend/clubs/toplayer',
          { top_n: 3 },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setClubsToPlayerRecs(clubsToPlayerResponse.data.recommendations || clubsToPlayerResponse.data);
  
      } catch (err) {
        setError(err.response?.data?.error || err.message);
        console.error("Recommendation error:", err.response?.data);
      } finally {
        setLoading(false);
      }
    };
  
    fetchRecommendations();
  }, [token]);

  if (loading) return <div className="loading">Loading recommendations...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="recommendation-sidebar">
      {/* Club Recommendations to agency */}
      {clubRecs.length > 0 && (
        <div className="recommendation-section">
          <div className="recommendation-header" onClick={() => toggleSection('clubs')}>
            <h3>Recommended Clubs for You</h3>
            <button className="dropdown-toggle">
              {expandedSections.clubs ? '−' : '+'}
            </button>
          </div>
          <div className={`dropdown-container ${expandedSections.clubs ? 'expanded' : ''}`}>
            {clubRecs.map((rec, index) => (
              <div key={`club-${index}`} className="recommendation-item">
                <a href={`/user/${encodeURIComponent(rec.club)}`} target="_blank" rel="noopener noreferrer">{rec.club}</a>
                <span>Score: {rec.score.toFixed(5)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Player Recommendations to agency */}
      {playerRecs.length > 0 && (
        <div className="recommendation-section">
          <div className="recommendation-header" onClick={() => toggleSection('players')}>
            <h3>Recommended Players for You</h3>
            <button className="dropdown-toggle">
              {expandedSections.players ? '−' : '+'}
            </button>
          </div>
          <div className={`dropdown-container ${expandedSections.players ? 'expanded' : ''}`}>
            {playerRecs.map((rec, index) => (
              <div key={`player-${index}`} className="recommendation-item">
                <a href={`/user/${encodeURIComponent(rec.player)}`} target="_blank" rel="noopener noreferrer">{rec.player}</a>
                <span>Score: {rec.score.toFixed(5)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* agency Recommendations to Player */}
      {agencyRecs.length > 0 && (
        <div className="recommendation-section">
          <div className="recommendation-header" onClick={() => toggleSection('agencies')}>
            <h3>Recommended Agencies for You</h3>
            <button className="dropdown-toggle">
              {expandedSections.agenies ? '−' : '+'}
            </button>
          </div>
          <div className={`dropdown-container ${expandedSections.agencies ? 'expanded' : ''}`}>
            {agencyRecs.map((rec, index) => (
              <div key={`agency-${index}`} className="recommendation-item">
                <a href={`/user/${encodeURIComponent(rec.agency)}`} target="_blank" rel="noopener noreferrer">{rec.agency}</a>
                <span>Score: {rec.score.toFixed(5)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/*  Club Recommendations to Player */}
      {clubsToPlayerRecs.length > 0 && (
        <div className="recommendation-section">
          <div className="recommendation-header" onClick={() => toggleSection('clubsToPlayer')}>
            <h3>Recommended Clubs for You </h3>
            <button className="dropdown-toggle">
              {expandedSections.clubsToPlayer ? '−' : '+'}
            </button>
          </div>
          <div className={`dropdown-container ${expandedSections.clubsToPlayer ? 'expanded' : ''}`}>
            {clubsToPlayerRecs.map((rec, index) => (
              <div key={`clubtoplayer-${index}`} className="recommendation-item">
                <a href={`/user/${encodeURIComponent(rec.club)}`} target="_blank" rel="noopener noreferrer">{rec.club}</a>
                <span>Score: {rec.score.toFixed(5)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationSidebar;
