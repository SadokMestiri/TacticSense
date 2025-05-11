

import Home from "./components/Home";
import {Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Chat from "./components/Chat";
import Header from "./components/Header";
import Reset from "./components/Reset";
import ResetPassword from "./components/ResetPassword";
import SinglePost from "./components/SinglePost";
import PlayerPredictor from './components/PlayerPredictor';
import ExistingPlayerPredictor from './components/ExistingPlayerPredictor';
import PlayerProfile from './components/PlayerProfile';
import SavedPosts from './components/SavedPosts';
export default function App() {

  const header = (<Header/>);

  return (

    <div>
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/Home" element={<Home header={header} />} />
      <Route path="/Chat" element={<Chat header={header}/>} />
      <Route path="/Register" element={<Register/>} />
      <Route path="/header" element={<Header />} />
      <Route path="/Reset" element={<Reset/>}/>
      <Route path="/ResetPassword" element={<ResetPassword/>}/>
      <Route path="/post" element={<SinglePost header={header} />} />
      <Route path="/StatPredictions/new" element={<PlayerPredictor />} />
      <Route path="/StatPredictions/existing" element={<ExistingPlayerPredictor />} />
      <Route path="/player/:name" element={<PlayerProfile />} />
      <Route path="/saved-posts" element={<SavedPosts header={header} />} />
    </Routes>
  </div>
    
  );
}