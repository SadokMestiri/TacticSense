import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [showPassword, setShowPassword] = useState(false);
    const [showStreakPopup, setShowStreakPopup] = useState(false);
    const [userStreakData, setUserStreakData] = useState(null);  // To store user streak data
    const [loading, setLoading] = useState(false);  // To track the loading state

    const navigate = useNavigate();
    const baseUrl = process.env.REACT_APP_BASE_URL || "http://127.0.0.1:5000";

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
    
        try {
            // Attempt to log the user in
            const response = await axios.post(
                `${baseUrl}/login`, 
                { username, password },
                { headers: { "Content-Type": "application/json" } }
            );
    
            if (response.status === 200) {
                const { token } = response.data;
                const decodedToken = jwt_decode(token);
                const userId = decodedToken?.public_id;
    
                // Store token and user data in cookies (will be overwritten if they already exist)
                Cookies.set('token', token, { expires: 10 });
    
                // Fetch the user's streak (this will also update it if necessary)
                const streakResponse = await axios.get(`${baseUrl}/get_streak/${userId}`);
                
                // Check if the streak response contains error
                if (streakResponse.status === 200) {
                    // Set the updated streak data
                    setUserStreakData(streakResponse.data);
                    
                    // Store user data in cookies
                    const userResponse = await axios.get(`${baseUrl}/get_user/${userId}`);
                    const user = userResponse.data;
                    Cookies.set('user', JSON.stringify(user), { expires: 1 });
    
                    // Show the streak popup (after both fetching and updating streak)
                    setShowStreakPopup(true);
                } else {
                    setError('Failed to fetch streak data');
                }
            }
        } catch (error) {
            setError(error.response?.data?.message || 'Invalid username or password');
        } finally {
            setLoading(false);
        }
    };       
    
    

    // Close the popup and navigate to home
    const closePopup = () => {
        setShowStreakPopup(false);
    
        // After closing the popup, now set token and user info, then navigate to home
        const token = Cookies.get('token');
        if (token) {
            const decodedToken = jwt_decode(token);
            const userId = decodedToken?.public_id;
    
            // Fetch user details from server after closing popup
            axios.get(`${baseUrl}/get_user/${userId}`).then((userResponse) => {
                const user = userResponse.data;
    
                // Set user data and token in cookies after closing the popup
                Cookies.set('user', JSON.stringify(user), { expires: 1 });
    
                // Navigate to the Home page after setting the cookies
                navigate('/Home');
            }).catch((err) => {
                console.error('Error fetching user data:', err);
            });
        } else {
            console.log('No token found');
        }
    };
    

    return (
        <div id="page-container">
            <div className="login login-with-news-feed">
                <div className="news-feed">
                    <div className="news-image" style={{ backgroundImage: "url(assets/images/background.jpg)" }}></div>
                    <div className="news-caption">
                        <h4 className="caption-title"><b>Meta</b>Scout</h4>
                    </div>
                </div>

                <div className="right-content">
                    <div className="login-header">
                        <div className="brand">
                            <b>Meta</b>Scout
                            <small>A smarter way to scout</small>
                        </div>
                    </div>
                    <div className="login-content">
                        {error && <p className="alert alert-danger">{error}</p>}
                        <form onSubmit={handleLogin}>
                            <div className="form-group">
                                <input
                                    type="text"
                                    className="form-control form-control-lg"
                                    placeholder="Username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <input
                                    type={showPassword ? "text" : "password"} 
                                    className="form-control form-control-lg"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                                <span
                                    onClick={() => setShowPassword(!showPassword)}
                                    style={{ position: 'absolute', right: '20px', top: '40%', cursor: 'pointer' }}
                                >
                                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                                </span>
                            </div>
                            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>Sign in</button>
                        </form>
                        <div className="m-t-20">
                            <a href="/Reset">Forgot password?</a>
                        </div>
                    </div>
                </div>
            </div>

            {/* Streak popup */}
            {showStreakPopup && userStreakData && (
                <div className="popup">
                    <div className="popup-content">
                        <h4>Congratulations!</h4>
                        <p>Your current streak is {userStreakData.current_streak} days.</p>
                        <p>Your highest streak is {userStreakData.highest_streak} days.</p>
                        <p>Your total score is {userStreakData.score} points.</p>
                        <button onClick={closePopup}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Login;
