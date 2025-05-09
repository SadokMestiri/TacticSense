import React from 'react';
import { Link } from 'react-router-dom';
import './AnalysisHubMain.css'; // We'll create this CSS file next

function AnalysisHubMain() {
    return (
        <div className="analysis-hub-main-container">
            <header className="hub-main-header">
                <h1>Analysis Hub</h1>
                <p className="hub-main-subtitle">Your central dashboard for tactical insights and player analytics.</p>
            </header>
            <div className="hub-main-navigation-grid">
                <Link to="/analysis-hub/matches" className="hub-tool-card">
                    <div className="tool-card-icon">
                        {/* Placeholder for an icon - e.g., a clipboard or tactics board icon */}
                        <span role="img" aria-label="Tactical Match Analysis Icon">📊</span>
                    </div>
                    <h2>Tactical Match Analysis</h2>
                    <p>Review match footage, tactical overlays, and heatmaps.</p>
                </Link>

                <Link to="/analysis-hub/players" className="hub-tool-card">
                    <div className="tool-card-icon">
                        {/* Placeholder for an icon - e.g., a player or graph icon */}
                        <span role="img" aria-label="Player Performance Icon">📈</span>
                    </div>
                    <h2>Player Performance & Prediction</h2>
                    <p>Analyze player statistics and future performance forecasts.</p>
                </Link>
                
                {/* Add more tool cards here as new features are developed */}
            </div>
        </div>
    );
}

export default AnalysisHubMain;