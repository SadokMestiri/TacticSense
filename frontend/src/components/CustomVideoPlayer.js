import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CustomVideoPlayer.css';
import Cookies from 'js-cookie';

const CustomVideoPlayer = ({ videoUrl, postId, onTimeUpdate, onCaptionsLoaded, isInAnalysisPage = false }) => {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showCaptions, setShowCaptions] = useState(false);
  const [captionsData, setCaptionsData] = useState(null);
  const [currentCaption, setCurrentCaption] = useState('');
  const [debugMode, setDebugMode] = useState(false);
  const [loadingCaptions, setLoadingCaptions] = useState(false);


  const videoRef = useRef(null);
  const navigate = useNavigate();
  

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    
    const onLoadedMetadata = () => {
      console.log("Video metadata loaded, duration:", video.duration);
      setDuration(video.duration);
    };
    
    video.addEventListener('loadedmetadata', onLoadedMetadata);
    
    // Try to set duration immediately if already available
    if (video.readyState >= 1) {
      setDuration(video.duration);
    }
    
    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
    };
  }, []); // Empty dependency array - runs once on mount
  

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !captionsData?.length) return;
    
    // Keep the metadata handler from your existing code
    const onLoadedMetadata = () => {
      setDuration(video.duration);
    };
    
    const handleTimeUpdate = () => {
      const currentTime = video.currentTime;
      // Keep updating currentTime state from your existing code
      setCurrentTime(currentTime);

      // Call the callback if provided
      if (onTimeUpdate) {
        onTimeUpdate(currentTime);
      }
      
      // Find the caption that matches the current time
      const currentCap = captionsData.find(
        cap => currentTime >= cap.start && currentTime <= cap.end
      );
      
      // For debugging: log every 5 seconds
      if (Math.floor(currentTime) % 5 === 0) {
        console.log(`Time: ${currentTime}, Found caption: ${currentCap?.text?.substring(0, 20) || 'none'}`);
      }
      
      setCurrentCaption(currentCap ? currentCap.text : '');
    };
    
    video.addEventListener('loadedmetadata', onLoadedMetadata);
    video.addEventListener('timeupdate', handleTimeUpdate);
    
    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
      video.removeEventListener('timeupdate', handleTimeUpdate);
    };
  }, [onTimeUpdate, captionsData]);
  
  const handlePlayPause = () => {
    const video = videoRef.current;
    if (playing) {
      video.pause();
    } else {
      video.play();
    }
    setPlaying(!playing);
  };
  
  const handleSliderChange = (e) => {
    const video = videoRef.current;
    const newTime = e.target.value;
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };
  
  const handleCaptions = async () => {
    // Toggle captions visibility
    setShowCaptions(!showCaptions);
    
    // If we're turning on captions but don't have caption data yet, fetch them
    if (!showCaptions && !captionsData) {
      setLoadingCaptions(true);
      try {
        // Extract filename as you're already doing
        let filename = videoUrl;
        if (filename.includes('/uploads/')) {
          filename = filename.split('/uploads/')[1];
        } else {
          filename = filename.split('/').pop();
        }
        
        // Try to load directly from the expected location
        const base_filename = filename.replace(/\.[^/.]+$/, '');
        const srtUrl = `/processed_videos/${base_filename}.srt`;
      
      try {
        // Try to fetch the SRT directly
        const srtResponse = await fetch(`${process.env.REACT_APP_BASE_URL}${srtUrl}`);
        
        if (srtResponse.ok) {
          console.log("Found existing captions!");
          const srtText = await srtResponse.text();
          const parsedCaptions = parseSRT(srtText);
          setCaptionsData(parsedCaptions);

          // Now we can safely pass the parsed captions to the parent
          if (onCaptionsLoaded) {
            onCaptionsLoaded(parsedCaptions);
          }

          setLoadingCaptions(false);
          return;
        }
      } catch (error) {
        console.log("No existing SRT found, will generate new captions");
      }
      
      // Continue with caption generation if we didn't find existing captions
      console.log("No existing captions found, generating new ones...");
      
        
        // If we get here, no existing captions were found, so generate new ones
        console.log("Starting caption generation for video:", filename);
      
            
            const response = await fetch(`${process.env.REACT_APP_BASE_URL}/api/public-transcribe`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ video_path: filename })
            });
            
            console.log("Transcription API response status:", response.status);
            
            if (response.ok) {
              const result = await response.json();
              console.log("REAL CAPTIONS GENERATED:", result);
              
              // Now fetch the SRT file
              const srtResponse = await fetch(`${process.env.REACT_APP_BASE_URL}${result.srt_url}`);
              console.log("SRT file response status:", srtResponse.status);
              
              if (srtResponse.ok) {
                const srtText = await srtResponse.text();
                console.log("SRT content received, length:", srtText.length);
                const parsedCaptions = parseSRT(srtText);
                console.log("FINAL PARSED CAPTIONS:", parsedCaptions);
                setCaptionsData(parsedCaptions);

                // Now we can safely pass the parsed captions to the parent
                if (onCaptionsLoaded) {
                  onCaptionsLoaded(parsedCaptions);
                }
              } else {
                throw new Error(`Failed to fetch SRT file: ${srtResponse.status}`);
              }
            } else {
              throw new Error(await response.text());
            }
          } catch (error) {
            console.error("ERROR GENERATING REAL CAPTIONS:", error);
            // Fall back to debug captions only in case of error
            setDebugMode(true);
            const debugCaptions = [
              { start: 1, end: 5, text: "FALLBACK - Real transcription failed" },
              { start: 6, end: 10, text: "Please check the console for error details" },
              { start: 11, end: 15, text: "Try again or select a different video" }
            ];
            setCaptionsData(debugCaptions);
          } finally {
            setLoadingCaptions(false);
          }
        } else if (captionsData && onCaptionsLoaded) {
          // If we already have captions, share them
          onCaptionsLoaded(captionsData);
        }
        
      };

      // Add a useEffect to share captions when they're initially loaded
      useEffect(() => {
        if (captionsData && onCaptionsLoaded) {
          onCaptionsLoaded(captionsData);
        }
      }, [captionsData, onCaptionsLoaded]);
  
    const handleAnalyze = () => {
        navigate(`/video-analysis/${postId}`);
      };
  
      const parseSRT = (srtText) => {
        const captions = [];
        
        try {
          // Normalize line endings to avoid Windows/Unix issues
          const normalizedText = srtText.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
          
          // Use regex to properly extract captions
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
          
          console.log(`Successfully parsed ${captions.length} discrete captions`);
          
          // Debug the first few captions
          captions.slice(0, 3).forEach((cap, i) => {
            console.log(`Caption ${i+1}: ${cap.start.toFixed(2)}-${cap.end.toFixed(2)}: ${cap.text.substring(0, 30)}...`);
          });
          
          return captions;
        } catch (error) {
          console.error("Error parsing SRT with regex:", error);
          return []; // Return empty array on error
        }
      };
      
      // Improved timeToSeconds function
      const timeToSeconds = (timeStr) => {
        try {
          // Format: 00:00:00,000
          const parts = timeStr.trim().split(':');
          if (parts.length !== 3) {
            console.error(`Invalid time format: ${timeStr}`);
            return NaN;
          }
          
          let [hours, minutes, secPart] = parts;
          
          // Handle both comma and period as decimal separators
          secPart = secPart.replace(',', '.');
          const [seconds, milliseconds] = secPart.includes('.') ? 
            secPart.split('.') : [secPart, '0'];
          
          const totalSeconds = 
            parseInt(hours) * 3600 + 
            parseInt(minutes) * 60 + 
            parseInt(seconds) + 
            parseFloat(`0.${milliseconds}`);
          
          return totalSeconds;
        } catch (error) {
          console.error(`Error parsing time: ${timeStr}`, error);
          return NaN;
        }
      };
  
  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };
  
  return (
    <div className="custom-video-player">
      <div className="video-container">
        <video
          ref={videoRef}
          src={videoUrl}
          onClick={handlePlayPause}
        />
        
        {showCaptions && currentCaption && (
          <div className="captions-overlay">
            {currentCaption}
          </div>
        )}

        {loadingCaptions && (
          <div className="caption-loading">
            Generating captions...
          </div>
        )}
      </div>
      
      <div className="controls">
        <button className="play-button" onClick={handlePlayPause}>
          {playing ? '⏸' : '▶'}
        </button>
        
        <div className="time-display">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
        
        <input
          type="range"
          min="0"
          max={duration}
          value={currentTime}
          onChange={handleSliderChange}
          className="time-slider"
        />
        
        <button 
          className={`caption-button ${showCaptions ? 'active' : ''}`}
          onClick={handleCaptions}
        >
          CC
        </button>
        
        <button 
          className="analyze-button"
          onClick={handleAnalyze}
        >
          🔍 Analyze
        </button>
      </div>
    </div>
  );
};

export default CustomVideoPlayer;