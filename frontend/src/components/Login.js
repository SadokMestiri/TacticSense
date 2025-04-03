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
    
    const navigate = useNavigate();
    const baseUrl = process.env.REACT_APP_BASE_URL || "http://127.0.0.1:5000";

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        
        try {
            const response = await axios.post(
                `${baseUrl}/login`, 
                { username, password },
                { headers: { "Content-Type": "application/json" } }
            );
        
            if (response.status === 200) {
                const { token } = response.data;
                const decodedToken = jwt_decode(token);
                const userId = decodedToken?.public_id;
                
                // Fetch user details using the userId
                const userResponse = await axios.get(`${baseUrl}/get_user/${userId}`);
                const user = userResponse.data;
    
                // Store token and user data in cookies
                Cookies.set('token', token, { expires: 1 });
                Cookies.set('user', JSON.stringify(user), { expires: 1 });

                navigate('/Home');
            }
        } catch (error) {
            setError(error.response?.data?.message || 'Invalid username or password');
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
                            <button type="submit" className="btn btn-primary btn-block">Sign in</button>
                        </form>
                        <div className="m-t-20">
                            <a href="/Reset">Forgot password?</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
