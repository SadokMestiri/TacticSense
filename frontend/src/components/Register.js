import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';


const Register = () => {
    const [username, setUsername] = useState('');
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [profileImage, setProfileImage] = useState(null);
    const [verificationFile, setVerificationFile] = useState(null);

    const navigate = useNavigate();

    const validateRoleDocument = async () => {
        const formData = new FormData();
        formData.append('file', verificationFile);
        formData.append('role', role);

        try {
            const res = await axios.post(`${process.env.REACT_APP_BASE_URL}/verify_document`, formData);
            return res.data.valid;
        } catch (err) {
            console.error(err);
            return false;
        }
    };



    const handleRegister = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        if (!role) {
            setError("Please select a role.");
            return;
        }

        if (!verificationFile) {
            setError("Please upload a verification document.");
            return;
        }

        const isValid = await validateRoleDocument();
        
        if (!isValid) {
            setError("The uploaded document does not match the selected role.");
            return;
        }

        const formData = new FormData();
        formData.append('username', username);
        formData.append('email', email);
        formData.append('password', password);
        formData.append('name', name);
        formData.append('role', role);


        if (profileImage) {
            formData.append('profile_image', profileImage);
        }
        formData.append('role', role);
        formData.append('verification_file', verificationFile);

        try {
            const response = await axios.post(`${process.env.REACT_APP_BASE_URL}/register`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            });

            if (response.status === 201) {
                setSuccess('User registered successfully. Redirecting to login...');
                setTimeout(() => navigate('/'), 2000);
            }
        } catch (error) {
            console.error('Registration error:', error);
            if (error.response) {
                // The request was made and the server responded with a status code
                setError(error.response.data?.message || `Server error: ${error.response.status}`);
            } else if (error.request) {
                // The request was made but no response was received
                setError('No response from server. Please check if the backend is running.');
            } else {
                // Something happened in setting up the request
                setError(`Error: ${error.message}`);
            }
        }
    };

    const handleProfileImageChange = (e) => {
        setProfileImage(e.target.files[0]);
        setSuccess('Profile image uploaded successfully!');
    };


    return (
        <div>
            <div id="page-loader" className="fade show"><span className="spinner"></span></div>
            <div className="login-cover">
                <div className="login-cover-image" style={{ backgroundImage: "url(assets/img/login-bg/register-bg.jpg)" }} data-id="login-cover-image"></div>
                <div className="login-cover-bg"></div>
            </div>
            <div id="page-container" className="fade">
                <div className="login login-v2" data-pageload-addclassName="animated fadeIn">
                    <div className="login-header">
                        <div className="brand">
                            <b>Meta</b>Scout
                            <small>A smarter way to scout</small>
                        </div>
                        <div className="icon">
                            <i className="fa fa-user-plus"></i>
                        </div>
                    </div>
                    <div className="login-content">
                        <form onSubmit={handleRegister} method="POST" className="margin-bottom-0">
                            <div className="form-group m-b-20">
                                <input
                                    type="text"
                                    className="form-control form-control-lg"
                                    placeholder="Full Name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                />
                                </div>
                                <div className="form-group m-b-20">
                                    <input
                                        type="text"
                                        className="form-control form-control-lg"
                                        placeholder="Username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        required
                                    />
                                </div>
                        
                            <div className="form-group m-b-20">
                                <input
                                    type="email"
                                    className="form-control form-control-lg"
                                    placeholder="Email Address"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
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
                            <div className="form-group m-b-20">
                                <select
                                    className="form-control form-control-lg"
                                    value={role}
                                    onChange={(e) => setRole(e.target.value)}
                                    required
                                >
                                    <option value="" disabled>Select Role</option>
                                    <option value="Player">Player</option>
                                    <option value="Coach">Coach</option>
                                    <option value="Agent">Agent</option>
                                    <option value="Manager">Manager</option>
                                    <option value="Club">Club</option>
                                    <option value="Staff">Staff</option>
                                    <option value="Scout">Scout</option>
                                </select>
                            </div>

                            {/* Profile image upload */}
                            <div className="form-group m-b-20">
                                <label htmlFor="profile-image-upload" className="upload-label">
                                    <div className="file-upload-area">
                                        <i className="fa fa-cloud-upload-alt"></i> {/* Cloud Icon */}
                                        <p>Upload Profile Picture</p>
                                    </div>
                                </label>
                                <input
                                    type="file"
                                    id="profile-image-upload"
                                    className="file-upload-input"
                                    onChange={handleProfileImageChange}
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                />
                            </div>

                            <div className="form-group m-b-20">
                                <label htmlFor="verification-file-upload" className="upload-label">
                                    <div className="file-upload-area">
                                        <i className="fa fa-file-upload"></i>
                                        <p>Upload Verification Document (must mention your role)</p>
                                    </div>
                                </label>
                                <input
                                    type="file"
                                    id="verification-file-upload"
                                    className="file-upload-input"
                                    onChange={(e) => setVerificationFile(e.target.files[0])}
                                    accept="image/*,.pdf"
                                    style={{ display: 'none' }}
                                />
                            </div>

                            {error && <p className="text-danger">{error}</p>}
                            {success && <p className="text-success">{success}</p>}

                            <div className="login-buttons">
                                <button type="submit" className="btn btn-success btn-block btn-lg">Register</button>
                            </div>
                            <div className="m-t-20">
                                Already have an account? Click <a href="/">here</a> to login.
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );


};

export default Register;
