import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";

const Footer = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const user =  JSON.parse(Cookies.get('user'));
  const token = Cookies.get('token');
  let decodedToken = null;
  let exp = null;

  if (token) {
    decodedToken = jwt_decode(token);
    exp = decodedToken?.exp;
  }

  const date = exp ? new Date(exp * 1000) : null;
  const now = new Date();
  const [allowed, setAllowed] = useState(false);

  // Token expiration check
  useEffect(() => {
    if (!token || !decodedToken) {
      navigate('/');
    } else if (date && date.getTime() < now.getTime()) {
      Cookies.remove('token');
      navigate('/');
    } else {
      setAllowed(true);
    }
  }, [token, decodedToken, navigate, date]);







  // Conditionally render based on user data availability
  if (!user) {
    return <div>Loading...</div>; // Show loading if user data is not fetched
  }

  return (
    <div>
      <footer>
        <div className="footer-area footer-bg footer-padding">
            <div className="container">
                <div className="row d-flex justify-content-between">
                    <div className="col-xl-3 col-lg-3 col-md-4 col-sm-6">
                       <div className="single-footer-caption mb-50">
                         <div className="single-footer-caption mb-30">
                             <div className="footer-tittle">
                                 <h4>About Us</h4>
                                 <div className="footer-pera">
                                     <p>Revolutionizing football scouting with AI-driven insights, connecting talent with opportunity.</p>
                                </div>
                             </div>
                         </div>

                       </div>
                    </div>
                    <div className="col-xl-3 col-lg-3 col-md-4 col-sm-5">
                        <div className="single-footer-caption mb-50">
                            <div className="footer-tittle">
                                <h4>Contact Info</h4>
                                <ul>
                                    <li><a href="#">Phone : +8880 44338899</a></li>
                                    <li><a href="#">Email : metascout@gmail.com</a></li>
                                </ul>
                            </div>

                        </div>
                    </div>
                    <div className="col-xl-3 col-lg-3 col-md-4 col-sm-5">
                        <div className="single-footer-caption mb-50">
                            <div className="footer-tittle">
                                <h4>Shortcuts</h4>
                                <ul>
                                    <li><a href="/home">Home</a></li>
                                    <li><a href="#">Network</a></li>
                                    <li><a href="/Chat">Messaging</a></li>
                                    <li><a href="/jobs">Jobs</a></li>
                                    <li><a href="#">Notifications</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>


<div className="footer-bottom-area footer-bg" >
  <div className="container">
    <div className="footer-border">
      <div className="row d-flex justify-content-between align-items-center">
        {/* Logo, copyright, and social media links are placed next to each other */}
        <div className="col-xl-4 col-lg-4 col-md-4 d-flex align-items-center">
          {/* Logo */}
          <div className="footer-logo">
            <a href="index.html"><img src="assets/images/logo.png" height={"auto"} width={"150px"} alt="logo" /></a>
          </div>
        </div>

        <div className="col-xl-4 col-lg-4 col-md-4 d-flex align-items-center justify-content-center">
          {/* Copyright Text */}
          <div className="footer-copy-right">
            <p> 
              Copyright &copy;2025 All rights reserved 
            </p>
          </div>
        </div>

        <div className="col-xl-4 col-lg-4 col-md-4 d-flex align-items-center justify-content-end">
          {/* Social Links */}
          <div className="footer-social">
            <a href="#"><i className="fab fa-facebook-f"></i></a>
            <a href="#"><i className="fab fa-twitter"></i></a>
            <a href="#"><i className="fas fa-globe"></i></a>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</div>
</div>
    </footer>
    </div>
  );
};

export default Footer;
