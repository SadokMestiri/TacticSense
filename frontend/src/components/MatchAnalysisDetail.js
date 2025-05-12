import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Cookies from 'js-cookie';
import axios from 'axios';
import CustomVideoPlayer from './CustomVideoPlayer'; // Assuming you want to use this for the overlay video
import Slider from "react-slick"; // Import react-slick
import Spinner from './Spinner'; // Import the Spinner
import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";
import './AnalysisHub.css';

// New sub-component for individual image items
const CarouselImageItem = ({ imgUrl, altText }) => {
    return (
        // The div wrapper helps with spacing and ensures react-slick handles items correctly.
        // The margin provides space between slides.
        <div style={{ margin: '0 15px' }}> 
            <img 
                src={imgUrl} 
                alt={altText} 
                style={{ 
                    width: '100%', /* Image will try to fill the width of the slide */
                    height: 'auto', 
                    maxHeight: '350px', /* Increased max height for larger images */
                    objectFit: 'contain', /* Ensures aspect ratio is maintained */
                    borderRadius: '4px',
                    display: 'block', /* Helps prevent extra space below image */
                    margin: '0 auto' /* Centers image if slide is wider than image's aspect ratio dictates */
                }} 
            />
        </div>
    );
};

// New sub-component for a single segment/track of images
const ImageSetSegment = ({ imageSet }) => {
    if (!imageSet || !imageSet.images || imageSet.images.length === 0) {
        return null;
    }

    const settings = {
        dots: true,
        infinite: false,
        speed: 500,
        slidesToShow: 1, // Show 1 large slide at a time
        slidesToScroll: 1,
        variableWidth: false, // Set to false if CarouselImageItem wrapper has a consistent effective width due to margins
        adaptiveHeight: true, // Good for images of potentially different aspect ratios
        centerMode: true, // Centers the active slide
        centerPadding: '60px', // Shows a glimpse of the next/prev slides. Adjust as needed.
                               // Set to '0px' if you don't want glimpses.
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    centerPadding: '40px',
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    centerPadding: '20px', // Less padding on smaller screens
                    dots: false // Optionally hide dots on very small screens
                }
            }
        ]
    };

    return (
        <div className="carousel-segment-block">
            {imageSet.label && <h5>{imageSet.label}</h5>}
            <Slider {...settings}>
                {imageSet.images.map((imgUrl, imgIndex) => (
                    <CarouselImageItem
                        key={imgIndex} 
                        imgUrl={imgUrl}
                        altText={`${imageSet.label || 'Image'} ${imgIndex + 1}`}
                    />
                ))}
            </Slider>
        </div>
    );
};

// Modified ImageCarousel component
const ImageCarousel = ({ images, title }) => {
    if (!images || images.length === 0) return null;

    return (
        <div className="image-carousel-main-container">
            {title && <h4>{title}</h4>}
            {images.map((imageSet, setIndex) => (
                <ImageSetSegment key={setIndex} imageSet={imageSet} />
            ))}
        </div>
    );
};

