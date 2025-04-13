import React, { useState } from 'react';
import axios from 'axios';
import { FaVolumeUp, FaStop } from 'react-icons/fa';

const SummaryTTS = ({ summaryText }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState(null);
  const [error, setError] = useState(null);

  const handleTTS = async () => {
    // If already playing, stop the audio
    if (isPlaying && audioElement) {
      audioElement.pause();
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_BASE_URL}/api/public-tts`,
        { text: summaryText }
      );

      if (response.data && response.data.audio_url) {
        // Create a new audio element
        const audio = new Audio(`${process.env.REACT_APP_BASE_URL}${response.data.audio_url}`);
        
        // Add event listeners
        audio.addEventListener('ended', () => setIsPlaying(false));
        audio.addEventListener('error', () => {
          setError('Error playing audio');
          setIsPlaying(false);
        });
        
        // Store audio element reference and play
        setAudioElement(audio);
        audio.play();
        setIsPlaying(true);
      }
    } catch (err) {
      console.error('Error converting text to speech:', err);
      setError('Could not convert text to speech');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="summary-tts">
      <button 
        className={`tts-button ${isPlaying ? 'playing' : ''}`}
        onClick={handleTTS}
        disabled={isLoading || !summaryText}
        title={isPlaying ? "Stop audio" : "Listen to summary"}
      >
        {isLoading ? (
          <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        ) : isPlaying ? (
          <FaStop />
        ) : (
          <FaVolumeUp />
        )}
        {isPlaying ? ' Stop' : ' Listen'}
      </button>
      {error && <div className="text-danger mt-2">{error}</div>}
    </div>
  );
};

export default SummaryTTS;