

import Home from "./components/Home";
import Profile from "./components/Profile";
import {Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Reset from "./components/Reset";
import ResetPassword from "./components/ResetPassword";
import SinglePost from "./components/SinglePost";




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