function MatchAnalysisDetail({ header,footer }) {
    const { matchId } = useParams();
    const navigate = useNavigate();
    const [matchDetails, setMatchDetails] = useState(null); // For general match info like title, teams
    const [analysisData, setAnalysisData] = useState(null); // For tactical analysis specific data
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [pollingIntervalId, setPollingIntervalId] = useState(null);
    
    // State for collapsible sections
    const [isFinalHeatmapsOpen, setIsFinalHeatmapsOpen] = useState(false); // Default to open
    const [isIntermediateHeatmapsOpen, setIsIntermediateHeatmapsOpen] = useState(false); // Default to open


    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:5000';

    const fetchAnalysisData = useCallback(async () => {
        // setLoading(true); // Keep main loading for initial, not for polling
        setError('');
        const token = Cookies.get('token');
        if (!token) {
            navigate('/login');
            return;
        }

        try {
            const response = await axios.get(`${API_BASE_URL}/api/match/${matchId}/tactical-analysis`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = response.data;
            setAnalysisData(data);
            // Set matchDetails from this endpoint now
            setMatchDetails({
                title: data.title,
                team1_name: data.team1_name,
                team2_name: data.team2_name,
                competition: data.competition,
                match_date: data.match_date,
            });

            if (data.status === 'completed' || data.status === 'failed') {
                if (pollingIntervalId) {
                    clearInterval(pollingIntervalId);
                    setPollingIntervalId(null);
                }
            }
        } catch (err) {
            console.error("Error fetching analysis data:", err);
            setError(err.response?.data?.error || 'Failed to load analysis data.');
            if (pollingIntervalId) {
                clearInterval(pollingIntervalId);
                setPollingIntervalId(null);
            }
        } finally {
            setLoading(false); // Only set to false on initial load
        }
    }, [matchId, navigate, pollingIntervalId, API_BASE_URL]);

    useEffect(() => {
        fetchAnalysisData(); // Initial fetch
    }, [fetchAnalysisData]); // Only run on mount and when fetchAnalysisData changes (which it shouldn't after mount)

    const startAnalysis = async () => {
        const token = Cookies.get('token');
        if (!token) {
            navigate('/login');
            return;
        }
        setError('');
        setAnalysisData(prev => ({ ...prev, status: 'pending' })); // Optimistic update

        try {
            await axios.post(`${API_BASE_URL}/api/match/${matchId}/trigger-tactical-analysis`, {}, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            // Start polling
            if (pollingIntervalId) clearInterval(pollingIntervalId); // Clear existing if any
            const intervalId = setInterval(fetchAnalysisData, 5000); // Poll every 5 seconds
            setPollingIntervalId(intervalId);
        } catch (err) {
            console.error("Error starting analysis:", err);
            setError(err.response?.data?.message || 'Failed to start analysis.');
            setAnalysisData(prev => ({ ...prev, status: err.response?.data?.status || 'failed' }));
        }
    };

    useEffect(() => {
        // Cleanup polling on component unmount
        return () => {
            if (pollingIntervalId) {
                clearInterval(pollingIntervalId);
            }
        };
    }, [pollingIntervalId]);

    if (loading) return <div className="hub-loading-indicator">Loading Analysis Hub...</div>;
    if (error && !analysisData) return <div className="hub-error-message">Error: {error}</div>;
    if (!analysisData || !matchDetails) return <div className="hub-loading-indicator">Match data not available.</div>;

    const { status, overlay_video_url, heatmaps_final = [], heatmaps_intermediate = [], error_message: analysisError } = analysisData;
    const { title, team1_name, team2_name, competition, match_date } = matchDetails;

    const displayTitle = title || `${team1_name || 'Team 1'} vs ${team2_name || 'Team 2'}`;

    // Calculate specific processing message
    let currentProcessingMessage = "Processing analysis...";
    if (status === 'processing') {
        if (!overlay_video_url && (!heatmaps_final || heatmaps_final.length === 0) && (!heatmaps_intermediate || heatmaps_intermediate.length === 0)) {
            currentProcessingMessage = "Preparing analysis and generating tactical overlay video...";
        } else if (overlay_video_url && (!heatmaps_final || heatmaps_final.length === 0) && (!heatmaps_intermediate || heatmaps_intermediate.length === 0)) {
            currentProcessingMessage = "Generating heatmaps...";
        } else if (overlay_video_url && (heatmaps_final?.length > 0 || heatmaps_intermediate?.length > 0) && !heatmaps_final?.every(h => h) && !heatmaps_intermediate?.every(h => h)) {
            currentProcessingMessage = "Finalizing heatmap generation..."; // Example if some heatmaps are there but not all
        }
    }

    const showGlobalSpinner =
        (status === 'pending') ||
        (status === 'processing' && !overlay_video_url && (!heatmaps_final || heatmaps_final.length === 0) && (!heatmaps_intermediate || heatmaps_intermediate.length === 0));

    return (
        <div className="analysis-hub-container">
            <header className="analysis-hub-page-header">
                <Link to="/matches" className="back-to-matches">&larr; Back to Matches</Link>
            </header>
            <div className="analysis-hub-content">
                <h1 className="analysis-hub-main-title">ANALYSIS HUB</h1>
                <div className="analysis-hub-match-title-container">
                    <h2>{displayTitle}</h2>
                    <p className="match-meta-info">{competition || 'N/A'} - {match_date || 'N/A'}</p>
                </div>

                <div className="analysis-actions">
                    <button
                        onClick={startAnalysis}
                        disabled={status === 'processing' || status === 'pending'}
                        className="btn-start-analysis"
                    >
                        {status === 'processing' && 'Processing...'}
                        {status === 'pending' && 'Pending...'}
                        {status === 'completed' && 'Re-Analyze'}
                        {status === 'failed' && 'Retry Analysis'}
                        {status === 'not_started' && 'Start Tactical Analysis'}
                        {!status && 'Start Tactical Analysis'}
                    </button>
                </div>

                <div className="analysis-status-section">
                    <p>Status: <span className={`status-tactical-${status}`}>{status || 'Not Started'}</span></p>
                    {status === 'failed' && analysisError && <p className="hub-error-message">Error: {analysisError}</p>}
                </div>

                {showGlobalSpinner && (
                    <Spinner message={status === 'pending' ? 'Analysis is pending...' : currentProcessingMessage} />
                )}

                {!showGlobalSpinner && (status === 'completed' || status === 'processing') && (
                    <>
                        {/* Tactical Overlay Video Section */}
                        {overlay_video_url && status === 'completed' && (
                            <div className="analysis-video-section">
                                <h3>Tactical Overlay Video</h3>
                                <CustomVideoPlayer videoUrl={overlay_video_url} />
                            </div>
                        )}
                        {status === 'processing' && !overlay_video_url && (
                            <div className="info-message-box">
                                <p>Tactical overlay video is being generated...</p>
                            </div>
                        )}
                        {status === 'completed' && !overlay_video_url && (
                             <div className="info-message-box">
                                <p>Tactical overlay video is not available for this analysis.</p>
                            </div>
                        )}

                        {/* Final Heatmaps Section - Collapsible */}
                        {(heatmaps_final && heatmaps_final.length > 0 && status === 'completed') && (
                            <div className="analysis-heatmaps-section final-heatmaps collapsible-section">
                                <h3 onClick={() => setIsFinalHeatmapsOpen(!isFinalHeatmapsOpen)} className="collapsible-header">
                                    Final Heatmaps
                                    <span className={`arrow ${isFinalHeatmapsOpen ? 'open' : ''}`}>{isFinalHeatmapsOpen ? '▼' : '►'}</span>
                                </h3>
                                <div className={`collapsible-content ${isFinalHeatmapsOpen ? 'open' : ''}`}>
                                    <div className="heatmaps-grid">
                                        {heatmaps_final.map((url, index) => (
                                            <div key={`final-${index}`} className="heatmap-item">
                                                <img src={url} alt={`Final Heatmap ${index + 1}`} />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                        {status === 'processing' && (!heatmaps_final || heatmaps_final.length === 0) && (
                            <div className="info-message-box">
                                <p>Final heatmaps are being generated...</p>
                            </div>
                        )}
                         {status === 'completed' && (!heatmaps_final || heatmaps_final.length === 0) && ( // Show if completed but no final heatmaps
                            <div className="info-message-box">
                                <p>No final heatmaps are available for this analysis.</p>
                            </div>
                        )}

                        {/* Intermediate Heatmaps Section - Collapsible */}
                        {(heatmaps_intermediate && heatmaps_intermediate.length > 0 && status === 'completed') && (
                            <div className="analysis-heatmaps-section intermediate-heatmaps collapsible-section">
                               <h3 onClick={() => setIsIntermediateHeatmapsOpen(!isIntermediateHeatmapsOpen)} className="collapsible-header">
                                   Intermediate Heatmaps (Segments)
                                   <span className={`arrow ${isIntermediateHeatmapsOpen ? 'open' : ''}`}>{isIntermediateHeatmapsOpen ? '▼' : '►'}</span>
                                </h3>
                               <div className={`collapsible-content ${isIntermediateHeatmapsOpen ? 'open' : ''}`}>
                                   <ImageCarousel images={heatmaps_intermediate} title="" />
                               </div>
                            </div>
                        )}
                        {status === 'processing' && (!heatmaps_intermediate || heatmaps_intermediate.length === 0) && (
                             <div className="info-message-box">
                                <p>Intermediate heatmaps are being generated...</p>
                            </div>
                        )}
                        {status === 'completed' && (!heatmaps_intermediate || heatmaps_intermediate.length === 0) && ( // Show if completed but no intermediate
                            <div className="info-message-box">
                                <p>No intermediate heatmaps are available for this analysis.</p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

export default MatchAnalysisDetail;