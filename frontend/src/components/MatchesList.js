import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'; // Make sure axios is installed
import Cookies from 'js-cookie'; // Import Cookies
import './MatchesList.css'; // Create this CSS file for styling

const StatusTag = ({ status }) => {
    let tagClassName = 'status-tag';
    let tagContent = status;

    // Normalize status to lowercase for consistent matching
    const normalizedStatus = status ? status.toLowerCase().replace(/\s+/g, '_') : 'unknown';

    switch (normalizedStatus) {
        case 'captions_ready':
            tagClassName += ' status-captions-ready';
            // Using a simple text "CC" for the symbol, can be replaced with an SVG icon
            tagContent = <span title="Captions Ready">CC</span>;
            break;
        case 'processing': // Tactical analysis status
            tagClassName += ' status-processing';
            tagContent = 'Processing';
            break;
        case 'pending': // Tactical analysis status
            tagClassName += ' status-pending';
            tagContent = 'Pending';
            break;
        case 'completed': // Tactical analysis status
            tagClassName += ' status-completed';
            tagContent = 'Analyzed';
            break;
        case 'failed': // Tactical analysis status or general error
            tagClassName += ' status-failed';
            tagContent = 'Failed';
            break;
        case 'not_started': // Tactical analysis status
            tagClassName += ' status-not-started';
            tagContent = 'Not Started';
            break;
        default:
            tagClassName += ' status-unknown';
            tagContent = status || 'Unknown'; // Display the original status if not specifically handled
            break;
    }

    return <span className={tagClassName}>{tagContent}</span>;
};

function MatchesList() {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchMatches = async () => {
            setLoading(true);
            setError('');
            try {
                const token = Cookies.get('token');
                if (!token) {
                    setError('Authentication token not found. Please log in.');
                    setLoading(false);
                    return;
                }
                const response = await axios.get('http://localhost:5000/api/matches', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                setMatches(response.data);
            } catch (err) {
                console.error("Error fetching matches:", err);
                // Check if the error is from the server response or a network issue
                if (err.response && err.response.data && err.response.data.message) {
                    setError(err.response.data.message);
                } else if (err.message) {
                    setError(err.message);
                } else {
                    setError('Failed to load matches. Please try again later.');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchMatches();
    }, []);

    return (
        <div className="matches-list-container">
            <h2 style={{color: 'black'}}>Matches</h2>
            <Link to="/matches/upload" className="upload-match-link">Upload New Match</Link>

            {loading && <p>Loading matches...</p>}
            {error && <p className="error-message">{error}</p>}

            {!loading && !error && (
                <ul className="matches-list">
                    {matches.length === 0 ? (
                        <p>No matches uploaded yet.</p>
                    ) : (
                        matches.map(match => (
                            <li key={match.id} className="match-item">
                                <div className="match-info">
                                    <Link to={`/matches/${match.id}`}>
                                        <h3>{match.title || `${match.team1_name} vs ${match.team2_name}`}</h3>
                                        <p>{match.team1_name} {match.team1_score ?? ''} - {match.team2_score ?? ''} {match.team2_name}</p>
                                        <p>Competition: {match.competition || 'N/A'}</p>
                                        <p>Date: {match.match_date || 'N/A'}</p>
                                        <div className="match-status-container">
                                            <span>Status: </span>
                                            <StatusTag status={match.status} />
                                        </div>
                                        {/* Display error message if status is 'failed' or there's a specific error_message */}
                                        {(match.status && match.status.toLowerCase() === 'failed' && match.error_message) && 
                                            <p className="error-message item-error-message">Error: {match.error_message}</p>}
                                    </Link>
                                </div>
                            </li>
                        ))
                    )}
                </ul>
            )}
        </div>
    );
}

export default MatchesList;
