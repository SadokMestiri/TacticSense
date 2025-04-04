

import Home from "./components/Home";
import {Routes, Route } from "react-router-dom";
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
      <Route path="/post" element={<SinglePost header={header} footer={footer} />} />
      <Route path="/jobs" element={<Jobs header={header} footer={footer} />} />
      <Route path="/jobDetails" element={<JobDetails header={header} footer={footer} />} />
      <Route path="/jobApplications" element={<JobApplications header={header} footer={footer} />} />
      <Route path="/hashtag" element={<HashtagPage header={header} footer={footer} />} />
    </Routes>
  </div>
    
  );
}