

import Home from "./components/Home";
import Profile from "./components/Profile";
import Profile_View from "./components/Profile_View";
import Manager_View from "./components/ManagerProfileView";
import Coach_View from "./components/CoachProfileView";
import CoachProfile from "./components/CoachProfile";
import ClubProfile from "./components/ClubProfile";
import ManagerProfile from "./components/ManagerProfile";
import AgentProfile from "./components/AgentProfile";
import AgencyProfile from "./components/AgencyProfile";
import {Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Reset from "./components/Reset";
import ResetPassword from "./components/ResetPassword";
import SinglePost from "./components/SinglePost";
import ManagerProfileView from "./components/ManagerProfileView";
import CoachProfileView from "./components/CoachProfileView";




export default function App() {

  const header = (<Header/>);
  const footer = (<Footer/>);

  return (

    <div>
    <Routes>
      <Route path="/" element={<Login header={header} footer={footer}/>} />
      <Route path="/Home" element={<Home header={header} />} />
      <Route path="/Chat" element={<Chat header={header}/>} />
      <Route path="/Profile" element={<Profile header={header}/>} />
      <Route path="/Profile_View" element={<Profile_View header={header}/>} />
      <Route path="/Manager_View" element={<ManagerProfileView header={header}/>} />
      <Route path="/Coach_View" element={<CoachProfileView header={header}/>} />
      <Route path="/CoachProfile" element={<CoachProfile header={header}/>} />
      <Route path="/ClubProfile" element={<ClubProfile header={header}/>} />
      <Route path="/ManagerProfile" element={<ManagerProfile header={header}/>} />
      <Route path="/AgentProfile" element={<AgentProfile header={header}/>} />
      <Route path="/AgencyProfile" element={<AgencyProfile header={header}/>} />
      <Route path="/Register" element={<Register/>} />
      <Route path="/header" element={<Header />} />
      <Route path="/footer" element={<Footer />} />
      <Route path="/Reset" element={<Reset/>}/>
      <Route path="/ResetPassword" element={<ResetPassword/>}/>
      <Route path="/post" element={<SinglePost header={header} />} />
    </Routes>
  </div>
    
  );
}