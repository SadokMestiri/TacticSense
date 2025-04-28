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
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";

function Chat({ header }) {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]); // Messages between users
  const [conversationUser, setConversationUser] = useState(null); // User selected for conversation
  const [newMessage, setNewMessage] = useState(""); // New message input
  const [conversations, setConversations] = useState([]); // List of conversations
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const conversationUserId = conversationUser?.id;
  const apiUrl = "http://localhost:5000"; // Update with your backend URL
const token = Cookies.get('token');
let decodedToken = null;
let exp = null;

if (token) {
  decodedToken = jwt_decode(token);
  exp = decodedToken?.exp;
}

const date = exp ? new Date(exp * 1000) : null;
const now = new Date();
const [allowed, setAllowed] = useState(false);
const user =  JSON.parse(Cookies.get('user'));
// Token expiration check
useEffect(() => {
  if (!token || !decodedToken) {
    navigate('/login');
  } else if (date && date.getTime() < now.getTime()) {
    Cookies.remove('token');
    navigate('/login');
  } else {
    setAllowed(true);
  }
}, [token, decodedToken, navigate, date]);


  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${apiUrl}/get_conversations/${user.id}`);
      setConversations(response.data);
    } catch (error) {
      console.error("Error fetching conversations:", error);
    }
  };

  // Fetch messages between the logged-in user and the selected conversation user
  const fetchMessages = async (conversationId) => {
    if (conversationUser) {
      try {
        const response = await axios.get(
          `${apiUrl}/get_messages/${user.id}/${conversationUserId}`
        );
        console.log(response.data);
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
        sender_id: user.id,
        receiver_id: conversationUserId,
        message: newMessage,
        conversation_id: conversationId,
      });
      setNewMessage(""); // Clear the input field after sending the message
      fetchMessages(); // Refresh the messages
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  // Handle selecting a conversation
  const selectConversation = async (selectedUser) => {
    setConversationUser(selectedUser);
    setConversationId(selectedUser.conversation_id);

    // Create conversation if it doesn't exist
    try {
      const response = await axios.post(`${apiUrl}/create_conversation`, {
        user1_id: user.id,
        user2_id: selectedUser.id,
      });

      // Get conversation data
      const conversationData = response.data;
      if (conversationData.conversation_id) {
        fetchMessages(conversationData.conversation_id); // Fetch messages for new conversation
      }
    } catch (error) {
      console.error("Error selecting conversation:", error);
    }
  };

  const markAsSeen = async (messageId) => {
    try {
      await axios.post(`${apiUrl}/mark_message_seen/${messageId}`);
    } catch (error) {
      console.error("Error marking message as seen:", error);
    }
  };

  const handleMessageDisplay = (msg) => {
    console.log(msg);
    // Mark the message as seen if the sender is not the current user
    if (msg.sender_id !== user.id && !msg.seen) {
      markAsSeen(msg.id);
    }
  };
  useEffect(() => {
    // Fetch the initial list of conversations
    fetchConversations();
    console.log(conversations);
  }, []); // Fetch conversations when component mounts

  useEffect(() => {
    // Fetch the initial messages if there's a selected conversation
    if (conversationUserId) {
      fetchMessages();
    }
  }, [conversationUserId]); // Re-run when conversationUserId changes

  console.log(messages);


  return (
    <div>
      {header}
      <MDBContainer fluid className="py-5" style={{ backgroundColor: "#cccc" }}>
        <MDBRow>
          <MDBCol md="12">
            <MDBCard id="chat3" style={{ borderRadius: "15px" }}>
              <MDBCardBody>
                <MDBRow>
                  <MDBCol md="6" lg="5" xl="4" className="mb-4 mb-md-0">
                    <div className="p-3">
                      <PerfectScrollbar style={{ position: "relative", height: "400px" }}>
                        <MDBTypography listUnStyled className="mb-0">
                          {/* List of users to chat with */}
                          {conversations.map((conv, index) => (
                            <li
                              key={index}
                              className="p-2 border-bottom"
                              onClick={() => selectConversation(conv)}
                            >
                              <a href="#!" className="d-flex justify-content-between">
                                <div className="d-flex flex-row">
                                  <div>
                                    <img
                                      src={`${process.env.REACT_APP_BASE_URL}/${conv.profile_image}`} // You can dynamically add the image here
                                      alt="avatar"
                                      className="d-flex align-self-center me-3"
                                      width="60"
                                      style={{ borderRadius: "50%" }} />
                                    <span className="badge bg-success badge-dot"></span>
                                  </div>
                                  <div className="pt-1">
                                  <p className="fw-bold mb-0" style={{ color: "#28a745" }}>{conv.name}</p>
                                  <p className="small text-muted">{conv.last_message}</p>
                                  </div>
                                </div>
                                <div className="pt-1">
                                  <p className="small text-muted mb-1">{conv.last_time}</p>
                                  {conv.unread_count > 0 && (
                                    <span className="badge bg-danger rounded-pill float-end">
                                      {conv.unread_count}
                                    </span>
                                  )}
                                </div>

                              </a>
                            </li>
                          ))}
                          {conversations.length === 0 && (
                            <MDBTypography tag="p" className="text-center mt-5">
                              No conversations found
                            </MDBTypography>)}
                        </MDBTypography>
                      </PerfectScrollbar>
                    </div>
                  </MDBCol>
                  <MDBCol md="6" lg="7" xl="8">
                    <PerfectScrollbar style={{ position: "relative", height: "400px" }} className="pt-3 pe-3">
                      {conversationUser && messages.map((msg, index) => (
                        <div
                          key={index}
                          className={`d-flex flex-row ${msg.sender_id === user.id ? "justify-content-end" : "justify-content-start"}`}
                          onLoad={() => handleMessageDisplay(msg)}
                        >
                          <img
                            src={`${process.env.REACT_APP_BASE_URL}/${msg.sender_image}`}
                            alt="avatar 1"
                            style={{ width: "45px", height: "100%", borderRadius: "50%" }} />
                          <div>
                            <p
                              className="small p-2 ms-3 mb-1 rounded-3"
                              style={{ 
                                backgroundColor: msg.sender_id === conversationUserId ? "#28a745" : "#f5f6f7",
                                color: msg.sender_id === conversationUserId ? "#ffffff" : "#000000"
                              }}
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
                        placeholder="Type message" />
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
    </div>
  );
}
export default Chat;