import React, { useState, useRef, useEffect, useCallback } from 'react';
// import { useNavigate } from 'react-router-dom'; // No longer needed if analyze button is removed
import './CustomVideoPlayer.css';
// import Cookies from 'js-cookie'; // No longer needed if no API calls from player

const CustomVideoPlayer = ({ videoUrl, srtUrl, onTimeUpdate, onCaptionsLoaded }) => {
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showPlayerCaptions, setShowPlayerCaptions] = useState(false); // Internal state for player's own caption overlay
  const [captionsData, setCaptionsData] = useState(null);
  const [currentCaptionText, setCurrentCaptionText] = useState('');
  const [loadingSrt, setLoadingSrt] = useState(false);
  const [volume, setVolume] = useState(1);
  const [isControlsVisible, setIsControlsVisible] = useState(true); // Show controls initially
  const [isHovering, setIsHovering] = useState(false);


  const videoRef = useRef(null);
  const playerContainerRef = useRef(null);
  let controlsTimeoutRef = useRef(null);

  const parseSRT = useCallback((srtText) => {
    const captions = [];
    if (!srtText) return captions;
    try {
      const normalizedText = srtText.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      const regex = /(\d+)\n(\d{2}:\d{2}:\d{2}[,.]\d{3}) --> (\d{2}:\d{2}:\d{2}[,.]\d{3})(?:[ \t]+\S+:.+)*\n([\s\S]*?)(?=\n\n\d+\n|\n\n$|$)/g;
      let match;
      while ((match = regex.exec(normalizedText)) !== null) {
        captions.push({
          start: timeToSeconds(match[2]),
          end: timeToSeconds(match[3]),
          text: match[4].trim().replace(/<[^>]+>/g, ''), // Strip HTML tags from captions
        });
      }
    } catch (error) {
      console.error("Error parsing SRT:", error);
    }
    return captions;
  }, []);

  const timeToSeconds = useCallback((timeStr) => {
    try {
      const parts = timeStr.split(':');
      const secondsAndMillis = parts[2].replace(',', '.').split('.');
      const hours = parseInt(parts[0], 10);
      const minutes = parseInt(parts[1], 10);
      const seconds = parseInt(secondsAndMillis[0], 10);
      const milliseconds = secondsAndMillis[1] ? parseInt(secondsAndMillis[1], 10) : 0;
      return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000;
    } catch (error) {
      console.error(`Error parsing time string: ${timeStr}`, error);
      return 0;
    }
  }, []);


  useEffect(() => {
    if (srtUrl) {
      setLoadingSrt(true);
      fetch(srtUrl)
        .then(response => {
          if (!response.ok) throw new Error(`Failed to fetch SRT: ${response.status} ${response.statusText}`);
          return response.text();
        })
        .then(srtText => {
          const parsed = parseSRT(srtText);
          setCaptionsData(parsed);
          // Inform parent that captions are loaded (or failed), but this is not a user toggle action.
          // Parent can decide if it wants to show its transcript by default based on this.
          if (onCaptionsLoaded) {
            onCaptionsLoaded(parsed, false); // false: initial load, not direct user toggle of CC button
          }
        })
        .catch(error => {
          console.error("Error loading SRT file:", error);
          setCaptionsData(null);
          if (onCaptionsLoaded) {
            onCaptionsLoaded(null, false); // Inform parent captions failed to load
          }
        })
        .finally(() => {
          setLoadingSrt(false);
        });
    } else {
      setCaptionsData(null);
      if (onCaptionsLoaded) {
        onCaptionsLoaded(null, false); // No SRT URL provided
      }
    }
  }, [srtUrl, onCaptionsLoaded, parseSRT]);


  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleLoadedMetadata = () => setDuration(video.duration);
    const handleTimeUpdateInternal = () => {
      const newTime = video.currentTime;
      setCurrentTime(newTime);
      if (onTimeUpdate) onTimeUpdate(newTime);

      if (showPlayerCaptions && captionsData) {
        const currentCap = captionsData.find(cap => newTime >= cap.start && newTime <= cap.end);
        setCurrentCaptionText(currentCap ? currentCap.text : '');
      } else {
        setCurrentCaptionText('');
      }
    };
    const handlePlay = () => setPlaying(true);
    const handlePause = () => setPlaying(false);
    const handleEnded = () => setPlaying(false);


    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('timeupdate', handleTimeUpdateInternal);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('ended', handleEnded);
    video.addEventListener('volumechange', () => setVolume(video.volume));


    // Initial duration if already loaded
    if (video.readyState >= 1) {
        handleLoadedMetadata();
    }


    return () => {
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('timeupdate', handleTimeUpdateInternal);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('ended', handleEnded);
      video.removeEventListener('volumechange', () => setVolume(video.volume));
    };
  }, [onTimeUpdate, captionsData, showPlayerCaptions]);
  
  const hideControls = useCallback(() => {
    if (playing && !isHovering) { // Only hide if playing and not hovering over controls
        setIsControlsVisible(false);
    }
  }, [playing, isHovering]);

  useEffect(() => {
    if (playing) {
        controlsTimeoutRef.current = setTimeout(hideControls, 3000); // Hide after 3s of inactivity
    } else {
        setIsControlsVisible(true); // Always show if paused
        clearTimeout(controlsTimeoutRef.current);
    }
    return () => clearTimeout(controlsTimeoutRef.current);
  }, [playing, currentTime, hideControls]); // Re-evaluate on play/pause or activity

  const handleMouseEnterPlayer = () => {
    setIsControlsVisible(true);
    clearTimeout(controlsTimeoutRef.current);
  };

  const handleMouseLeavePlayer = () => {
    if (playing) {
        controlsTimeoutRef.current = setTimeout(hideControls, 500); // Shorter delay on mouse leave if playing
    }
  };
   const handleControlsMouseEnter = () => {
    setIsHovering(true);
    clearTimeout(controlsTimeoutRef.current); // Keep controls visible while hovering them
  };

  const handleControlsMouseLeave = () => {
    setIsHovering(false);
    if (playing) {
        controlsTimeoutRef.current = setTimeout(hideControls, 3000); // Restart hide timer
    }
  };


  const handlePlayPause = () => {
    const video = videoRef.current;
    if (playing) video.pause();
    else video.play();
    // setPlaying(!playing); // State will be updated by event listeners
  };

  const handleSliderChange = (e) => {
    const newTime = parseFloat(e.target.value);
    videoRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleSkip = (amount) => {
    videoRef.current.currentTime += amount;
  };

  const handleTogglePlayerCaptions = () => {
    const newShowState = !showPlayerCaptions;
    setShowPlayerCaptions(newShowState);
    if (onCaptionsLoaded) {
      // Inform parent about user's explicit toggle action
      onCaptionsLoaded(newShowState && captionsData ? captionsData : null, true);
    }
  };
  
  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    videoRef.current.volume = newVolume;
    setVolume(newVolume);
  };

  const formatTime = (timeInSeconds) => {
    const minutes = Math.floor(timeInSeconds / 60).toString().padStart(2, '0');
    const seconds = Math.floor(timeInSeconds % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  };

  return (
    <div 
        ref={playerContainerRef} 
        className="custom-video-player-modern"
        onMouseEnter={handleMouseEnterPlayer}
        onMouseLeave={handleMouseLeavePlayer}
        onMouseMove={handleMouseEnterPlayer} // Show controls on any mouse move over player
    >
      <div className="video-wrapper-modern">
        <video ref={videoRef} src={videoUrl} onClick={handlePlayPause}>
          Your browser does not support the video tag.
        </video>
        {showPlayerCaptions && currentCaptionText && (
          <div className="captions-overlay-modern">{currentCaptionText}</div>
        )}
        {loadingSrt && <div className="srt-loading-indicator">Loading Captions...</div>}
      </div>

      <div 
        className={`controls-modern ${isControlsVisible ? 'visible' : ''}`}
        onMouseEnter={handleControlsMouseEnter}
        onMouseLeave={handleControlsMouseLeave}
      >
        <button onClick={handlePlayPause} className="control-button-modern">
          {playing ? '❚❚' : '►'}
        </button>
        <button onClick={() => handleSkip(-10)} className="control-button-modern">« 10s</button>
        <button onClick={() => handleSkip(10)} className="control-button-modern">10s »</button>
        
        <div className="time-display-modern">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
        <input
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSliderChange}
          className="time-slider-modern"
        />
        <div className="volume-control-modern">
            <span>🔊</span>
            <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.05" 
                value={volume} 
                onChange={handleVolumeChange}
                className="volume-slider-modern"
            />
        </div>
        <button
          onClick={handleTogglePlayerCaptions}
          className={`control-button-modern caption-button-modern ${showPlayerCaptions && captionsData ? 'active' : ''}`}
          disabled={loadingSrt || !captionsData}
        >
          CC
        </button>
      </div>
    </div>
  );
};

export default CustomVideoPlayer;