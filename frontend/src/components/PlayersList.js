import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StarRatings from 'react-star-ratings';
import { toast } from "react-toastify";
import './PlayersList.css';

const PlayersList = ({ header, footer }) => {
    const user_id = localStorage.getItem('user_id');
    const [user, setUser] = useState({});
    const [userImages, setUserImages] = useState({});
    const [users, setUsers] = useState([]);
    const [error, setError] = useState(null);
    const [isActivityOpen, setIsActivityOpen] = useState(false);
    const [players, setPlayers] = useState([]);

    const fetchPlayers = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_players`);
            setPlayers(response.data);
        } catch (error) {
            setError(error.response?.data?.message || 'Error fetching players');
        }
    };
    useEffect(() => {
        fetchUser();
        fetchPlayers();
    }, [user_id]);


    const fetchUsers = async (user_id) => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${user_id}`);

            setUsers(prevUsers => ({
                ...prevUsers,
                [user_id]: response.data.profile_image
            }));
        } catch (error) {
            setError(error.response?.data?.message || 'Error fetching user data');
        }
    };
    const fetchUser = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_user/${user_id}`);

            setUser(response.data);
        } catch (error) {
            setError(error.response?.data?.message || 'Error fetching user data');
        }
    };
    useEffect(() => {
        fetchUser();
    }, [user_id]);

    const handleRatingChange = async (playerId, rating) => {
        try {
            const response = await fetch("http://127.0.0.1:5000/rate_player", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ id: playerId, score: rating, user_id: user_id }),
            });

            const data = await response.json();
            if (response.ok) {
                console.log("Score mis à jour :", data.average_score);
                setPlayers(prevPlayers =>
                    prevPlayers.map(player =>
                        player.id === playerId
                            ? { ...player, score: data.average_score }
                            : player
                    )
                );
                toast.success("✅ Score ajouté avec succès !", {
                    position: "top-center"
                });
            } else {
                console.error("Erreur backend :", data.message);
                toast.warning(`⚠️ ${data.message || "Erreur lors de l'envoi du score."}`, {
                    position: "top-center"
                });
            }
        } catch (err) {
            alert("Erreur de connexion au serveur.");
            toast.error("❌ Erreur de connexion au serveur.", {
                position: "top-center"
            });

        }
    };


    return (
        <div>
            {header}

            <div className="container">
                <div className="left-sidebar">
                    <div className="sidebar-profile-box">
                        <img src="assets/images/cover-pic.jpg" alt="cover" width="100%" />
                        <div className="sidebar-profile-info">
                            <img src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`} alt="profile" />
                            <h1>{user.name}</h1>
                            <h3><h3>{user.role}</h3></h3>
                            <ul>
                                <li>Your profile views <span>24K</span></li>
                                <li>Your post views <span>128K</span></li>
                                <li>Your Connections <span>108K</span></li>
                            </ul>
                        </div>
                        <div className="sidebar-profile-link">
                            <a href="#"><img src="assets/images/items.svg" alt="items" />My Items</a>
                            <a href="#"><img src="assets/images/premium.png" alt="premium" />Try Premium</a>
                        </div>
                    </div>

                    {/* Activity */}
                    <div className={`sidebar-activity ${isActivityOpen ? 'open-activity' : ''}`} id="sidebarActivity">
                        <h3>RECENT</h3>
                        <a href="#"><img src="assets/images/recent.svg" alt="recent" />Data Analysis</a>
                        <a href="#"><img src="assets/images/recent.svg" alt="recent" />UI UX Design</a>
                        <a href="#"><img src="assets/images/recent.svg" alt="recent" />Web Development</a>
                        <a href="#"><img src="assets/images/recent.svg" alt="recent" />Object Oriented Programming</a>
                        <a href="#"><img src="assets/images/recent.svg" alt="recent" />Operating Systems</a>
                        <a href="#"><img src="assets/images/recent.svg" alt="recent" />Platform technologies</a>

                        <h3>GROUPS</h3>
                        <a href="#"><img src="assets/images/group.svg" alt="group" />Data Analyst group</a>
                        <a href="#"><img src="assets/images/group.svg" alt="group" />Learn NumPy</a>
                        <a href="#"><img src="assets/images/group.svg" alt="group" />Machine Learning group</a>
                        <a href="#"><img src="assets/images/group.svg" alt="group" />Data Science Aspirants</a>

                        <h3>HASHTAG</h3>
                        <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />dataanalyst</a>
                        <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />numpy</a>
                        <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />machinelearning</a>
                        <a href="#"><img src="assets/images/hashtag.svg" alt="hashtag" />datascience</a>

                        <div className="discover-more-link">
                            <a href="#">Discover More</a>
                        </div>
                    </div>

                    <p id="showMoreLink" >Show more <b>+</b></p>
                </div>
                <div className="main-content">
                    <h2>Registered Players</h2>
                    <div className="players-list">
                        {players.length > 0 ? (
                            players.map(player => (
                                <div key={player.id} className="player-card">
                                    <img src={`${process.env.REACT_APP_BASE_URL}/${player.photo}`} alt={player.name} />
                                    <div className="player-info">
                                        <h3>{player.name}</h3>
                                        <div style={{ display: "flex", gap: "20px" }}>
                                            <div style={{ marginRight: "150px" }}>
                                                <p>Age: {player.age}</p>
                                                <p>Position: {player.position}</p>
                                            </div>
                                            <div>
                                                <p>Club: {player.club}</p>
                                                <p>Score: {player.score !== null ? player.score.toFixed(2) : "N/A"}</p>
                                            </div>
                                        </div>

                                        <div className="rating">
                                            <StarRatings
                                                rating={player.score || 0}
                                                starRatedColor="gold"
                                                starHoverColor="orange"
                                                changeRating={(newRating) => handleRatingChange(player.id, newRating)}
                                                numberOfStars={5}
                                                name={`rating-${player.id}`}
                                                starDimension="24px"
                                                starSpacing="2px"
                                            />

                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p>No players found.</p>
                        )}
                    </div>
                </div>




                {/* Right Sidebar */}
                <div className="right-sidebar">
                    <div className="sidebar-news">
                        <img src="assets/images/more.svg" className="info-icon" alt="more" />
                        <h3>Trending News</h3>
                        <a href="#">High Demand for Skilled Employees</a>
                        <span>1d ago &middot; 10,934 readers</span>
                        <a href="#">Inflation in Canada Affects the Workforce</a>
                        <span>2d ago &middot; 7,043 readers</span>
                        <a href="#">Mass Recruiters fire Employees</a>
                        <span>4d ago &middot; 17,789 readers</span>
                        <a href="#">Crypto predicted to Boom this year</a>
                        <span>9d ago &middot; 2,436 readers</span>
                        <a href="#" className="read-more-link">Read More</a>
                    </div>

                    <div className="sidebar-ad">
                        <small>Ad &middot; &middot; &midd;</small>
                        <p>Master Web Development</p>
                        <div>
                            <img src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`} alt="user" />
                            <img src="assets/images/mi-logo.png" alt="mi logo" />
                        </div>
                        <b>Brand and Demand in Xiaomi</b>
                        <a href="#" className="ad-link">Learn More</a>
                    </div>

                    <div className="sidebar-useful-links">
                        <a href="#">About</a>
                        <a href="#">Accessibility</a>
                        <a href="#">Help Center</a>
                        <a href="#">Privacy Policy</a>
                        <a href="#">Advertising</a>
                        <a href="#">Get the App</a>
                        <a href="#">More</a>
                        <div className="copyright-msg">
                            <img src="assets/images/logo.png" alt="logo" />
                            <p>MetaScout &#169; 2025. All Rights Reserved</p>
                        </div>
                    </div>
                </div>
            </div>
            {footer}
        </div>
    );
};
export default PlayersList;
