import React from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Cookies from "js-cookie";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Core Components
import Header from "./components/Header";
import Footer from "./components/Footer";

// Auth
import Login from "./components/Login";
import Register from "./components/Register";
import Reset from "./components/Reset";
import ResetPassword from "./components/ResetPassword";

// Profiles
import Profile from "./components/Profile";
import Profile_View from "./components/Profile_View";
import CoachProfile from "./components/CoachProfile";
import ClubProfile from "./components/ClubProfile";
import ManagerProfile from "./components/ManagerProfile";
import ManagerProfileView from "./components/ManagerProfileView";
import CoachProfileView from "./components/CoachProfileView";
import myPosts from "./components/myPosts";

// Main Pages
import Home from "./components/Home";
import Chat from "./components/Chat";
import SinglePost from "./components/SinglePost";
import HashtagPage from "./components/HashtagPage";
import Notifications from "./components/Notifications";

// Jobs
import Jobs from "./components/Jobs";
import JobDetails from "./components/JobDetails";
import JobApplications from "./components/JobApplications";
import PostJob from "./components/PostJob";
import PlayerPredictor from './components/PlayerPredictor';
import ExistingPlayerPredictor from './components/ExistingPlayerPredictor';
import PlayerProfile from './components/PlayerProfile';
import SavedPosts from './components/SavedPosts';
import Profile from './components/Profile';

// Prediction Tools
import InjuryPredictor from "./components/InjuryPredictor";
import StreakPopUp from "./components/StreakPopUp";
import GPT from "./components/GPT";
import PlayersList from "./components/PlayersList";

// Match Analysis
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
    const noHeaderPaths = ["/", "/register", "/reset", "/resetpassword"];

    const header = !noHeaderPaths.includes(location.pathname.toLowerCase()) && <Header />;
    const footer = !noHeaderPaths.includes(location.pathname.toLowerCase()) && <Footer />;

    return (
        <div>

            <Routes>
                {/* Public */}
                <Route path="/" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/reset" element={<Reset />} />
                <Route path="/resetpassword" element={<ResetPassword />} />

                {/* Authenticated */}
                <Route path="/home" element={isAuthenticated ? <Home header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/chat" element={isAuthenticated ? <Chat header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/chat/:userId" element={isAuthenticated ? <Chat header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/post/:postId" element={isAuthenticated ? <SinglePost header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/hashtag" element={isAuthenticated ? <HashtagPage header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/notifications" element={isAuthenticated ? <Notifications header={header} footer={footer} /> : <Navigate to="/" />} />

                {/* Profile Views */}
                <Route path="/profile" element={isAuthenticated ? <Profile header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/profile_view" element={isAuthenticated ? <Profile_View header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/manager_view" element={isAuthenticated ? <ManagerProfileView header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/coach_view" element={isAuthenticated ? <CoachProfileView header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/coachprofile" element={isAuthenticated ? <CoachProfile header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/clubprofile" element={isAuthenticated ? <ClubProfile header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/managerprofile" element={isAuthenticated ? <ManagerProfile header={header} footer={footer} /> : <Navigate to="/" />} />

                {/* Jobs */}
                <Route path="/jobs" element={isAuthenticated ? <Jobs header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/jobdetails" element={isAuthenticated ? <JobDetails header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/jobapplications" element={isAuthenticated ? <JobApplications header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/postjob" element={isAuthenticated ? <PostJob header={header} footer={footer} /> : <Navigate to="/" />} />

                {/* Predictors */}
                <Route path="/injury" element={isAuthenticated ? <InjuryPredictor header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/streak" element={isAuthenticated ? <StreakPopUp /> : <Navigate to="/" />} />
                <Route path="/gpt" element={isAuthenticated ? <GPT header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/players" element={isAuthenticated ? <PlayersList header={header} footer={footer} /> : <Navigate to="/" />} />

                {/* Match Analysis */}
                <Route path="/matches" element={isAuthenticated ? <MatchesList header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/matches/upload" element={isAuthenticated ? <MatchUpload header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/matches/:matchId" element={isAuthenticated ? <VideoAnalysis header={header} footer={footer} /> : <Navigate to="/" />} />

                {/* Analysis Hub */}
                <Route path="/analysis-hub" element={isAuthenticated ? <AnalysisHubMain header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/analysis-hub/matches" element={isAuthenticated ? <MatchesList header={header} footer={footer} /> : <Navigate to="/" />} />
                <Route path="/analysis-hub/matches/:matchId/analysis" element={isAuthenticated ? <MatchAnalysisDetail header={header} footer={footer}/> : <Navigate to="/" />} />
                <Route path="/analysis-hub/players" element={isAuthenticated ? <ExistingPlayerPredictor header={header} footer={footer}/> : <Navigate to="/" />} />
                <Route path="/analysis-hub/players/new" element={isAuthenticated ? <PlayerPredictor header={header} footer={footer}/> : <Navigate to="/" />} />
                <Route path="/analysis-hub/players/:name" element={isAuthenticated ? <PlayerProfile header={header} footer={footer}/> : <Navigate to="/" />} />

                <Route path="/saved-posts" element={<SavedPosts header={header} />} />
                <Route path="/profile/:username" element={ <myPosts header={header} />} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to={isAuthenticated ? "/home" : "/"} />} />
            </Routes>
            <ToastContainer />
            {footer}
        </div>
    );
}

export default App;
