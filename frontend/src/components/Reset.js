import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';

function Reset() {
    const navigate = useNavigate();
    const baseUrl = "http://127.0.0.1:5000";
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [error, setError] = useState("");

    useEffect(() => {
        document.title = 'Reset password';
        const pageLoader = document.getElementById("page-loader");
        pageLoader.classList.remove("show");
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            const response = await axios.post(`${baseUrl}/reset`, { email:email, username:username });
            console.log(response);

            if (response.status === 200) {
                navigate('/'); // Redirect on success
            } else {
                setError(response.data.error); // Set error message from response
            }
        } catch (error) {
            setError(error.response?.data?.error || 'An unknown error occurred');
        }
    };

    return (
        <div>
            <div id="page-loader" className="fade show" style={{ height: "85vh" }}>
                <div className="material-loader">
                    <svg className="circular" viewBox="25 25 50 50">
                        <circle className="path" cx="50" cy="50" r="20" fill="none" strokeWidth="2" strokeMiterlimit="10"></circle>
                    </svg>
                    <div className="message">Loading...</div>
                </div>
            </div>

            <div className="login-cover">
                <div className="login-cover-image" style={{ backgroundImage: " url(qr.png)" }} data-id="login-cover-image"></div>
                <div className="login-cover-bg"></div>
            </div>

            <div id="page-container" className="login-container" style={{ height: "85vh" }}>
                <div className="login login-v2" data-pageload-addclass="animated fadeIn" style={{ marginTop: "168px" }}>
                    <div className="login-header">
                        <div className="brand">
                            Reset <br />password
                        </div>
                        <div className="icon" style={{ marginTop: "50px" }}>
                            <i className="fa fa-lock"></i>
                        </div>
                    </div>

                    <div className="login-content">
                        <form onSubmit={handleSubmit} action="index.html" method="GET" className="margin-bottom-0">
                            <div className="form-group m-b-20">
                                <input
                                    type="text"
                                    placeholder="Email"
                                    value={email}
                                    className="form-control form-control-lg"
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            <div className="form-group m-b-20">
                                <input
                                    type="text"
                                    placeholder="Nom d'utilisateur"
                                    value={username}
                                    className="form-control form-control-lg"
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                            <div className="login-buttons">
                                <button type="submit" className="btn btn-success btn-block btn-lg">Submit</button>
                            </div>
                            <div className="m-t-20">
                                Remember your password? Click <a href="/">here</a> to login.
                            </div>
                            {error && 
                                <div className="alert alert-danger fade show">{error}</div>
                            }
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Reset;
