import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-grid">
          {/* Section 1 */}
          <div>
            <h2>TacticSense</h2>
            <p>Advanced analysis of football data.</p>
          </div>

          {/* Section 2 */}
          <div>
            <h2>Useful Links</h2>
            <ul>
              <li><a href="#">Home</a></li>
              <li><a href="#">About</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>

          {/* Section 3 */}
          <div>
            <h2>Follow Us</h2>
            <div className="footer-social">
              <a href="#">Facebook</a>
              <a href="#">Twitter</a>
              <a href="#">LinkedIn</a>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="footer-bottom">
          © {new Date().getFullYear()} TacticSense. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;