import React, { useState, useEffect } from 'react';
import Header from './Header';
import './Profile.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';

const ClubProfile = () => {
    const [message, setMessage] = useState('');
    const [profileImage, setProfileImage] = useState('');
    const [username, setUsername] = useState('');
    const [name, setName] = useState('');
    const [role, setRole] = useState('');
    const [email, setEmail] = useState('');
    const [country, setCountry] = useState('');
    const [competition, setCompetition] = useState('');
    const [squadSize, setSquadSize] = useState('');

    useEffect(() => {
        const fetchClubData = async () => {
            const userCookie = Cookies.get('user');
            if (userCookie) {
                const parsedUser = JSON.parse(userCookie);
                const userId = parsedUser.id;

                try {
                    const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${userId}`, {
                        headers: {
                            Authorization: `Bearer ${Cookies.get('token')}`,
                        },
                    });

                    const clubData = response.data;

                    // Update state with the fetched club data
                    setProfileImage(clubData.profile_image);
                    setUsername(clubData.username);
                    setName(clubData.name);
                    setEmail(clubData.email);
                    setRole(clubData.role);
                    setCountry(clubData.country);
                    setCompetition(clubData.competition);
                    setSquadSize(clubData.squad_size);
                    console.log('Club data:', clubData);
                } catch (error) {
                    console.error('Error fetching club data:', error);
                    setMessage('Failed to fetch club data. Please try again.');
                }
            }
        };

        fetchClubData();
    }, []);

    const handleImageChange = async (event) => {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('profile_image', file);

            const token = Cookies.get('token');
            if (!token) {
                setMessage('No token found. Please log in again.');
                return;
            }

            try {
                const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile`, formData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setProfileImage(response.data.profile_image);
                setMessage('Profile image updated successfully');
            } catch (error) {
                setMessage('Error updating profile image');
            }
        }
    };

    const handleProfileUpdate = async () => {
        const updatedProfile = {
            username,
            name,
            email,
            role,
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
            const response = await axios.put(`${process.env.REACT_APP_BASE_URL}/update_profile`, updatedProfile, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.status === 200) {
                setMessage('Profile updated successfully');
            } else {
                setMessage('Unexpected response from the server.');
            }
        } catch (error) {
            if (error.response) {
                if (error.response.status === 401) {
                    setMessage('Unauthorized. Please log in again.');
                } else {
                    setMessage(`Error: ${error.response.data.message || 'Failed to update profile.'}`);
                }
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
                            <div className="profile-image-wrapper">
                                <img
                                    src={`${process.env.REACT_APP_BASE_URL}/${profileImage}`}
                                    alt="profile"
                                    className="profile-image"
                                />
                                <label htmlFor="profile-image-upload" className="edit-icon">
                                    <img
                                        src="assets/images/edit-icon.png"
                                        alt="edit"
                                        className="edit-icon-image"
                                    />
                                </label>
                                <input
                                    type="file"
                                    id="profile-image-upload"
                                    style={{ display: 'none' }}
                                    accept="image/*"
                                    onChange={handleImageChange}
                                />
                            </div>
                            <h1 className="profile-name">{name}</h1>
                            <h3 className="profile-username">{username}</h3>
                            <ul className="profile-stats">
                                <li>
                                    Profile views <span className="stat-value">10K</span>
                                </li>
                                <li>
                                    Post views <span className="stat-value">50K</span>
                                </li>
                                <li>
                                    Connections <span className="stat-value">5K</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div className="main-content">
                    <h2>Account Info</h2>
                    <form>
                        <div className="form-group">
                            <label>Username</label>
                            <input
                                type="text"
                                className="form-control"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Enter new username"
                            />
                        </div>
                        <div className="form-group">
                            <label>Name</label>
                            <input
                                type="text"
                                className="form-control"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Enter full name"
                            />
                        </div>
                        <div className="form-group">
                            <label>Role</label>
                            <input
                                type="text"
                                className="form-control"
                                value={role}
                                readOnly
                            />
                        </div>
                        <div className="form-group">
                            <label>Email</label>
                            <input
                                type="email"
                                className="form-control"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="Enter email address"
                            />
                        </div>
                        <div style={{ width: '90%', margin: '20px auto', borderTop: '1px solid #ccc' }}></div>

                        <h2>Details</h2>

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
                            Update Profile
                        </button>
                    </form>
                    {message && <p className="text-info">{message}</p>}
                </div>
                <div className="right-sidebar">
                    <div className="sidebar-news"></div>
                </div>
            </div>
        </div>
    );
};

export default ClubProfile;