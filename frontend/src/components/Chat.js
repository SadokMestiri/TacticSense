import React, { useState, useEffect } from "react";
import {
  MDBContainer,
  MDBRow,
  MDBCol,
  MDBCard,
  MDBCardBody,
  MDBIcon,
  MDBTypography,
  MDBInputGroup,
} from "mdb-react-ui-kit";
import PerfectScrollbar from "react-perfect-scrollbar";
import "react-perfect-scrollbar/dist/css/styles.css";
import axios from "axios";

export default function Chat() {
  const [user, setUser] = useState(null); // Holds the logged-in user
  const [messages, setMessages] = useState([]); // Messages between users
  const [conversationUser, setConversationUser] = useState(null); // User selected for conversation
  const [newMessage, setNewMessage] = useState(""); // New message input
const senderId = 4; // Logged-in user ID
const conversationUserId = 6; // Selected conversation user ID
  // Base API URL
  const apiUrl = "http://localhost:5000"; // Update with your backend URL



  // Fetch messages between the logged-in user and the selected conversation user
  const fetchMessages = async () => {
    if (conversationUser) {
      try {
        const response = await axios.get(
          `${apiUrl}/get_messages/${senderId}/${conversationUserId}`
        );
        console.log(response.data)
        setMessages(response.data);
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    }
  };

  // Handle sending a message
  const handleSendMessage = async () => {
    try {
      await axios.post(`${apiUrl}/send_message`, {
        sender_id: senderId,
        receiver_id: conversationUserId,
        message: newMessage,
      });
      setNewMessage(""); // Clear the input field after sending the message
      fetchMessages(); // Refresh the messages
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  // Handle selecting a conversation
  const selectConversation = (selectedUser) => {
    setConversationUser(selectedUser);
    fetchMessages(); // Fetch messages for the selected conversation
  };

  useEffect(() => {
  
      // Fetch the initial conversation list (if needed) and messages
      fetchMessages();
    
  }, []);

  console.log(messages)
  

  return (
    <MDBContainer fluid className="py-5" style={{ backgroundColor: "#cccc" }}>
      <MDBRow>
        <MDBCol md="12">
          <MDBCard id="chat3" style={{ borderRadius: "15px" }}>
            <MDBCardBody>
              <MDBRow>
                <MDBCol md="6" lg="5" xl="4" className="mb-4 mb-md-0">
                  <div className="p-3">
                    <PerfectScrollbar  style={{ position: "relative", height: "400px" }}>
                      <MDBTypography listUnStyled className="mb-0">
                        {/* List of users to chat with */}
                        <li
                          className="p-2 border-bottom"
                          onClick={() => selectConversation({ id: 2, name: "Marie Horwitz" })} // Example: Selecting Marie for chat
                        >
                          <a href="#!" className="d-flex justify-content-between">
                            <div className="d-flex flex-row">
                              <div>
                                <img
                                  src="assets/images/user-5.png"
                                  alt="avatar"
                                  className="d-flex align-self-center me-3"
                                  width="60"
                                  style={{ borderRadius: "50%" }}
                                />
                                <span className="badge bg-success badge-dot"></span>
                              </div>
                              <div className="pt-1">
                                <p className="fw-bold mb-0">Marie Horwitz</p>
                                <p className="small text-muted">Hello, Are you there?</p>
                              </div>
                            </div>
                            <div className="pt-1">
                              <p className="small text-muted mb-1">Just now</p>
                              <span className="badge bg-danger rounded-pill float-end">3</span>
                            </div>
                          </a>
                        </li>
                      </MDBTypography>
                    </PerfectScrollbar>
                  </div>
                </MDBCol>

                <MDBCol md="6" lg="7" xl="8">
                  <PerfectScrollbar  style={{ position: "relative", height: "400px" }} className="pt-3 pe-3">
                    {messages.map((msg, index) => (
                      <div
                        key={index}
                        className={`d-flex flex-row ${msg.sender_id === user.id ? "justify-content-end" : "justify-content-start"}`}
                      >
                        <img
                          src="assets/images/user-5.png"
                          alt="avatar 1"
                          style={{ width: "45px", height: "100%", borderRadius: "50%" }}
                        />
                        <div>
                          <p
                            className="small p-2 ms-3 mb-1 rounded-3"
                            style={{ backgroundColor: msg.sender_id === user.id ? "#0d6efd" : "#f5f6f7" }}
                          >
                            {msg.message}
                          </p>
                          <p className="small ms-3 mb-3 rounded-3 text-muted float-end">
                            {new Date(msg.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </PerfectScrollbar>

                  <div className="d-flex justify-content-start align-items-center pe-3 pt-3 mt-2">
                    <input
                      type="text"
                      className="form-control form-control-lg"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type message"
                    />
                    <a className="ms-3" href="#!" onClick={handleSendMessage}>
                      <MDBIcon fas icon="paper-plane" />
                    </a>
                  </div>
                </MDBCol>
              </MDBRow>
            </MDBCardBody>
          </MDBCard>
        </MDBCol>
      </MDBRow>
    </MDBContainer>
  );
}
