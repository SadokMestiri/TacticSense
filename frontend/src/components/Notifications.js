import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Notifications.css';

const Notifications = ({ header, footer }) => {
    const user_id = localStorage.getItem('user_id');
    const [user, setUser] = useState({});
    const [users, setUsers] = useState([]);
    const [error, setError] = useState(null);
    const [isActivityOpen, setIsActivityOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [playerId, setPlayerId] = useState(null);

    useEffect(() => {
        const fetchPlayerId = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/player_id/${user_id}`);
                setPlayerId(response.data.player_id);
            } catch (error) {
                console.error("Erreur lors de la récupération du player ID:", error);
            }
        };

        if (user_id) {
            fetchPlayerId();
        }
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

    useEffect(() => {
        const fetchNotifications = async () => {
            if (!playerId) return;
            try {
                const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/notifications/${playerId}`);
                console.log("Notifications reçues:", response.data);
                setNotifications(response.data);
            } catch (error) {
                console.error("Error fetching notifications:", error);
            }
        };

        if (playerId) {
            console.log("Fetching notifications for player ID:", playerId);
            fetchNotifications();
        }
    }, [playerId]);

    const handleNotificationClick = async (notifId) => {
        try {
            await axios.post(`${process.env.REACT_APP_BASE_URL}/notifications/read/${notifId}`);
            // Marquer comme lue localement
            setNotifications((prevNotifs) =>
                prevNotifs.map((notif) =>
                    notif.id === notifId ? { ...notif, is_read: true } : notif
                )
            );
        } catch (error) {
            console.error("Erreur lors du marquage de la notification comme lue:", error);
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
                            <h3>{user.role}</h3>
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
                    <div className="notifications-page">
                        <h2>Notifications</h2>
                        {notifications.map((notif) => (
                            <div
                                key={notif.id}
                                className="notif-item"
                                onClick={() => handleNotificationClick(notif.id)}
                                style={{ cursor: 'pointer' }}
                            >
                                <div className="notif-coach-img">
                                    {notif.coach_image ? (
                                        <img src={`${process.env.REACT_APP_BASE_URL}/${notif.coach_image}`} alt="Coach" />
                                    ) : (
                                        <img src="/assets/images/default-profile.png" alt="Default Coach" />
                                    )}
                                </div>
                                <div className="notif-text">
                                    <p>{notif.message}</p>
                                    <small>{notif.timestamp ? new Date(notif.timestamp).toLocaleString() : "N/A"}</small>
                                </div>
                                {!notif.is_read && <div className="notif-dot" />}
                            </div>
                        ))}
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

export default Notifications;
