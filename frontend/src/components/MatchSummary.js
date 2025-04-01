import React from 'react';
import './MatchSummary.css';

const MatchSummary = ({ summary, keyMoments, loading }) => {
  if (loading) {
    return (
      <div className="summary-loading">
        Analyzing match commentary...
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="summary-placeholder">
        No match summary available. Generate summary first.
      </div>
    );
  }

  return (
    <div className="match-summary">
      <div className="summary-text">
        <h4>Match Summary</h4>
        <p>{summary}</p>
      </div>
      
      {keyMoments && keyMoments.length > 0 && (
        <div className="key-moments">
          <h4>Key Moments</h4>
          <ul>
            {keyMoments.map((moment, index) => (
              <li 
                key={index} 
                className={`moment excitement-${Math.floor(moment.excitement)}`}
              >
                {moment.time && <span className="moment-time">{moment.time}</span>}
                <span className="moment-text">{moment.text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MatchSummary;