import React, { useState, useEffect } from 'react';
import Header from './Header';
import './Profile.css';
import axios from 'axios';
import Cookies from 'js-cookie';

const ClubProfile = ({ header,footer }) => {
    const [message, setMessage] = useState('');
    const [clubName, setClubName] = useState('');
    const [country, setCountry] = useState('');
    const [competition, setCompetition] = useState('');
    const [squadSize, setSquadSize] = useState('');

    useEffect(() => {
        const fetchClubData = async () => {
            const token = Cookies.get('token');
            if (!token) {
                setMessage('No token found. Please log in again.');
                return;
            }

            try {
                const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_club`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                const clubData = response.data;
                setClubName(clubData.name);
                setCountry(clubData.country);
                setCompetition(clubData.competition);
                setSquadSize(clubData.squad_size);
            } catch (error) {
                console.error('Error fetching club data:', error);
                setMessage('Failed to fetch club data. Please try again.');
            }
        };

        fetchClubData();
    }, []);

    const handleProfileUpdate = async () => {
        const updatedProfile = {
            name: clubName,
            country,
            competition,
            squad_size: squadSize,
        };

        const token = Cookies.get('token');
        if (!token) {
            setMessage('No token found. Please log in again.');
            return;
        }

        try {
            const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_club`, updatedProfile, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.status === 200) {
                setMessage('Club profile updated successfully');
            } else {
                setMessage('Unexpected response from the server.');
            }
        } catch (error) {
            if (error.response) {
                setMessage(`Error: ${error.response.data.message || 'Failed to update club profile.'}`);
            } else {
                setMessage('Network error. Please try again later.');
            }
        }
    };

    return (
        <div>
            <Header />
            <div className="container">
                <div className="left-sidebar">
                    <div className="sidebar-profile-box">
                        <img src="assets/images/cover-pic.jpg" alt="cover" className="cover-image" />
                        <div className="sidebar-profile-info">
                            <h1 className="profile-name">Club Profile</h1>
                            <ul className="profile-stats">
                                <li>
                                    Matches Played <span className="stat-value">100</span>
                                </li>
                                <li>
                                    Wins <span className="stat-value">60</span>
                                </li>
                                <li>
                                    Losses <span className="stat-value">40</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div className="right-sidebar">
                    <div className="sidebar-news">
                        <h3>Latest News</h3>
                        <ul>
                            <li>Club signed a new player</li>
                            <li>Upcoming match schedule released</li>
                        </ul>
                    </div>
                </div>
                <div className="main-content">
                    <h2>Account Info</h2>
                    <form>
                        <div className="form-group">
                            <label>Club Name</label>
                            <input
                                type="text"
                                className="form-control"
                                value={clubName}
                                onChange={(e) => setClubName(e.target.value)}
                                placeholder="Enter club name"
                            />
                        </div>
                        <div className="form-group">
                            <label>Country</label>
                            <input
                                type="text"
                                className="form-control"
                                value={country}
                                onChange={(e) => setCountry(e.target.value)}
                                placeholder="Enter country"
                            />
                        </div>
                        <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>
                        <h2>Details</h2>
                        <div className="form-group">
                            <label>Competition</label>
                            <input
                                type="text"
                                className="form-control"
                                value={competition}
                                onChange={(e) => setCompetition(e.target.value)}
                                placeholder="Enter competition"
                            />
                        </div>
                        <div className="form-group">
                            <label>Squad Size</label>
                            <input
                                type="number"
                                className="form-control"
                                value={squadSize}
                                onChange={(e) => setSquadSize(e.target.value)}
                                placeholder="Enter squad size"
                            />
                        </div>
                        <button type="button" className="update-profile-btn" onClick={handleProfileUpdate}>
                            Update Club Profile
                        </button>
                    </form>
                    {message && <p className="text-info">{message}</p>}
                </div>
            </div>
        </div>
    );
};

export default ClubProfile;
