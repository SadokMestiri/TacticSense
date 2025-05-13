import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './GPT.css';
import Cookies from 'js-cookie';


const GPT = () => {
    const [question, setQuestion] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);
    const user_id = localStorage.getItem('user_id');
    const [users, setUsers] = useState([]);
    const [error, setError] = useState(null);
      const [metaBalance, setMetaBalance] = useState(null);
      const [metaCoinMessage, setMetaCoinMessage] = useState(false);
      const [checkingBalance, setCheckingBalance] = useState(false);
    const [isActivityOpen, setIsActivityOpen] = useState(false);
const userCookie = Cookies.get('user');
const user = userCookie ? JSON.parse(userCookie) : null;
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


    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await axios.post('http://127.0.0.1:8000/generate', {
                prompt: question
            });
            console.log(prompt);
            console.log(res.data.response);
            setResponse(res.data.response);
        } catch (error) {
            setResponse('Une erreur est survenue.');
        } finally {
            setLoading(false);
        }
    };
 const checkBalance = async () => {
    setCheckingBalance(true);

    try {
        const response = await axios.get(
            `${process.env.REACT_APP_BASE_URL}/check_balance/${user.id}`,
        );

        if (response.status === 200 && response.data?.balance !== undefined) {
            setMetaBalance(response.data.balance);
        } else {
            setMetaCoinMessage("Failed to retrieve MetaCoin balance.");
        }
    } catch (error) {
        const errMsg = error.response?.data?.error || "Error checking balance.";
        setMetaCoinMessage(errMsg);
    } finally {
        setCheckingBalance(false);
    }
};

    const formatResponse = (text) => {
        // Remplace les éléments entre *...* par du <strong>...</strong>
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    };

    return (
        <div>
    

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
<a href="#" onClick={checkBalance} style={{ width: "60px", cursor: "pointer" }}>
    <img src="assets/images/metacoin.png" alt="metacoin" style={{ width: "50px"}} />
    {checkingBalance ? "Checking..." : metaBalance !== null ? `Balance: ${metaBalance} MC` : "Check MetaCoin Balance"}
</a>
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
                    <div style={{ textAlign: 'center', marginBottom: '20px', padding: '10px' }}>
                        <h1 style={{ fontSize: '2.5em', color: '#333', marginBottom: '10px' }}>
                            Ask MetaScout AI
                        </h1>
                        <p style={{ fontSize: '1.1em', color: '#555', maxWidth: '600px', margin: '0 auto' }}>
                            Engage with our AI assistant specialized in the soccer industry. Ask questions about tactics, player analysis, market trends, or anything football-related!
                        </p>
                    </div>
                    <div className="create-post" style={{ height: 'auto', minHeight: '500px', paddingBottom: '20px' }}>
                        <form onSubmit={handleSubmit} className="w-full max-w-md" style={{ paddingTop: '30px'}}>
                            <div style={{ marginLeft: '50px'}}>
                                <textarea
                                    value={question}
                                    style={{ width:'500px', height:'200px'}}
                                    onChange={(e) => setQuestion(e.target.value)}
                                    placeholder="Ask a question..."
                                    className="w-full p-3 border border-gray-300 rounded-xl mb-4 resize-y min-h-[120px] focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                className="send-chat-btn"
                                style={{marginLeft: '450px', width:'100px' }}
                            >
                                {loading ? 'Loading...' : 'Send'}
                            </button>
                            
                        </form>
                        {response && (
                            <div className="mt-6 bg-white p-4 rounded shadow max-w-xl w-full" style={{ border: '1px solid green', maxHeight: '300px', overflowY: 'auto' }}>
                                <h2 className="font-semibold mb-2">Response :</h2>
                                <div dangerouslySetInnerHTML={{ __html: formatResponse(response) }} />
                            </div>
                        )}
                        <div style={{ textAlign: 'center', marginTop: '20px', padding: '10px', fontSize: '0.9em', color: '#777', maxWidth: '600px', margin: '0 auto' }}>
                            <p>
                                🤖 Please be aware that AI-generated responses can sometimes be inaccurate or incomplete. Always cross-reference critical information.
                            </p>
                        </div>
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
                        <small>Ad</small>
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

        </div>
    );
};
export default GPT;
