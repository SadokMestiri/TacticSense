import React, { useState } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

const TextToSpeech = () => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);
  const [voice, setVoice] = useState('21m00Tcm4TlvDq8ikWAM'); // Default voice

  // List of available voices
  const voices = [
    { id: '21m00Tcm4TlvDq8ikWAM', name: 'English Male (Josh)' },
    { id: 'EXAVITQu4vr4xnSDxMaL', name: 'English Female (Rachel)' },
    { id: 'AZnzlk1XvdvUeBnXmlld', name: 'English Male (Domi)' },
    { id: 'MF3mGyEYCl7XYWbV9V6O', name: 'English Female (Elli)' }
  ];

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleVoiceChange = (e) => {
    setVoice(e.target.value);
  };

  const handleGenerateSpeech = async () => {
    if (!text.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const token = Cookies.get('token');
      const response = await axios.post(
        `${process.env.REACT_APP_BASE_URL}/api/tts`,
        { text, voice_id: voice },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      setAudioUrl(`${process.env.REACT_APP_BASE_URL}${response.data.audio_url}`);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="tts-container">
      <h2>Text to Speech</h2>
      
      <div className="form-group mb-3">
        <label htmlFor="voice-select">Choose a voice:</label>
        <select 
          id="voice-select"
          className="form-control" 
          value={voice} 
          onChange={handleVoiceChange}
        >
          {voices.map(v => (
            <option key={v.id} value={v.id}>{v.name}</option>
          ))}
        </select>
      </div>
      
      <div className="form-group mb-3">
        <label htmlFor="tts-text">Enter text to convert to speech:</label>
        <textarea
          id="tts-text"
          className="form-control"
          rows={5}
          value={text}
          onChange={handleTextChange}
          placeholder="Type your text here..."
        />
      </div>
      
      <button 
        onClick={handleGenerateSpeech} 
        disabled={!text.trim() || loading}
        className="btn btn-primary mb-3"
      >
        {loading ? 'Generating...' : 'Generate Speech'}
      </button>
      
      {error && <div className="alert alert-danger">{error}</div>}
      
      {audioUrl && (
        <div className="audio-player mt-3">
          <h3>Generated Audio</h3>
          <audio controls src={audioUrl} className="w-100" />
          <div className="mt-2">
            <a 
              href={audioUrl} 
              download
              className="btn btn-secondary"
            >
              Download Audio
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default TextToSpeech;