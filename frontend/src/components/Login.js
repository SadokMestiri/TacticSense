import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        console.log(username,password)
        try {
            const response = await axios.post(`${process.env.REACT_APP_BASE_URL}/login`, {
                username,
                password
            });
            if (response.status === 200) {
                // Stocker le token et rediriger l'utilisateur
                localStorage.setItem('token', response.data.token);
                navigate('/');
            } else {
                setError(response.data.message || 'Login failed');
            }
        } catch (error) {
            setError(error.response?.data?.message || 'An error occurred. Please try again.');
        }
    };

    return (
        <div>
            <div id="page-container">
                <div className="login login-with-news-feed">
                    <div className="news-feed">
                        <div className="news-image" style={{backgroundImage: "url(assets/images/background.jpg)"}}></div>
                        <div className="news-caption">
                            <h4 className="caption-title"><b>Meta</b>Scout</h4>
                        </div>
                    </div>

                    <div className="right-content">
                        <div className="login-header">
                            <div className="brand">
                                <a href="index.html" className="meta-logo"><img src="assets/images/logo.png" alt="logo" /></a>
                                <b>Meta</b>Scout
                                <small>A smarter way to scout</small>
                            </div>
                            <div className="icon">
                                <i className="fa fa-sign-in"></i>
                            </div>
                        </div>
                        <div className="login-content">
                            <form onSubmit={handleLogin} className="margin-bottom-0">
                                <div className="form-group m-b-15">
                                    <input
                                        type="text"
                                        className="form-control form-control-lg"
                                        placeholder="Username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="form-group m-b-15">
                                    <input
                                        type="password"
                                        className="form-control form-control-lg"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="checkbox checkbox-css m-b-30">
                                    <input type="checkbox" id="remember_me_checkbox" value="" />
                                    <label htmlFor="remember_me_checkbox">
                                        Remember Me
                                    </label>
                                </div>
                                <div className="login-buttons">
                                    <button type="submit" className="btn btn-primary btn-block btn-lg">Sign me in</button>
                                </div>
                                <div className="m-t-20 m-b-40 p-b-40">
                                    Not a member yet? Click <a href="register_v3.html" style={{color:"black"}}>here</a> to register.
                                </div>
                                <hr />
                                <p className="text-center">
                                    &copy; MetaScout All Right Reserved 2025
                                </p>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
