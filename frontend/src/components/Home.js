import React, { useState } from 'react';


const Home = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isActivityOpen, setIsActivityOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);



  const toggleActivity = () => {
    setIsActivityOpen(!isActivityOpen);
  };

  const toggleMenu = () => {
      setProfileMenuOpen(prevState => !prevState);
  };

  const posts = [
    {
        author: 'Bejamin Leo',
        title: 'Founder and CEO at Giva | Angel Investor',
        time: '2 hours ago',
        content: 'The success of every website depends on Search engine optimisation and digital marketing strategy...',
        image: 'assets/images/post-image-1.png',
        likes: 89,
        comments: 22,
        shares: 40
    },
    {
        author: 'Claire Smith',
        title: 'SDE at Swiggy | Solopreneur',
        time: '2 hours ago',
        content: 'The success of every website depends on Search engine optimisation and digital marketing strategy...',
        image: 'assets/images/post-image-2.png',
        likes: 60,
        comments: 12,
        shares: 28
    },
    {
        author: 'Rohit Kumar',
        title: 'Senior Developer at Google | Tech Enthusiast',
        time: '1 day ago',
        content: 'Just finished reading an amazing article on React hooks! I highly recommend checking it out.',
        image: 'assets/images/post-image-3.png',
        likes: 120,
        comments: 34,
        shares: 56
    },
    {
        author: 'Samantha Doe',
        title: 'Marketing Lead at Meta | Content Strategist',
        time: '5 days ago',
        content: 'Digital marketing strategies are changing rapidly, here’s how you can adapt to the new trends...',
        image: 'assets/images/post-image-4.png',
        likes: 72,
        comments: 18,
        shares: 31
    }
];

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-left">
          <a href="index.html" className="meta-logo"><img src="assets/images/logo.png" alt="logo" /></a>
          <div className="search-box">
            <img src="assets/images/search.png" alt="search" />
            <input type="text" placeholder="Search for anything" />
          </div>
        </div>
        <div className="navbar-center">
          <ul>
            <li><a href="#" className="active-link"><img src="assets/images/home.png" alt="home" /> <span>Home</span></a></li>
            <li><a href="#"><img src="assets/images/network.png" alt="network" /> <span>My Network</span></a></li>
            <li><a href="#"><img src="assets/images/jobs.png" alt="jobs" /> <span>Jobs</span></a></li>
            <li><a href="#"><img src="assets/images/message.png" alt="message" /> <span>Messaging</span></a></li>
            <li><a href="#"><img src="assets/images/notification.png" alt="notification" /> <span>Notifications</span></a></li>
          </ul>
        </div>
        <div className="navbar-right">
          <div className="online">
            <img src="assets/images/user-1.jpg" className="nav-profile-img" onClick={toggleMenu} alt="profile" />
          </div>
        </div>

        {/* Dropdown menu */}
        {isMenuOpen && (
          <div className="profile-menu-wrap">
            <div className="profile-menu">
              <div className="user-info">
                <img src="assets/images/user-1.jpg" alt="user" />
                <div>
                  <h3>John Doe</h3>
                  <a href="#">See your profile</a>
                </div>
              </div>
              <hr />
              <a href="#" className="profile-menu-link">
                <img src="assets/images/feedback.png" alt="feedback" />
                <p>Give Feedback</p>
                <span></span>
              </a>
              <a href="#" className="profile-menu-link">
                <img src="assets/images/setting.png" alt="settings" />
                <p>Settings & Privacy</p>
                <span></span>
              </a>
              <a href="#" className="profile-menu-link">
                <img src="assets/images/help.png" alt="help" />
                <p>Help & Support</p>
                <span></span>
              </a>
              <a href="#" className="profile-menu-link">
                <img src="assets/images/display.png" alt="display" />
                <p>Display & Accessibility</p>
                <span></span>
              </a>
              <a href="#" className="profile-menu-link">
                <img src="assets/images/logout.png" alt="logout" />
                <p>Logout</p>
                <span></span>
              </a>
            </div>
          </div>
        )}
      </nav>

      <div className="container">
        <div className="left-sidebar">
          <div className="sidebar-profile-box">
            <img src="assets/images/cover-pic.jpg" alt="cover" width="100%" />
            <div className="sidebar-profile-info">
              <img src="assets/images/user-1.jpg" alt="profile" />
              <h1>Cristiano Ronaldo</h1>
              <h3>Professional footballer</h3>
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

          <p id="showMoreLink" onClick={toggleActivity}>Show more <b>+</b></p>
        </div>

        {/* Main Content */}
        <div className="main-content">
          {/* Create Post Section */}
          <div className="create-post">
            <div className="create-post-input">
              <img src="assets/images/user-1.jpg" alt="profile" />
              <textarea rows="2" placeholder="Write Something"></textarea>
            </div>
            <div className="create-post-links">
              <li><img src="assets/images/photo.svg" alt="photo" />Photo</li>
              <li><img src="assets/images/video.svg" alt="video" />Video</li>
              <li><img src="assets/images/event.svg" alt="event" />Event</li>
              <li>Post</li>
            </div>
          </div>

          {/* Sorting */}
          <div className="sort-by">
            <hr />
            <p>Sort by : <span>top <img src="assets/images/down-arrow.png" alt="down-arrow" /></span> </p>
          </div>

          {/* Posts */}
                {posts.map((post, index) => (
                    <div key={index} className="post">
                        <div className="post-author">
                            <img src="assets/images/user-3.png" alt="user" />
                            <div>
                                <h1>{post.author}</h1>
                                <small>{post.title}</small>
                                <small>{post.time}</small>
                            </div>
                        </div>
                        <p>{post.content}</p>
                        <img src={post.image} width="100%" alt="post" />
                        <div className="post-stats">
                            <div>
                                <img src="assets/images/thumbsup.png" alt="like" />
                                <img src="assets/images/love.png" alt="love" />
                                <img src="assets/images/clap.png" alt="clap" />
                                <span className="liked-users">{`Adam Doe and ${post.likes} others`}</span>
                            </div>
                            <div>
                                <span>{`${post.comments} comments &middot; ${post.shares} shares`}</span>
                            </div>
                        </div>
                        <div className="post-activity">
                            <div>
                                <img src="assets/images/user-1.jpg" className="post-activity-user-icon" alt="user-icon" />
                                <img src="assets/images/down-arrow.png" className="post-activity-arrow-icon" alt="arrow-icon" />
                            </div>
                            <div className="post-activity-link">
                                <img src="assets/images/like.png" alt="like-icon" />
                                <span>Like</span>
                            </div>
                            <div className="post-activity-link">
                                <img src="assets/images/comment.png" alt="comment-icon" />
                                <span>Comment</span>
                            </div>
                            <div className="post-activity-link">
                                <img src="assets/images/share.png" alt="share-icon" />
                                <span>Share</span>
                            </div>
                            <div className="post-activity-link">
                                <img src="assets/images/send.png" alt="send-icon" />
                                <span>Send</span>
                            </div>
                        </div>
                    </div>
                ))}
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
              <img src="assets/images/user-1.jpg" alt="user" />
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

export default Home;
