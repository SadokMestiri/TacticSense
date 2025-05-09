import React from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom'; // Import useLocation
import Cookies from 'js-cookie'; // Import Cookies
import Header from './components/Header';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Reset from './components/Reset';
import ResetPassword from './components/ResetPassword';
import Chat from './components/Chat';
import SinglePost from './components/SinglePost';
import VideoAnalysis from './components/VideoAnalysis';
import MatchesList from './components/MatchesList';
import MatchUpload from './components/MatchUpload';
import AnalysisHub from './components/AnalysisHub'; // Import the new component

function App() {
    // Check for token in Cookies instead of localStorage
    const isAuthenticated = !!Cookies.get('token');
    const location = useLocation(); // Get current location

    // Define paths where the header should NOT be shown
    const noHeaderPaths = ['/login', '/register', '/reset', '/ResetPassword'];

    return (
        <>
            {/* Conditionally render Header based on path */} 
            {!noHeaderPaths.includes(location.pathname) && <Header />}
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/reset" element={<Reset />} />
                <Route path="/ResetPassword" element={<ResetPassword />} />
                <Route
                    path="/"
                    element={isAuthenticated ? <Home /> : <Navigate to="/login" />}
                />
                <Route
                    path="/chat"
                    element={isAuthenticated ? <Chat /> : <Navigate to="/login" />}
                />
                <Route
                    path="/chat/:userId"
                    element={isAuthenticated ? <Chat /> : <Navigate to="/login" />}
                />
                <Route
                    path="/post/:postId"
                    element={isAuthenticated ? <SinglePost /> : <Navigate to="/login" />}
                />
                <Route
                    path="/matches"
                    element={isAuthenticated ? <MatchesList /> : <Navigate to="/login" />}
                />
                <Route
                    path="/matches/upload"
                    element={isAuthenticated ? <MatchUpload /> : <Navigate to="/login" />}
                />
                <Route
                    path="/matches/:matchId" 
                    element={isAuthenticated ? <VideoAnalysis /> : <Navigate to="/login" />}
                />
                <Route
                    path="/matches/:matchId/analysis"
                    element={isAuthenticated ? <AnalysisHub /> : <Navigate to="/login" />}
                />
                <Route
                    path="*"
                    element={isAuthenticated ? <Navigate to="/" /> : <Navigate to="/login" />}
                />
            </Routes>
        </>
    );
}

export default App;