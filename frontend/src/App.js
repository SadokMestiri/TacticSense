import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Home from "./components/Home";
import { Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Header from "./components/Header";
import Reset from "./components/Reset";
import ResetPassword from "./components/ResetPassword";
import SinglePost from "./components/SinglePost";
import Jobs from "./components/Jobs";
import JobDetails from "./components/JobDetails";
import Footer from "./components/Footer";
import JobApplications from "./components/JobApplications";
import HashtagPage from "./components/HashtagPage";
import PostJob from "./components/PostJob";
import InjuryPredictor from "./components/InjuryPredictor";
import StreakPopUp from "./components/StreakPopUp";
import GPT from "./components/GPT";
import PlayersList from "./components/PlayersList";
import Notifications from "./components/Notifications";


export default function App() {

  const header = (<Header/>);
  const footer = (<Footer/>);
  return (

    <div>
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/Home" element={<Home header={header} footer={footer} />} />
      <Route path="/Chat" element={<Chat header={header} footer={footer}/>} />
      <Route path="/Register" element={<Register/>} />
      <Route path="/header" element={<Header />} />
      <Route path="/Reset" element={<Reset/>}/>
      <Route path="/ResetPassword" element={<ResetPassword/>}/>
      <Route path="/post" element={<SinglePost header={header} footer={footer} postId={4} />} />
      <Route path="/jobs" element={<Jobs header={header} footer={footer} />} />
      <Route path="/jobDetails" element={<JobDetails header={header} footer={footer} />} />
      <Route path="/jobApplications" element={<JobApplications header={header} footer={footer} />} />
      <Route path="/hashtag" element={<HashtagPage header={header} footer={footer} />} />
      <Route path="/postJob" element={<PostJob header={header} footer={footer} />} />
      <Route path="/injury" element={<InjuryPredictor header={header} footer={footer} />} />
      <Route path="/streak" element={<StreakPopUp  />} />
      <Route path="/gpt" element={<GPT header={header} footer={footer}/>} />
      <Route path="/players" element={<PlayersList header={header} footer={footer}/>} />
      <Route path="/notifications" element={<Notifications header={header} footer={footer}/>} />
    </Routes>
    <ToastContainer />
  </div>

  );
}