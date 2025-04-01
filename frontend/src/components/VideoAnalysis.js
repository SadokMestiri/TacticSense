import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import { useParams, useNavigate } from 'react-router-dom';
import CustomVideoPlayer from './CustomVideoPlayer';
import TranscriptDisplay from './TranscriptDisplay';
import './VideoAnalysis.css';
import MatchSummary from './MatchSummary';

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
  const [captionsFromPlayer, setCaptionsFromPlayer] = useState(null);
  const [showTranscript, setShowTranscript] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [summaryData, setSummaryData] = useState(null);
  const [analyzingTranscript, setAnalyzingTranscript] = useState(false);
  

  // states for transcript functionality
  const [currentTime, setCurrentTime] = useState(0);
  const [captionsData, setCaptionsData] = useState(null);


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

  // Parse SRT data when result.srt_url changes
  useEffect(() => {
    if (result?.srt_url) {
      fetchAndParseSRT(result.srt_url);
    }
  }, [result?.srt_url]);

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
          const vidFilename = response.data.video_url.split('/').pop().split('.')[0];
          setResult({
            transcript: "This is a sample transcript for debugging purposes.\n\nThe analysis feature can identify key moments in sports videos and provide insights into player movements, tactical patterns, and game statistics.",
            srt_url: `/processed_videos/${vidFilename}.srt`
          });
        } else {
          // If not in debug mode, analyze the video
          analyzePostVideo(response.data.video_url);
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

  // Function to fetch and parse SRT file
  const fetchAndParseSRT = async (srtUrl) => {
    try {
      console.log("Fetching SRT with modified path");
      
      // Extract filename from video URL
      let filename = videoUrl;
      if (filename.includes('/uploads/')) {
        filename = filename.split('/uploads/')[1];
      } else {
        filename = filename.split('/').pop();
      }
      
      // Get base filename WITHOUT using split('.')[0] which truncates at first period
      // Instead use regex to only remove the file extension
      const base_filename = filename.replace(/\.[^/.]+$/, '');
      console.log("Full base_filename:", base_filename);
      
      const srtUrl = `/processed_videos/${base_filename}.srt`;
      console.log("Trying SRT URL:", srtUrl);
      
      // Fetch SRT content directly with fetch API
      const srtResponse = await fetch(`${process.env.REACT_APP_BASE_URL}${srtUrl}`);
      
      if (srtResponse.ok) {
        console.log("SRT found successfully!");
        const srtText = await srtResponse.text();
        const parsedCaptions = parseSRT(srtText);
        setCaptionsData(parsedCaptions);
      } else {
        console.error("SRT file not found at:", srtUrl);
      }
    } catch (err) {
      console.error("Error fetching SRT:", err);
    }
  };

  // SRT parsing function
  const parseSRT = (srtText) => {
    const captions = [];
    
    try {
      // Normalize line endings
      const normalizedText = srtText.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      
      // Extract caption blocks with regex
      const regex = /(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?=\n\n\d+\n|$)/g;
      
      let match;
      while ((match = regex.exec(normalizedText + "\n\n")) !== null) {
        const index = parseInt(match[1]);
        const startTime = timeToSeconds(match[2]);
        const endTime = timeToSeconds(match[3]);
        const text = match[4].trim();
        
        if (!isNaN(startTime) && !isNaN(endTime)) {
          captions.push({
            index,
            start: startTime,
            end: endTime,
            text
          });
        }
      }
      
      console.log(`Successfully parsed ${captions.length} captions`);
      return captions;
    } catch (error) {
      console.error("Error parsing SRT:", error);
      return [];
    }
  };

  // Helper function to convert timestamp to seconds
  const timeToSeconds = (timeStr) => {
    try {
      const parts = timeStr.split(':');
      const [hours, minutes, secPart] = parts;
      const [seconds, milliseconds] = secPart.split(',');
      
      return parseInt(hours) * 3600 + 
             parseInt(minutes) * 60 + 
             parseInt(seconds) + 
             parseInt(milliseconds) / 1000;
    } catch (error) {
      console.error(`Error parsing time: ${timeStr}`, error);
      return NaN;
    }
  };

  // Handle time updates from the video player
  const handleTimeUpdate = (time) => {
    setCurrentTime(time);
  };

  // function to receive captions from player
  const handleCaptionsLoaded = (captions, toggleRequest = false) => {
    console.log("Received captions from player:", captions?.length || 0);
    setCaptionsData(captions);
    
    // If this is a toggle request from the CC button
    if (toggleRequest) {
      setShowTranscript(prev => !prev);
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
  
  const handleFileChange = (e) => { // deprecated
    setFile(e.target.files[0]);
    // Create a preview URL for the selected file
    if (e.target.files[0]) {
      setVideoUrl(URL.createObjectURL(e.target.files[0]));
    }
  };
  

const handleUpload = async () => { // depreacted
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


  const analyzeTranscript = async () => {
    if (!result?.transcript || analyzingTranscript) return;
    
    setAnalyzingTranscript(true);
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_BASE_URL}/api/analyze-transcript`,
        { transcript: result.transcript }
      );
      
      setSummaryData(response.data);
      // Auto-expand the summary when it's ready
      setShowSummary(true);
    } catch (err) {
      console.error("Error analyzing transcript:", err);
      setError("Failed to analyze the transcript");
    } finally {
      setAnalyzingTranscript(false);
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
    <div className="video-analysis-container">
      <div className="video-analysis-header">
        <h2>Video Analysis</h2>
      </div>
      
      <div className="video-analysis-content">
        {/* Left side - Video */}
        <div className="video-section">
          {videoUrl ? (
            <CustomVideoPlayer 
            videoUrl={videoUrl} 
            postId={postId}
            onTimeUpdate={handleTimeUpdate}
            onCaptionsLoaded={handleCaptionsLoaded}
            isInAnalysisPage={true} // Let player know it's in analysis page
          />
          ) : (
            <div className="video-container-loader">
              {loading ? (
                <div className="loading-indicator">Loading video...</div>
              ) : (
                <div className="error-message">{error || 'No video available'}</div>
              )}
            </div>
          )}
        </div>
        
        {/* Right side - Transcript */}
        <div className="analysis-section">
  {/* Always render the transcript section, but with a class indicating if it's expanded */}
  <div className={`transcript-section ${showTranscript ? 'expanded' : 'collapsed'}`}>
    <h3 onClick={() => setShowTranscript(prev => !prev)} className="transcript-header">
      Live Transcript
      <span className="toggle-icon">{showTranscript ? '▼' : '▶'}</span>
    </h3>
    
    {/* Only render the content when expanded */}
    {captionsData && showTranscript && (
      <div className="transcript-content">
        <TranscriptDisplay 
          captionsData={captionsData}
          currentTime={currentTime}
          showTranscript={true}
        />
      </div>
    )}
  </div>
          
  {result?.transcript && (
  <div className={`summary-section ${showSummary ? 'expanded' : 'collapsed'}`}>
    <h3 onClick={() => setShowSummary(prev => !prev)} className="transcript-header">
      Match Summary
      <span className="toggle-icon">{showSummary ? '▼' : '▶'}</span>
    </h3>
    
    {showSummary && (
      <div className="summary-content">
        {!summaryData && !analyzingTranscript && (
          <div className="summary-actions">
            <button 
              onClick={analyzeTranscript}
              className="analyze-button"
            >
              Generate Summary
            </button>
          </div>
        )}
        
        <MatchSummary 
          summary={summaryData?.summary}
          keyMoments={summaryData?.key_moments}
          loading={analyzingTranscript}
        />
      </div>
    )}
          </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoAnalysis;