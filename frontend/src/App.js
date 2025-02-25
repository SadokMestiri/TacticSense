

import Home from "./components/Home";
import {Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";



export default function App() {



  return (

      <div>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/Login" element={<Login />} />
          <Route path="/Chat" element={<Chat/>} />
          <Route path="/Register" element={<Register/>} />
        </Routes>
      </div>
    
  );
}