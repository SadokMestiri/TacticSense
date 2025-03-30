import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import jwt_decode from "jwt-decode";

function ResetPassword() {
    const navigate = useNavigate();
    const baseUrl = "http://localhost:5000";
    const [newPassword, setNewPassword] = useState("");
    const [confirmNewPassword, setConfirmNewPassword] = useState("");
    const [error, setError] = useState("");
    const [token, setToken] = useState("");

    useEffect(() => {
        document.title = 'Réinitialiser mot de passe';
        const pageLoader = document.getElementById("page-loader");
        pageLoader.classList.remove("show");

        const searchParams = new URLSearchParams(window.location.search);
        const token = searchParams.get('token');
        setToken(token);
    }, []);

    const decodedToken = token ? jwt_decode(token) : null;
    const role = decodedToken?.role;

    const handleSubmit = (e) => {
        e.preventDefault();

        if (newPassword === confirmNewPassword) {
            axios.put(`${baseUrl}/resetPassword`, { token: token, newPassword: newPassword })
                .then((response) => {
                    console.log(response);
                    setNewPassword("");
                    setConfirmNewPassword("");
                    navigate('/Login');
                })
                .catch((error) => {
                    setError(error.response?.data?.error || 'An unknown error occurred');
                });
        } else {
            setError('Les mots de passe ne correspondent pas');
        }
    };

    console.log(role);

    return (
        <div>
            <div id="page-loader" className="fade show" style={{ height: "85vh" }}>
                <div className="material-loader">
                    <svg className="circular" viewBox="25 25 50 50">
                        <circle className="path" cx="50" cy="50" r="20" fill="none" strokeWidth="2" strokeMiterlimit="10"></circle>
                    </svg>
                    <div className="message">Chargement...</div>
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
                            Nouveau <br /> Mot de passe
                        </div>
                        <div className="icon" style={{ marginTop: "50px" }}>
                            <i className="fa fa-lock"></i>
                        </div>
                    </div>

                    <div className="login-content">
                        <form onSubmit={handleSubmit} action="index.html" method="GET" className="margin-bottom-0">
                            <div className="form-group m-b-20">
                                <input
                                    type="password"
                                    placeholder="Nouveau mot de passe"
                                    value={newPassword}
                                    className="form-control form-control-lg"
                                    autoComplete="off"
                                    onChange={(e) => setNewPassword(e.target.value)}
                                />
                            </div>
                            <div className="form-group m-b-20">
                                <input
                                    type="password"
                                    placeholder="Confirmer nouveau mot de passe"
                                    value={confirmNewPassword}
                                    className="form-control form-control-lg"
                                    autoComplete="off"
                                    onChange={(e) => setConfirmNewPassword(e.target.value)}
                                />
                            </div>

                            <div className="login-buttons">
                                <button type="submit" className="btn btn-success btn-block btn-lg">Réinitialiser</button>
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

export default ResetPassword;
