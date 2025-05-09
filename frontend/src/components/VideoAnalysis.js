import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie'; // Using Cookies
import CustomVideoPlayer from './CustomVideoPlayer';
import TranscriptDisplay from './TranscriptDisplay';
import MatchSummary from './MatchSummary';
import './VideoAnalysis.css';

function VideoAnalysis() {
    const { matchId } = useParams();
    const navigate = useNavigate();
    const [matchData, setMatchData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [captions, setCaptions] = useState([]);
    const [showTranscript, setShowTranscript] = useState(false); // Start false
    const [summary, setSummary] = useState('');
    const [loadingSummary, setLoadingSummary] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);

    const fetchMatchData = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const token = Cookies.get('token');
            if (!token) {
                navigate('/login');
                return;
            }
            const response = await axios.get(`http://localhost:5000/api/matches/${matchId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setMatchData(response.data);
            setSummary(response.data.summary || '');
        } catch (err) {
            console.error("Error fetching match data:", err);
            setError(`Failed to load match data: ${err.response?.data?.error || err.message}`);
            if (err.response?.status === 401) {
                navigate('/login');
            }
        } finally {
            setLoading(false);
        }
    }, [matchId, navigate]);

    useEffect(() => {
        fetchMatchData();
    }, [fetchMatchData]);

    const handleCaptionsLoaded = useCallback((loadedCaptions, isUserToggleAction = false) => {
        // isUserToggleAction: true if this call is a direct result of user clicking CC in player,
        //                     which means the player's internal state for showing captions has changed.
        //                     false if captions were loaded programmatically (e.g., on initial page load from srtUrl).
        console.log("VideoAnalysis: handleCaptionsLoaded called. Captions count:", loadedCaptions ? loadedCaptions.length : 0, "Is user toggle:", isUserToggleAction);

        if (loadedCaptions && loadedCaptions.length > 0) {
            setCaptions(loadedCaptions);
            if (isUserToggleAction) {
                // If user toggled CC ON in the player and captions loaded, show the transcript section.
                setShowTranscript(true);
            }
            // If !isUserToggleAction (e.g., initial silent load), captions are set,
            // but showTranscript remains its current state (initially false).
            // User must click header or player CC to expand.
        } else {
            // No captions loaded, or CC was toggled OFF in the player.
            setCaptions([]);
            setShowTranscript(false); // Always collapse/hide if no captions or CC is OFF.
        }
    }, []);


    const handleTimeUpdate = (time) => {
        setCurrentTime(time);
    };

    const handleGenerateSummary = async () => {
        if (!matchId || loadingSummary) return;
        setLoadingSummary(true);
        setError('');
        try {
            const token = Cookies.get('token');
            if (!token) {
                navigate('/login');
                setLoadingSummary(false);
                return;
            }
            // The backend endpoint /api/matches/${matchId}/summarize is called.
            // If "it loaded the model and stopped", this is likely a backend issue:
            // - The summarization task might be hanging or taking too long (timeout).
            // - There could be an unhandled error in the backend summarization script.
            // - Resource limitations on the server when loading/running the ML model.
            // The frontend code below for making the request is standard.
            const response = await axios.post(`http://localhost:5000/api/matches/${matchId}/summarize`, {}, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setSummary(response.data.summary);
        } catch (err) {
            console.error("Error generating summary:", err);
            setError(err.response?.data?.error || 'Failed to generate summary. The process might have failed on the server.');
            if (err.response?.status === 401) {
                navigate('/login');
            }
        } finally {
            setLoadingSummary(false);
        }
    };
    
    const captionsAvailable = captions && captions.length > 0;
    const canGenerateSummary = captionsAvailable || (matchData && (matchData.status === 'captions_ready' || matchData.status === 'analysis_complete'));

    const toggleTranscriptDisplay = () => {
        if (captionsAvailable) {
            setShowTranscript(prev => !prev);
        }
    };


    if (loading) return <div className="loading-indicator">Loading match data...</div>;
    if (error && !matchData) return <p className="error-message" style={{ padding: '20px' }}>{error}</p>;
    if (!matchData) return <div className="loading-indicator" style={{ padding: '20px' }}>Match data not found.</div>;

    let videoUrlToPlay = matchData.captioned_video_url || matchData.video_url;
    let srtUrlForPlayer = matchData.srt_url;

    const baseUrl = process.env.REACT_APP_BASE_URL || '';

    if (videoUrlToPlay && !videoUrlToPlay.startsWith('http')) {
        videoUrlToPlay = `${baseUrl}${videoUrlToPlay.startsWith('/') ? '' : '/'}${videoUrlToPlay}`;
    }
    if (srtUrlForPlayer && !srtUrlForPlayer.startsWith('http')) {
        srtUrlForPlayer = `${baseUrl}${srtUrlForPlayer.startsWith('/') ? '' : '/'}${srtUrlForPlayer}`;
    }

    return (
        <div className="video-analysis-container">
            <div className="video-analysis-header">
            <div>
                <h2>{matchData.title || `${matchData.team1_name || 'Team 1'} vs ${matchData.team2_name || 'Team 2'}`}</h2>
                <p>{matchData.competition || 'N/A'} - {matchData.match_date || 'N/A'}</p>
                <p>Match Status: <span className={`status-${matchData.status}`}>{matchData.status}</span></p>
                {matchData.tactical_analysis_status && (matchData.tactical_analysis_status === 'processing' || matchData.tactical_analysis_status === 'pending') && (
                    <p className="tactical-processing-status">
                        Tactical Analysis: {matchData.tactical_analysis_status}
                        <span className="loading-dots">
                            <span>.</span><span>.</span><span>.</span>
                        </span>
                    </p>
                )}
                {matchData.tactical_analysis_status && matchData.tactical_analysis_status !== 'processing' && matchData.tactical_analysis_status !== 'pending' && matchData.tactical_analysis_status !== 'not_started' && (
                     <p>Tactical Analysis Status: <span className={`status-tactical-${matchData.tactical_analysis_status}`}>{matchData.tactical_analysis_status}</span></p>
                )}
            </div>
                <div className="header-buttons">
                    {matchData.status === 'analysis_complete' && (
                        <Link to={`/analysis-hub/matches/${matchId}/analysis`} className="btn btn-outline-primary analysis-hub-button">
                            View Tactical Analysis Hub
                        </Link>
                    )}
                    <Link to={`/analysis-hub/matches/${matchId}/analysis`} className="btn btn-primary analyze-button">
                        Analyze
                    </Link>
                </div>
            </div>
    
            {error && <p className="error-message" style={{ margin: '0 20px 10px 20px' }}>{error}</p>}
            {matchData.status === 'error' && matchData.error_message && (!error || !error.includes(matchData.error_message)) &&
                <p className="error-message" style={{ margin: '0 20px 10px 20px' }}>Processing Error: {matchData.error_message}</p>}
    
            <div className="analysis-layout">
                <div className="video-player-section">
                    {videoUrlToPlay ? (
                        <CustomVideoPlayer
                            videoUrl={videoUrlToPlay}
                            srtUrl={srtUrlForPlayer}
                            matchId={matchId}
                            onCaptionsLoaded={handleCaptionsLoaded}
                            onTimeUpdate={handleTimeUpdate}
                        />
                    ) : (
                        <div className="video-container-loader">
                            <p>Video not available for this match.</p>
                        </div>
                    )}
                </div>
    
                <div className="analysis-sidebar">
                    <MatchSummary
                        summary={summary}
                        onGenerate={handleGenerateSummary}
                        loading={loadingSummary}
                        captionsReady={canGenerateSummary}
                    />
                    <div
                        className={`transcript-section ${showTranscript && captionsAvailable ? 'expanded' : 'collapsed'}`}
                    >
                        <div className="transcript-header" onClick={toggleTranscriptDisplay}>
                            <h3>Transcript</h3>
                            {captionsAvailable && <span className="toggle-icon">{showTranscript ? '▼' : '►'}</span>}
                        </div>
    
                        {showTranscript && captionsAvailable ? (
                            <div className="transcript-content">
                                <TranscriptDisplay
                                    captionsData={captions}
                                    currentTime={currentTime}
                                />
                            </div>
                        ) : (
                            <div className="transcript-content" style={{ paddingTop: '10px' }}>
                                {captionsAvailable && !showTranscript && (
                                    <p>Transcript available. Click header to expand.</p>
                                )}
                                {!captionsAvailable && (
                                    <>
                                        {matchData.status === 'uploaded' && (
                                            <p>Video uploaded. Captions will be processed.</p>
                                        )}
                                        {matchData.status === 'processing_captions' && (
                                            <p>Captions are being processed...</p>
                                        )}
                                        {(matchData.status === 'error' || matchData.status === 'transcription_failed') && (
                                            <p>Caption generation failed. Check player CC or error messages.</p>
                                        )}
                                        {['captions_ready', 'analysis_pending', 'processing_analysis', 'analysis_complete'].includes(matchData.status) && !captionsAvailable && (
                                             <p>Captions should be available. Try toggling CC on the video player to load them.</p>
                                         )}
                                        {!captionsAvailable && !['uploaded', 'processing_captions', 'error', 'transcription_failed', 'captions_ready', 'analysis_pending', 'processing_analysis', 'analysis_complete'].includes(matchData.status) && (
                                            <p>No captions loaded. Captions may still be processing or try toggling CC on player.</p>
                                        )}
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default VideoAnalysis;