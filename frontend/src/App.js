

import Home from "./components/Home";
import {Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Header from "./components/Header";
import Footer from "./components/Footer";
import GPT from "./components/GPT";
import PlayersList from "./components/PlayersList";




export default function App() {

  const header = (<Header/>);
  const footer = (<Footer/>);

  return (

      <div>
        <Routes>
          <Route path="/" element={<Home header={header} footer={footer}/>} />
          <Route path="/Login" element={<Login />} />
          <Route path="/Chat" element={<Chat/>} />
          <Route path="/Register" element={<Register/>} />
          <Route path="/header" element={<Header />} />
          <Route path="/footer" element={<Footer />} />
          <Route path="/gpt" element={<GPT header={header} footer={footer}/>} />
          <Route path="/players" element={<PlayersList header={header} footer={footer}/>} />
        </Routes>
      </div>
    
  );
}