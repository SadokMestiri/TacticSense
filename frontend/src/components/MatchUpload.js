import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie'; // Import Cookies
import './MatchUpload.css'; // Create this CSS file

function MatchUpload() {
    const [title, setTitle] = useState('');
    const [team1Name, setTeam1Name] = useState('');
    const [team2Name, setTeam2Name] = useState('');
    const [team1Score, setTeam1Score] = useState('');
    const [team2Score, setTeam2Score] = useState('');
    const [matchDate, setMatchDate] = useState('');
    const [competition, setCompetition] = useState('');
    const [videoFile, setVideoFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const navigate = useNavigate();

    const handleFileChange = (event) => {
        setVideoFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError('');
        setSuccess('');

        if (!videoFile) {
            setError('Please select a video file.');
            return;
        }
        if (!team1Name || !team2Name) {
            setError('Team names are required.');
            return;
        }

        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('title', title);
        formData.append('team1_name', team1Name);
        formData.append('team2_name', team2Name);
        
        // --- Add console log --- 
        console.log("Appending scores:", { team1Score, team2Score });
        // --- End console log ---

        formData.append('team1_score', team1Score || '0'); // Ensure scores are sent, even if 0
        formData.append('team2_score', team2Score || '0'); // Ensure scores are sent, even if 0
        formData.append('match_date', matchDate);
        formData.append('competition', competition);

        setUploading(true);

        try {
            const token = Cookies.get('token'); // Use Cookies.get instead of localStorage
            if (!token) {
                setError('Authentication token not found. Please log in again.');
                setUploading(false);
                return;
            }
            const response = await axios.post('http://localhost:5000/api/matches/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${token}` // Use the retrieved token
                }
            });
            setSuccess(`Match uploaded successfully! ID: ${response.data.id}. Transcription started.`);
            // Optionally redirect after a delay
            setTimeout(() => {
                navigate('/matches'); // Redirect to the matches list
            }, 2000);
        } catch (err) {
            console.error("Upload error:", err.response ? err.response.data : err);
            setError(err.response?.data?.error || 'Upload failed. Please check the details and try again.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="match-upload-container">
            <h2>Upload Match Highlight</h2>
            <form onSubmit={handleSubmit} className="match-upload-form">
                {error && <p className="error-message">{error}</p>}
                {success && <p className="success-message">{success}</p>}

                <div className="form-group">
                    <label htmlFor="video">Video File*:</label>
                    <input
                        type="file"
                        id="video"
                        accept="video/mp4,video/mov,video/avi"
                        onChange={handleFileChange}
                        required
                        disabled={uploading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="title">Title (Optional):</label>
                    <input
                        type="text"
                        id="title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        disabled={uploading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="team1Name">Team 1 Name*:</label>
                    <input
                        type="text"
                        id="team1Name"
                        value={team1Name}
                        onChange={(e) => setTeam1Name(e.target.value)}
                        required
                        disabled={uploading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="team2Name">Team 2 Name*:</label>
                    <input
                        type="text"
                        id="team2Name"
                        value={team2Name}
                        onChange={(e) => setTeam2Name(e.target.value)}
                        required
                        disabled={uploading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="team1Score">Team 1 Score:</label>
                    <input
                        type="number"
                        id="team1Score"
                        value={team1Score}
                        onChange={(e) => setTeam1Score(e.target.value)}
                        min="0"
                        disabled={uploading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="team2Score">Team 2 Score:</label>
                    <input
                        type="number"
                        id="team2Score"
                        value={team2Score}
                        onChange={(e) => setTeam2Score(e.target.value)}
                        min="0"
                        disabled={uploading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="matchDate">Match Date:</label>
                    <input
                        type="date"
                        id="matchDate"
                        value={matchDate}
                        onChange={(e) => setMatchDate(e.target.value)}
                        disabled={uploading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="competition">Competition:</label>
                    <input
                        type="text"
                        id="competition"
                        value={competition}
                        onChange={(e) => setCompetition(e.target.value)}
                        disabled={uploading}
                    />
                </div>

                <button type="submit" disabled={uploading}>
                    {uploading ? 'Uploading...' : 'Upload Match'}
                </button>
            </form>
        </div>
    );
}

export default MatchUpload;
