import React, { useEffect, useRef } from 'react';
import './TranscriptDisplay.css';

const TranscriptDisplay = ({ captionsData, currentTime, showTranscript }) => {
  const transcriptRef = useRef(null);
  const currentCaptionRef = useRef(null);
  
  // Find the current, previous and upcoming captions
  const getCurrentCaptionIndex = () => {
    if (!captionsData) return -1;
    return captionsData.findIndex(
      cap => currentTime >= cap.start && currentTime <= cap.end
    );
  };
  
  const currentIndex = getCurrentCaptionIndex();
  
  // Get segments to display (current + context)
  const getPreviousCaptions = () => {
    if (currentIndex <= 0) return [];
    // Get up to 3 previous captions
    return captionsData.slice(Math.max(0, currentIndex - 3), currentIndex);
  };
  
  const getCurrentCaption = () => {
    if (currentIndex === -1) return null;
    return captionsData[currentIndex];
  };
  
  const getUpcomingCaptions = () => {
    if (currentIndex === -1 || currentIndex >= captionsData?.length - 1) return [];
    // Get up to 3 upcoming captions
    return captionsData.slice(currentIndex + 1, Math.min(captionsData.length, currentIndex + 4));
  };
  
  // Scroll the current caption into view with smooth animation
  useEffect(() => {
    if (currentCaptionRef.current && showTranscript) {
      currentCaptionRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  }, [currentIndex, showTranscript]);

  useEffect(() => {
    console.log("TranscriptDisplay received:", {
      captionsLength: captionsData?.length || 0,
      currentTime,
      showTranscript,
      currentIndex: getCurrentCaptionIndex()
    });
  }, [captionsData, currentTime, showTranscript]);
  
  if (!showTranscript || !captionsData?.length) return null;
  
  return (
    <div className="transcript-container" ref={transcriptRef}>
      {/* Previous captions */}
      <div className="previous-captions">
        {getPreviousCaptions().map((caption, idx) => (
          <div key={`prev-${caption.index || idx}`} className="caption previous">
            {caption.text}
          </div>
        ))}
      </div>
      
      {/* Current caption */}
      {getCurrentCaption() && (
        <div 
          ref={currentCaptionRef}
          className="caption current"
          key={`current-${getCurrentCaption().index || currentIndex}`}
        >
          {getCurrentCaption().text}
        </div>
      )}
      
      {/* Upcoming captions */}
      <div className="upcoming-captions">
        {getUpcomingCaptions().map((caption, idx) => (
          <div key={`next-${caption.index || idx}`} className="caption upcoming">
            {caption.text}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TranscriptDisplay;