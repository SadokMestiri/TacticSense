import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import './MatchSummary.css';

function MatchSummary({ summary, onGenerate, loading, captionsReady }) {
    const [ttsLoading, setTtsLoading] = useState(false);
    const [ttsError, setTtsError] = useState('');
    const [audioUrl, setAudioUrl] = useState('');

    const handleTTS = async () => {
        if (!summary || ttsLoading) return;
        setTtsLoading(true);
        setTtsError('');
        setAudioUrl('');
        try {
            const token = Cookies.get('token');
            if (!token) {
                setTtsError('Authentication required. Please log in.');
                setTtsLoading(false);
                return;
            }
            const response = await axios.post(
                'http://localhost:5000/api/tts',
                { text: summary },
                { headers: { Authorization: `Bearer ${token}` } }
            );
    
            // Adjust the audio_url to include the correct backend base URL
            const backendBaseUrl = 'http://localhost:5000';
            const adjustedAudioUrl = response.data.audio_url.startsWith('/')
                ? `${backendBaseUrl}${response.data.audio_url}`
                : response.data.audio_url;
    
            setAudioUrl(adjustedAudioUrl);
        } catch (err) {
            console.error('Error generating TTS:', err);
            setTtsError(err.response?.data?.error || 'Failed to generate TTS.');
        } finally {
            setTtsLoading(false);
        }
    };

    return (
        <div className="match-summary">
            <h3>Match Summary</h3>
            {summary ? (
                <p>{summary}</p>
            ) : (
                <p>No summary available. Generate one below.</p>
            )}
            <div className="summary-actions">
                <button
                    onClick={onGenerate}
                    disabled={loading || !captionsReady}
                    className="btn btn-primary"
                >
                    {loading ? 'Generating...' : 'Regenerate Summary'}
                </button>
                {summary && (
                    <button
                        onClick={handleTTS}
                        disabled={ttsLoading}
                        className="btn btn-secondary"
                    >
                        {ttsLoading ? 'Generating TTS...' : 'Play Summary'}
                    </button>
                )}
            </div>
            {ttsError && <p className="error-message">{ttsError}</p>}
            {audioUrl && (
                <audio controls>
                    <source src={audioUrl} type="audio/mpeg" />
                    Your browser does not support the audio element.
                </audio>
            )}
        </div>
    );
}

export default MatchSummary;