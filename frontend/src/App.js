import React from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom';
import Cookies from 'js-cookie';
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

// Updated imports for Analysis Hub structure
import AnalysisHubMain from './components/AnalysisHubMain'; // New landing page for the hub
import MatchAnalysisDetail from './components/MatchAnalysisDetail'; // RENAMED from AnalysisHub

import PlayerPredictor from './components/PlayerPredictor';
import ExistingPlayerPredictor from './components/ExistingPlayerPredictor';
import PlayerProfile from './components/PlayerProfile';

function App() {
    const isAuthenticated = !!Cookies.get('token');
    const location = useLocation();
    const noHeaderPaths = ['/login', '/register', '/reset', '/ResetPassword'];

    return (
        <>
            {!noHeaderPaths.includes(location.pathname) && <Header />}
            <Routes>
                {/* Public Auth Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/reset" element={<Reset />} />
                <Route path="/ResetPassword" element={<ResetPassword />} />

                {/* Protected Routes */}
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
                    path="/matches/:matchId" // This seems to be for a general video analysis
                    element={isAuthenticated ? <VideoAnalysis /> : <Navigate to="/login" />}
                />

                {/* --- New Analysis Hub Structure --- */}
                <Route 
                    path="/analysis-hub" 
                    element={isAuthenticated ? <AnalysisHubMain /> : <Navigate to="/login" />} 
                />
                <Route 
                    path="/analysis-hub/matches" 
                    element={isAuthenticated ? <MatchesList /> : <Navigate to="/login" />} 
                />
                <Route 
                    path="/analysis-hub/matches/:matchId/analysis" 
                    element={isAuthenticated ? <MatchAnalysisDetail /> : <Navigate to="/login" />} 
                />
                
                {/* Player Prediction Routes */}
                <Route 
                    path="/analysis-hub/players"  // This will render ExistingPlayerPredictor (the list)
                    element={isAuthenticated ? <ExistingPlayerPredictor /> : <Navigate to="/login" />} 
                />
                <Route 
                    path="/analysis-hub/players/new" // For adding a new player for prediction
                    element={isAuthenticated ? <PlayerPredictor /> : <Navigate to="/login" />} 
                />
                <Route 
                    path="/analysis-hub/players/:name" // For viewing a specific player's profile and prediction
                    element={isAuthenticated ? <PlayerProfile /> : <Navigate to="/login" />} 
                />

                {/* Catch-all route */}
                <Route
                    path="*"
                    element={isAuthenticated ? <Navigate to="/" /> : <Navigate to="/login" />}
                />
            </Routes>
        </>
    );
}

export default App;
