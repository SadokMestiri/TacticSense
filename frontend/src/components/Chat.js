import React, { useState, useEffect,useRef } from "react";
import {
  MDBContainer,
  MDBRow,
  MDBCol,
  MDBCard,
  MDBCardBody,
  MDBIcon,
  MDBTypography,
} from "mdb-react-ui-kit";
import PerfectScrollbar from "react-perfect-scrollbar";
import "react-perfect-scrollbar/dist/css/styles.css";
import axios from "axios";
import Cookies from 'js-cookie';
import jwt_decode from 'jwt-decode';
import { useNavigate } from "react-router-dom";

function Chat() {
  const navigate = useNavigate();
  // Example in React using useState
  const reactions = [
    { name: "like", icon: "assets/images/post-like.png" },
    { name: "love", icon: "assets/images/love.png" },
    { name: "laugh", icon: "assets/images/haha.png" },
    { name: "wow", icon: "assets/images/wow.png" },
    { name: "sad", icon: "assets/images/sad.png" },
    { name: "angry", icon: "assets/images/angry.png" },
  ];
  const [activeReactionsMessageId, setActiveReactionsMessageId] = useState(null);
  const reactionRef = useRef(null); // Reference for reactions container
  const [isGroupConversation, setIsGroupConversation] = useState(false);
  const [messages, setMessages] = useState([]);
  const [conversationUser, setConversationUser] = useState(null);
  const [newMessage, setNewMessage] = useState("");
  const [conversations, setConversations] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [allUsers, setAllUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [isCreatingGroup, setIsCreatingGroup] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState("");


  const apiUrl = "http://localhost:5000";
  const token = Cookies.get('token');
  let decodedToken = token ? jwt_decode(token) : null;
  const user = JSON.parse(Cookies.get('user'));

  useEffect(() => {
    if (!token || !decodedToken) {
      navigate('/');
    } else {
      const date = decodedToken?.exp ? new Date(decodedToken?.exp * 1000) : null;
      if (date && date.getTime() < new Date().getTime()) {
        Cookies.remove('token');
        navigate('/');
      }
    }
  }, [token, decodedToken, navigate]);

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${apiUrl}/get_conversations/${user.id}`);
      setConversations(response.data);
    } catch (error) {
      console.error("Error fetching conversations:", error);
    }
  };

/*   const fetchMessages = async (conversationId) => {
    try {
      const response = await axios.get(`${apiUrl}/get_messages/${user.id}/${conversationId}`);
      setMessages(response.data);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  }; */
  const selectConversation = (conversation) => {
    setConversationUser(conversation.other_user_id);
    setConversationId(conversation.id);

    if (conversation.type === "group") {
      setIsGroupConversation(true);
    } else {
      setIsGroupConversation(false); // For one-to-one conversations
    }
    fetchConversations();
  };
  

  const fetchMessages = async (conversationId, isGroupConversation) => {
    try {
      const isGroup = isGroupConversation ? "true" : "false"; // Ensure correct query param
      const response = await axios.get(
        `${apiUrl}/get_messages/${user.id}/${conversationId}?is_group_conversation=${isGroup}`
      );
      setMessages(response.data);

      // Automatically mark all fetched messages as seen based on the conversation type
      markMessagesAsSeen(response.data, isGroupConversation);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };

  // Handle Mark as Seen for all messages after fetch
  // Function to mark messages as seen for both group and one-to-one conversations
  const markMessagesAsSeen = async (messages, isGroupConversation) => {
    try {
      // Iterate over each message to mark it as seen
      for (const msg of messages) {
        const seenBy = msg.seen_by || []; // Ensure seen_by is always an array, even if undefined
  
        if (!seenBy.includes(user.name)) {
          // Prepare the URL based on whether it's a group or a one-to-one message
          const url = isGroupConversation
            ? `${apiUrl}/mark_group_message_seen/${msg.id}`
            : `${apiUrl}/mark_message_seen/${msg.id}`;
  
          // Send the request to the server to mark the message as seen
          await axios.post(url, {
            user_id: user.id, // User marking the message as seen
          });
        }
      }
  
    } catch (error) {
      console.error("Error marking messages as seen:", error);
    }
  };
  

  useEffect(() => {
    fetchConversations();
  }, []);
  
  useEffect(() => {
    if (conversationId !== null) {
      fetchMessages(conversationId, isGroupConversation);
    }
  }, [conversationId, isGroupConversation]); // Trigger when either conversationId or isGroupConversation changes
  
/*   const handleSendMessage = async () => {
    try {
      await axios.post(`${apiUrl}/send_message`, {
        sender_id: user.id,
        receiver_id: conversationUser?.id,
        message: newMessage,
        conversation_id: conversationId,
      });
      setNewMessage("");
      fetchMessages(conversationId);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  }; */
  const handleSendMessage = async () => {
    try {
      const messageData = {
        sender_id: user.id,
        message: newMessage,
        conversation_id: conversationId,
        is_group_conversation: isGroupConversation, // Add this flag here
      };
  console.log(conversationId)
      // If it's a one-to-one conversation, add the receiver_id
      if (!isGroupConversation) {
        messageData.receiver_id = conversationUser; // Only for one-to-one
      }
  console.log(user.id,newMessage,conversationId,conversationUser)
      // Send the message to the backend
      await axios.post(`${apiUrl}/send_message`, messageData);
  
      setNewMessage(""); // Clear the message input
      fetchMessages(conversationId,isGroupConversation); // Refresh the message list
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };
  
  
  
  const handleGroupSelection = (userId) => {
    setSelectedUsers(prevSelected =>
      prevSelected.includes(userId)
        ? prevSelected.filter(id => id !== userId)
        : [...prevSelected, userId]
    );
  };

  const handleCreateGroupChat = async () => {
    try {
      const response = await axios.post(`${apiUrl}/create_group`, {
        name: groupName, // Make sure this matches the server-side 'name' key
        user_ids: [...selectedUsers, user.id], // Add current user to group
      });
      console.log("Group chat created:", response.data);
      setIsCreatingGroup(false);
    } catch (error) {
      console.error("Error creating group chat:", error);
    }
  };
  
const handleCreateConversation = async () => {
  if (!selectedUserId) return;

  try {
    const response = await axios.post(`${apiUrl}/create_conversation`, {
      user1_id: user.id,
      user2_id: selectedUserId,
    });

    const newConversation = response.data;
    setConversations(prev => [...prev, newConversation]);
    setConversationUser(selectedUserId);
    setConversationId(newConversation.id);
    setIsGroupConversation(false);
    fetchMessages(newConversation.id, false);  // Fetch 1-to-1 messages
    setSelectedUserId("");  // Reset dropdown
  } catch (error) {
    console.error("Error creating conversation:", error);
  }
};
  useEffect(() => {
    const fetchAllUsers = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_BASE_URL}/get_users`);
        setAllUsers(response.data);
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    };

    fetchAllUsers();
  }, []);
  const handleReaction = async (messageId, conversationId, isGroup, reactionName) => {
    try {
      const response = await axios.post(`${apiUrl}/add_message_reaction`, {
        message_id: messageId,
        conversation_id: conversationId,  // Send conversation ID to differentiate
        is_group: isGroup,  // Whether it's a group conversation or not
        reaction_name: reactionName,
        user_id: user.id,
      });
  
      // Update the message's reactions in the frontend
      const updatedReactions = response.data.reactions;
  
      const updatedMessages = messages.map((msg) =>
        msg.id === messageId && msg.conversation_id === conversationId
          ? { ...msg, reactions: updatedReactions }  // Update reactions for this specific message
          : msg
      );
  
      setMessages(updatedMessages); // Update state with the new messages including reactions
      toggleReactions();
    } catch (error) {
      console.error("Error adding reaction:", error);
    }
  };
  

  // Toggle the visibility of reactions for the selected message
  const toggleReactions = (messageId, e) => {
    e.stopPropagation();
    setActiveReactionsMessageId((prev) => (prev === messageId ? null : messageId));
  };

  // Close reactions if clicked outside of the reactions container
  const closeReactionsIfOutside = (e) => {
    if (reactionRef.current && !reactionRef.current.contains(e.target)) {
      setActiveReactionsMessageId(null);
    }
  };

  useEffect(() => {
    document.addEventListener("click", closeReactionsIfOutside);
    return () => {
      document.removeEventListener("click", closeReactionsIfOutside);
    };
  }, []);


  // Modify the fetchReactions function to mark the message as having fetched reactions
  const fetchReactions = async (messageId, conversationId, isGroupConversation) => {
    try {
      const response = await axios.get(`${apiUrl}/get_message_reactions`, {
        params: { message_id: messageId, conversation_id: conversationId },
      });
  
      // Check if both conversation type and message group status match
      const isGroupMessage = response.data.is_group;
  
      if (isGroupMessage === isGroupConversation) {
        // If both are true or both are false, update the reactions
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.id === messageId
              ? { ...msg, reactions: response.data.reactions, reactionsFetched: true }
              : msg
          )
        );
      } else {
        // If one is true and the other is false, don't show the reactions
        console.log("Reaction group type does not match conversation type. Not displaying reactions.");
      }
    } catch (error) {
      console.error("Error fetching reactions:", error);
    }
  };
  

  return (
    <div>
      <MDBContainer fluid className="py-5" style={{ backgroundColor: "#cccc" }}>
        <MDBRow>
          <MDBCol md="12">
            <MDBCard id="chat3" style={{ borderRadius: "15px" }}>
              <MDBCardBody>
                <MDBRow>
                  <MDBCol md="6" lg="5" xl="4" className="mb-4 mb-md-0">
                    <div className="p-3">
                      <PerfectScrollbar style={{ position: "relative", height: "400px" }}>
                        <div className="mb-3">
  <label htmlFor="userSelect" className="form-label">Start New Chat</label>
  <div className="d-flex">
    <select
      id="userSelect"
      className="form-select me-2"
      value={selectedUserId}
      onChange={(e) => setSelectedUserId(e.target.value)}
    >
      <option value="">Select User</option>
      {allUsers
        .filter((u) => u.id !== user.id)  // Exclude self
        .map((u) => (
          <option key={u.id} value={u.id}>
            {u.name}
          </option>
        ))}
    </select>
    <button className="btn btn-success" onClick={handleCreateConversation}>
      Chat
    </button>
  </div>
</div>

                      <MDBTypography listUnStyled className="mb-0">
  {conversations.map((conv, index) => (
    <li
      key={index}
      className="p-2 border-bottom"
      onClick={() => selectConversation(conv)}
    >
      <a href="#!" className="d-flex justify-content-between">
        <div className="d-flex flex-row">
          <div>
          {conv.type === 'group' ? (
  <div className="d-flex align-items-center">
  {conv.users.slice(0, 2).map((user, idx) => (
    <div 
      key={user.id}  // Use a unique identifier for each key, assuming user.id is unique
      style={{
        position: 'relative',
        left: `${idx * -10}px`, // Shift second image slightly to the right
        top: `${idx * 15}px`,   // Shift second image slightly upwards
      }}
    >
<img
  src={`${process.env.REACT_APP_BASE_URL}/${user.profile_image}`}
  alt="avatar"
  className="d-flex align-self-center"
  style={{
    width: "30px",
    aspectRatio: "1 / 1",              // Makes it square
    height: "auto",                    // Maintains proportions
    objectFit: "cover",                // Prevents distortion
    borderRadius: "50%",              // Needed for circular shape
    boxShadow: "0 2px 5px rgba(0, 0, 0, 0.2)",
    transition: "transform 0.2s ease-in-out",
  }}
/>


    </div>
  ))}
</div>
   ) : (
              // One-to-one conversation: display the other user's profile image
              <img
                src={`${process.env.REACT_APP_BASE_URL}/${conv.profile_image}`}
                alt="avatar"
                className="d-flex align-self-center me-3"
                width="60"
                style={{ borderRadius: "50%" }}
              />
            )}
            <span className="badge bg-success badge-dot"></span>
          </div>
          <div className="pt-1">
            <p className="fw-bold mb-0" style={{ color: "#28a745" }}>
              {conv.name}
            </p>
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
    </MDBTypography>
  )}
</MDBTypography>

                      </PerfectScrollbar>
                    </div>
                    <button onClick={() => setIsCreatingGroup(true)} className="btn btn-primary w-100 mt-3">
                      Create Group Chat
                    </button>
                  </MDBCol>

                  {isCreatingGroup && (
                    <div className="modal" style={{ display: "block" }}>
                      <div className="modal-content">
                        <h5>Create Group Chat</h5>
                        <input
                          type="text"
                          value={groupName}
                          onChange={(e) => setGroupName(e.target.value)}
                          placeholder="Group name"
                          className="form-control"
                        />
                        <div className="mt-2">
                          {allUsers.map((user) => (
                            <div
                              key={user.id}
                              className="p-2"
                              style={{ cursor: "pointer" }}
                              onClick={() => handleGroupSelection(user.id)}
                            >
                              {user.name} {selectedUsers.includes(user.id) && '✔'}
                            </div>
                          ))}
                        </div>
                        <button onClick={handleCreateGroupChat} className="btn btn-success mt-3">
                          Create Group
                        </button>
                        <button onClick={() => setIsCreatingGroup(false)} className="btn btn-secondary mt-3">
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  <MDBCol md="6" lg="7" xl="8">


                  <PerfectScrollbar style={{ position: "relative", height: "400px" }} className="pt-3 pe-3">
  {conversationUser &&
    messages.map((msg, index) => {
      // Fetch reactions if not already fetched
      if (!msg.reactionsFetched) {
        fetchReactions(msg.id, conversationId, isGroupConversation);
      }

      return (
        <div
          key={index}
          className={`d-flex flex-row ${msg.sender_id === user.id ? "justify-content-end" : "justify-content-start"}`}
        >
          <img
            src={`${process.env.REACT_APP_BASE_URL}/${msg.sender_image}`}
            alt="avatar"
            style={{ width: "45px", height: "100%", borderRadius: "50%" }}
          />
          <div>
            <p
              className="small p-2 ms-3 mb-1 rounded-3"
              style={{
                backgroundColor: msg.sender_id === conversationUser?.id ? "#28a745" : "#f5f6f7",
                color: msg.sender_id === conversationUser?.id ? "#ffffff" : "#000000",
              }}
            >
              {msg.message}
            </p>
            <p className="small ms-3 mb-0 text-muted">
              <span>{msg.timestamp}</span>
              <MDBIcon
                far
                icon="smile"
                size="lg"
                className="ms-2"
                style={{ cursor: "pointer" }}
                onClick={(e) => toggleReactions(msg.id, e)} // Opens reactions for the selected message
              />
            </p>

            {activeReactionsMessageId === msg.id && (
              <div ref={reactionRef} className="d-flex flex-row justify-content-start mt-2">
                {/* Reaction selection (adding new reactions) */}
                {reactions.map((reaction, index) => (
                  <img
                    key={index}
                    src={reaction.icon}
                    alt={reaction.name}
                    className="reaction-icon"
                    style={{ width: "20px", height: "20px", cursor: "pointer", margin: "1px" }}
                    onClick={() => handleReaction(msg.id, conversationId, isGroupConversation, reaction.name)} // Handle adding reaction
                  />
                ))}
              </div>
            )}

            {/* Display reactions if they exist */}
{msg.reactions ? (
  <div className="message-reactions d-flex flex-row mt-2">
    {/* Aggregate reactions and display only one per reaction type */}
    {Object.keys(msg.reactions).map((reactionName, index) => {
      const totalCount = msg.reactions[reactionName].count;
      const reactionIcon = reactions.find((r) => r.name === reactionName)?.icon;

      // If the reaction icon is found, display it
      return reactionIcon ? (
        <div key={index} style={{ marginRight: '5px', marginTop: '-50px', marginLeft: '10px' }}>
          {/* Display one icon per reaction type */}
          <img
            src={reactionIcon} // Use the corresponding icon path
            alt={reactionName}
            className="reaction-icon"
            style={{ width: '18px', height: '18px' }}
          />
          <span
            className="reaction-count"
            style={{ fontSize: '12px', marginLeft: '3px' }}
          >
            {totalCount} {/* Display the total count for this reaction */}
          </span>
        </div>
      ) : null;
    })}
  </div>
) : (
  <div className="message-reactions d-flex flex-row mt-2">
    {/* Optional: Loading or placeholder message */}
  </div>
)}

          </div>
        </div>
      );
    })}
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
    </div>
  );
}

export default Chat;
