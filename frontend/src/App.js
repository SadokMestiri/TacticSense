

import Home from "./components/Home";
import {Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Header from "./components/Header";
import Reset from "./components/Reset";
import ResetPassword from "./components/ResetPassword";
import SinglePost from "./components/SinglePost";




export default function App() {

  const header = (<Header/>);

  return (

      <div>
        <Routes>
        <Route path="/" element={<Home header={header} />} />
        <Route path="/Login" element={<Login />} />
          <Route path="/Chat" element={<Chat header={header}/>} />
          <Route path="/Register" element={<Register/>} />
          <Route path="/header" element={<Header />} />
          <Route path="/Reset" element={<Reset/>}/>
          <Route path="/ResetPassword" element={<ResetPassword/>}/>
          <Route path="/post" element={<SinglePost header={header} />} />
        </Routes>
      </div>
    
  );
}