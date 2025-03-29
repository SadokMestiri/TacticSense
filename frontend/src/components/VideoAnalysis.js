import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useParams, useNavigate } from 'react-router-dom';

const VideoAnalysis = () => {
  const { postId } = useParams();
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [debugMode, setDebugMode] = useState(true); // Set to true for testing


  // Fetch post video if postId is provided
  useEffect(() => {
    if (postId) {
      fetchPostVideo(postId);
      
      // Debug mode: generate sample results if needed
      if (debugMode && !result) {
        setResult({
          transcript: "This is a sample transcript for debugging purposes. The analysis feature works with this test data.",
          srt_url: "/processed_videos/sample.srt",
          captioned_video_url: "/processed_videos/sample_captioned.mp4"
        });
      }
    }
  }, [postId]);

  const fetchPostVideo = async (id) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(
        `${process.env.REACT_APP_BASE_URL}/get_post_by_id/${id}`
      );
      
      if (response.data && response.data.video_url) {
        // Set video URL
        setVideoUrl(`${process.env.REACT_APP_BASE_URL}${response.data.video_url}`);
        
        // Auto-generate analysis if in debug mode
        if (debugMode) {
          setResult({
            transcript: "This is a sample transcript for debugging purposes.\n\nThe analysis feature can identify key moments in sports videos and provide insights into player movements, tactical patterns, and game statistics.",
            srt_url: `/processed_videos/${response.data.video_url.split('/').pop().split('.')[0]}.srt`
          });
        }
      } else {
        setError('No video found in this post');
      }
    } catch (err) {
      console.error("Error fetching post:", err);
      setError('Could not load video from post');
    } finally {
      setLoading(false);
    }
  };

  const analyzePostVideo = async (videoPath) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = Cookies.get('token');
      const response = await axios.post(
        `${process.env.REACT_APP_BASE_URL}/api/transcribe-from-path`,
        { video_path: videoPath },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error analyzing video');
    } finally {
      setLoading(false);
    }
  };
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    // Create a preview URL for the selected file
    if (e.target.files[0]) {
      setVideoUrl(URL.createObjectURL(e.target.files[0]));
    }
  };
  

const handleUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const token = Cookies.get('token');
      console.log("Using token:", token); // Debug the token
      
      const response = await axios.post(
        `${process.env.REACT_APP_BASE_URL}/api/transcribe`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      setResult(response.data);
    } catch (err) {
      console.error("API Error:", err);
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleTTS = async () => {
    try {
      setLoading(true);
      
      // Use the public endpoint instead
      const response = await axios.post(
        `${process.env.REACT_APP_BASE_URL}/api/public-tts`,
        { text: result.transcript || 'No transcript available' }
      );
      
      if (response.data && response.data.audio_url) {
        setAudioUrl(`${process.env.REACT_APP_BASE_URL}${response.data.audio_url}`);
        setAudioPlaying(true);
        
        // Play the audio automatically
        const audio = new Audio(`${process.env.REACT_APP_BASE_URL}${response.data.audio_url}`);
        audio.play();
      }
    } catch (err) {
      console.error('Error converting text to speech:', err);
      setError('Could not convert text to speech');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="video-analysis-container" style={{padding: '20px', maxWidth: '800px', margin: '0 auto'}}>
      <h2>Video Analysis</h2>
      
      {error && (
        <div style={{background: '#f8d7da', padding: '10px', borderRadius: '4px', marginBottom: '15px'}}>
          {error}
        </div>
      )}
      
      {videoUrl && (
        <div style={{marginBottom: '20px'}}>
          <video controls width="100%" src={videoUrl} />
        </div>
      )}
      
      {result && (
        <div>
          <h3>Transcript</h3>
          <div style={{
            border: '1px solid #ddd', 
            padding: '15px', 
            borderRadius: '4px',
            background: '#f8f9fa',
            whiteSpace: 'pre-line' // Preserves line breaks
          }}>
            {result.transcript}
          </div>
          
          <div style={{marginTop: '20px'}}>
            <button 
              onClick={handleTTS}
              disabled={loading}
              style={{
                padding: '8px 16px',
                background: '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {loading ? 'Processing...' : 'Read Aloud'}
            </button>
          </div>
        </div>
      )}
      
      {!result && !loading && !error && (
        <div style={{textAlign: 'center', margin: '40px 0'}}>
          <p>Select a video to analyze or upload one below.</p>
          <input 
            type="file" 
            accept="video/*" 
            onChange={(e) => setFile(e.target.files[0])}
            style={{display: 'block', margin: '20px auto'}}
          />
          {file && (
            <button 
              onClick={handleUpload}
              style={{
                padding: '8px 16px',
                background: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Analyze Video
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoAnalysis;