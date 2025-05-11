import React from 'react';
import './Spinner.css';

const Spinner = ({ message }) => {
    return (
        <div className="spinner-container">
            <div className="spinner"></div>
            {message && <p className="spinner-message">{message}</p>}
        </div>
    );
};

export default Spinner;