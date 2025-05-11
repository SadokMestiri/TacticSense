import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import Cookies from 'js-cookie'; // Re-added Cookies import
import jwt_decode from 'jwt-decode';
import './streak.css';
import StreakPopUp from "./StreakPopUp";

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [showPassword, setShowPassword] = useState(false);
    const [showStreakPopup, setShowStreakPopup] = useState(false);
    const [userStreakData, setUserStreakData] = useState(null);  // To store user streak data
    const [loading, setLoading] = useState(false);  // To track the loading state
    const [mintingLoading, setMintingLoading] = useState(false);  // To track minting state
    const [metaCoinMessage, setMetaCoinMessage] = useState('');  // For success/failure message

    const navigate = useNavigate();
    const baseUrl = process.env.REACT_APP_BASE_URL || "http://127.0.0.1:5000";

    const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setMetaCoinMessage('');

    try {
        const response = await axios.post(`${baseUrl}/login`, {
            username,
            password
        });

        if (response.status === 200) {
            const { token } = response.data;
            const decodedToken = jwt_decode(token);
            const userId = decodedToken?.public_id;

            Cookies.set('token', token, { expires: 10 });

            // Fetch user data
            const userResponse = await axios.get(`${baseUrl}/get_user/${userId}`);
            const user = userResponse.data;
            Cookies.set('user', JSON.stringify(user), { expires: 1 });

            // Get streak
            const streakResponse = await axios.get(`${baseUrl}/get_streak/${userId}`);
            const streakData = streakResponse.data;
            setUserStreakData(streakData);

            if (!streakData.already_logged_in_today) {
                setMintingLoading(true);
                setMetaCoinMessage("Generating streak and assigning MetaCoins...");
                await handleMintAndStreakMetaCoins(userId, streakData.current_streak);
                setShowStreakPopup(true);
            } else {
                // Not first login today, go straight to home
                navigate("/Home");
            }
        } else {
            setError('Login failed');
        }
    } catch (error) {
        setError(error.response?.data?.message || 'Login error');
    } finally {
        setLoading(false);
    }
};


    // Handle minting and adding MetaCoins
    const handleMintAndStreakMetaCoins = async (userId, currentStreak) => {
    try {
        const addMetaCoinsResponse = await axios.post(
            `${baseUrl}/add_metacoins_streak`,
            { user_id: userId },
            { headers: { "Content-Type": "application/json" } }
        );

        console.log("MetaCoin mint response:", addMetaCoinsResponse);

        if (addMetaCoinsResponse.status === 200) {
            const message = addMetaCoinsResponse.data?.message || "MetaCoins rewarded.";
            setMetaCoinMessage(message);
        } else {
            const errMsg = addMetaCoinsResponse.data?.error || "Failed to add MetaCoins.";
            setMetaCoinMessage(errMsg);
            setError(errMsg);
            console.error("MetaCoin minting failed:", errMsg);
            navigate("/Home");
        }
    } catch (error) {
        const errMsg = error.response?.data?.error || error.message || "Unexpected error during MetaCoin minting.";
        setError(errMsg);
        setMetaCoinMessage(errMsg);
        console.error("MetaCoin minting error:", error);
        navigate("/Home");
    } finally {
        setMintingLoading(false);
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
<button type="submit" className="btn btn-primary btn-block d-flex align-items-center justify-content-center" disabled={loading}>
    {loading ? (
        <>
            <span className="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>
            Signing in...
        </>
    ) : (
        'Sign in'
    )}
</button>
                        </form>
                        {mintingLoading && (
    <div className="text-center mt-3 d-flex align-items-center justify-content-center">
        <span className="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>
        <span>{metaCoinMessage}</span>
    </div>
)}

                        <div className="m-t-20">
                           Forgot password? <a href="/Reset">Click here to reset</a>
                        </div>
                         <div className="m-t-20">
                            Don't have an account yet?<a href="/Register"> Sign up now</a>
                        </div>
                    </div>
                    </div>
                </div>
            {/* Show MetaCoin messages */}
{showStreakPopup && userStreakData && (
  <div >
    <StreakPopUp
      currentStreak={userStreakData.current_streak}
      day={userStreakData.current_streak_day}
    />
  </div>
)}


{metaCoinMessage && (
  <div
    className="alert alert-success"
    style={{ backgroundColor: '#d4edda', color: '#155724' }}  // Dark green Bootstrap shades
  >
    {metaCoinMessage}
  </div>
)}



        </div>
    );
};

export default Login;
