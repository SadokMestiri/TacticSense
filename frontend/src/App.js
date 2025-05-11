import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Cookies from "js-cookie";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Core Components
import Header from "./components/Header";
import Footer from "./components/Footer";

// Auth Components
import Login from "./components/Login";
import Register from "./components/Register";
import Reset from "./components/Reset";
import ResetPassword from "./components/ResetPassword";

// Main Pages
import Home from "./components/Home";
import Chat from "./components/Chat";
import SinglePost from "./components/SinglePost";
import HashtagPage from "./components/HashtagPage";
import Notifications from "./components/Notifications";

// Job Features
import Jobs from "./components/Jobs";
import JobDetails from "./components/JobDetails";
import JobApplications from "./components/JobApplications";
import PostJob from "./components/PostJob";

// Prediction Tools
import InjuryPredictor from "./components/InjuryPredictor";
import StreakPopUp from "./components/StreakPopUp";
import GPT from "./components/GPT";
import PlayersList from "./components/PlayersList";

// Match Analysis Hub
import MatchesList from "./components/MatchesList";
import MatchUpload from "./components/MatchUpload";
import VideoAnalysis from "./components/VideoAnalysis";
import AnalysisHubMain from "./components/AnalysisHubMain";
import MatchAnalysisDetail from "./components/MatchAnalysisDetail";

// Player Prediction
import PlayerPredictor from "./components/PlayerPredictor";
import ExistingPlayerPredictor from "./components/ExistingPlayerPredictor";
import PlayerProfile from "./components/PlayerProfile";

function App() {
    const isAuthenticated = !!Cookies.get("token");
    const location = useLocation();
    const noHeaderPaths = ["/login", "/register", "/reset", "/ResetPassword"];

    const header = !noHeaderPaths.includes(location.pathname) && <Header />;
    const footer = !noHeaderPaths.includes(location.pathname) && <Footer />;

    return (
        <div>
            {header}
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/reset" element={<Reset />} />
                <Route path="/ResetPassword" element={<ResetPassword />} />

                {/* Authenticated Routes */}
                <Route
                    path="/"
                    element={isAuthenticated ? <Home header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/chat"
                    element={isAuthenticated ? <Chat header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/chat/:userId"
                    element={isAuthenticated ? <Chat header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/post/:postId"
                    element={isAuthenticated ? <SinglePost header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/jobs"
                    element={isAuthenticated ? <Jobs header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/jobDetails"
                    element={isAuthenticated ? <JobDetails header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/jobApplications"
                    element={isAuthenticated ? <JobApplications header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/hashtag"
                    element={isAuthenticated ? <HashtagPage header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/postJob"
                    element={isAuthenticated ? <PostJob header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/injury"
                    element={isAuthenticated ? <InjuryPredictor header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/streak"
                    element={isAuthenticated ? <StreakPopUp /> : <Navigate to="/login" />}
                />
                <Route
                    path="/gpt"
                    element={isAuthenticated ? <GPT header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/players"
                    element={isAuthenticated ? <PlayersList header={header} footer={footer} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/notifications"
                    element={isAuthenticated ? <Notifications header={header} footer={footer} /> : <Navigate to="/login" />}
                />

                {/* Match Analysis Routes */}
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

                {/* Analysis Hub */}
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
                    path="/analysis-hub/players"
                    element={isAuthenticated ? <ExistingPlayerPredictor /> : <Navigate to="/login" />}
                />
                <Route
                    path="/analysis-hub/players/new"
                    element={isAuthenticated ? <PlayerPredictor /> : <Navigate to="/login" />}
                />
                <Route
                    path="/analysis-hub/players/:name"
                    element={isAuthenticated ? <PlayerProfile /> : <Navigate to="/login" />}
                />

                {/* Catch-All */}
                <Route
                    path="*"
                    element={<Navigate to={isAuthenticated ? "/" : "/login"} />}
                />
            </Routes>
            <ToastContainer />
            {footer}
        </div>
    );
}

export default App;
