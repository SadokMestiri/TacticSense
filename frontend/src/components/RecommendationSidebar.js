import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RecommendationSidebar.css';

const RecommendationSidebar = ({ token }) => {
  const [clubRecs, setClubRecs] = useState([]);
  const [playerRecs, setPlayerRecs] = useState([]);
  const [agencyRecs, setagencyRecs] = useState([]);
  const [clubsToPlayerRecs, setClubsToPlayerRecs] = useState([]);
  const [playersToClubRecs, setPlayersToClubRecs] = useState([]);
  const [agenciesToClubRecs, setAgenciesToClubRecs] = useState([]);
  const [staffToClubRecs, setStaffToClubRecs] = useState([]);
  const [clubsToStaffRecs, setClubsToStaffRecs] = useState([]);
  const [agentsToAgencyRecs, setAgentsToAgencyRecs] = useState([]);
  const [agenciesToAgentRecs, setAgenciesToAgentRecs] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    clubs: false,
    players: false,
    agencies: false,
    clubsToPlayer: false,
    playersToClub: false,
    agenciesToClub: false,
    staffToClub: false,
    clubsToStaff: false,
    agentsToAgency: false,
    agenciesToAgent: false
    
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const scoreToStars = (score) => {
    // Round to the nearest 0.5
    const roundedScore = Math.round(score * 2) / 2;
  
    // Clamp the score to a range between 0 and 5
    const clampedScore = Math.max(0, Math.min(5, roundedScore));
  
    // If the score is below 2.5, double the stars
    const adjustedScore = clampedScore < 2.5 ? clampedScore * 2 : clampedScore;
  
    // Determine the number of full stars (integer part of the adjusted score)
    const fullStars = Math.floor(adjustedScore);
    // Check if there's a half star
    const halfStar = adjustedScore % 1 >= 0.5 ? 1 : 0;
  
    // Return stars, including half stars
    return '★'.repeat(fullStars) + (halfStar ? '⯪' : '') + '☆'.repeat(5 - fullStars - halfStar);
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

        // Fetch players recommendations to club
        const playersToClubResponse = await axios.post(
          'http://localhost:5000/api/recommend/players/toclub',
          { top_n: 3 },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setPlayersToClubRecs(playersToClubResponse.data.recommendations || playersToClubResponse.data);


        // Fetch agency recommendations to club
        const agenciesToClubResponse = await axios.post(
        'http://localhost:5000/api/recommend/agencies/toclub',
        { top_n: 3 },
        { headers: { Authorization: `Bearer ${token}` } }
        );
        setAgenciesToClubRecs(agenciesToClubResponse.data.recommendations || agenciesToClubResponse.data);

        // Fetch staff recommendations to club
        
    const staffToClubResponse = await axios.post(
      'http://localhost:5000/api/recommend/staff/toclub',
      { top_n: 3 },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setStaffToClubRecs(staffToClubResponse.data);


    // Fetch clubs to staff recommendations
    const clubsToStaffResponse = await axios.post(
      'http://localhost:5000/api/recommend/clubs/tostaff',
      { top_n: 3 },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setClubsToStaffRecs(clubsToStaffResponse.data.recommendations || clubsToStaffResponse.data);

    // Fetch agents to agency recommendations
const agentsToAgencyResponse = await axios.post(
  'http://localhost:5000/api/recommend/agents/toagency',
  { top_n: 3 },
  { headers: { Authorization: `Bearer ${token}` } }
);
setAgentsToAgencyRecs(agentsToAgencyResponse.data);

// Fetch agencies to agent recommendations
const agenciesToAgentResponse = await axios.post(
  'http://localhost:5000/api/recommend/agencies/toagent',
  { top_n: 3 },
  { headers: { Authorization: `Bearer ${token}` } }
);
setAgenciesToAgentRecs(agenciesToAgentResponse.data);
        
  
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
                <span>Stars: {scoreToStars(rec.score)}</span>
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
                <span>Stars: {scoreToStars(rec.score)}</span>
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
              {expandedSections.agencies ? '−' : '+'}
            </button>
          </div>
          <div className={`dropdown-container ${expandedSections.agencies ? 'expanded' : ''}`}>
            {agencyRecs.map((rec, index) => (
              <div key={`agency-${index}`} className="recommendation-item">
                <a href={`/user/${encodeURIComponent(rec.agency)}`} target="_blank" rel="noopener noreferrer">{rec.agency}</a>
                <span>Score: {rec.score.toFixed(5)}</span>
                <span>Stars: {scoreToStars(rec.score)}</span>
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
                <span>Stars: {scoreToStars(rec.score)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/*  Players Recommendations to club */}
      {playersToClubRecs.length > 0 && (
        <div className="recommendation-section">
          <div className="recommendation-header" onClick={() => toggleSection('playersToClub')}>
            <h3>Recommended Players for Your Club </h3>
            <button className="dropdown-toggle">
              {expandedSections.playersToClub ? '−' : '+'}
            </button>
          </div>
          <div className={`dropdown-container ${expandedSections.playersToClub ? 'expanded' : ''}`}>
            {playersToClubRecs.map((rec, index) => (
              <div key={`players-to-club-${index}`} className="recommendation-item">
                <a href={`/user/${encodeURIComponent(rec.player)}`} target="_blank" rel="noopener noreferrer">{rec.player}</a>
                <span>Score: {rec.score.toFixed(5)}</span>
                <span>Stars: {scoreToStars(rec.score)}</span>
              </div>
            ))}
          </div>
        </div>
      )}


      {/*  Agencies Recommendations to club */}
      {agenciesToClubRecs.length > 0 && (
        <div className="recommendation-section">
          <div className="recommendation-header" onClick={() => toggleSection('agenciesToClub')}>
            <h3>Recommended Agencies for Your Club</h3>
            <button className="dropdown-toggle">
              {expandedSections.agenciesToClub ? '−' : '+'}
            </button>
          </div>
          <div className={`dropdown-container ${expandedSections.agenciesToClub ? 'expanded' : ''}`}>
            {agenciesToClubRecs.map((rec, index) => (
              <div key={`agencies-to-club-${index}`} className="recommendation-item">
                <a href={`/user/${encodeURIComponent(rec.agency)}`} target="_blank" rel="noopener noreferrer">{rec.agency}</a>
                <span>Score: {rec.score.toFixed(5)}</span>
                <span>Stars: {scoreToStars(rec.score)}</span>
              </div>
            ))}
          </div>
        </div>
      )}


      {/* Staff Recommendations to Club */}
{staffToClubRecs.length > 0 && (
  <div className="recommendation-section">
    <div className="recommendation-header" onClick={() => toggleSection('staffToClub')}>
      <h3>Recommended Staff for Your Club</h3>
      <button className="dropdown-toggle">{expandedSections.staffToClub ? '−' : '+'}</button>
    </div>
    <div className={`dropdown-container ${expandedSections.staffToClub ? 'expanded' : ''}`}>
      {staffToClubRecs.map((rec, index) => (
        <div key={`staff-to-club-${index}`} className="recommendation-item">
          <a href={`/user/${encodeURIComponent(rec.staff)}`} target="_blank" rel="noopener noreferrer">{rec.staff}</a>
          <span>Score: {rec.score.toFixed(5)}</span>
          <span>Stars: {scoreToStars(rec.score)}</span>
        </div>
      ))}
    </div>
  </div>
)}

{/* Clubs Recommendations to Staff */}
{clubsToStaffRecs.length > 0 && (
  <div className="recommendation-section">
    <div className="recommendation-header" onClick={() => toggleSection('clubsToStaff')}>
      <h3>Recommended Clubs for You (Staff)</h3>
      <button className="dropdown-toggle">{expandedSections.clubsToStaff ? '−' : '+'}</button>
    </div>
    <div className={`dropdown-container ${expandedSections.clubsToStaff ? 'expanded' : ''}`}>
      {clubsToStaffRecs.map((rec, index) => (
        <div key={`clubs-to-staff-${index}`} className="recommendation-item">
          <a href={`/user/${encodeURIComponent(rec.club)}`} target="_blank" rel="noopener noreferrer">{rec.club}</a>
          <span>Score: {rec.score.toFixed(5)}</span>
          <span>Stars: {scoreToStars(rec.score)}</span>
        </div>
      ))}
    </div>
  </div>
)}

{/* Agents Recommendations to Agency */}
{agentsToAgencyRecs.length > 0 && (
  <div className="recommendation-section">
    <div className="recommendation-header" onClick={() => toggleSection('agentsToAgency')}>
      <h3>Recommended Agents for Your Agency</h3>
      <button className="dropdown-toggle">{expandedSections.agentsToAgency ? '−' : '+'}</button>
    </div>
    <div className={`dropdown-container ${expandedSections.agentsToAgency ? 'expanded' : ''}`}>
      {agentsToAgencyRecs.map((rec, index) => (
        <div key={`agents-to-agency-${index}`} className="recommendation-item">
          <a href={`/user/${encodeURIComponent(rec.agent)}`} target="_blank" rel="noopener noreferrer">{rec.agent}</a>
          <span>Score: {rec.score.toFixed(5)}</span>
          <span>Stars: {scoreToStars(rec.score)}</span>
        </div>
      ))}
    </div>
  </div>
)}

{/* Agencies Recommendations to Agent */}
{agenciesToAgentRecs.length > 0 && (
  <div className="recommendation-section">
    <div className="recommendation-header" onClick={() => toggleSection('agenciesToAgent')}>
      <h3>Recommended Agencies for You (Agent)</h3>
      <button className="dropdown-toggle">{expandedSections.agenciesToAgent ? '−' : '+'}</button>
    </div>
    <div className={`dropdown-container ${expandedSections.agenciesToAgent ? 'expanded' : ''}`}>
      {agenciesToAgentRecs.map((rec, index) => (
        <div key={`agencies-to-agent-${index}`} className="recommendation-item">
          <a href={`/user/${encodeURIComponent(rec.agency)}`} target="_blank" rel="noopener noreferrer">{rec.agency}</a>
          <span>Score: {rec.score.toFixed(5)}</span>
          <span>Stars: {scoreToStars(rec.score)}</span>
        </div>
      ))}
    </div>
  </div>
)}
   

    </div>
  );
};

export default RecommendationSidebar;
