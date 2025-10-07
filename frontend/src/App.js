import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    { role: "agent", text: "Hi, I'm Alex! How can I help you today :)?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      if (data.response) {
        setMessages((msgs) => [...msgs, { role: "agent", text: data.response }]);     
      } else {
        setMessages((msgs) => [...msgs, { role: "agent", text: data.error || "No response from agent." }]);
      }
    } catch (err) {
      setMessages((msgs) => [...msgs, { role: "agent", text: "Network error." }]);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      {/* <div className="header">  
        <h1>Welcome to Contoso Pizza</h1>
      </div> */}
      <div className="website-background">
        <img src="bg.jpeg" alt="Website Background" />
      </div>
      <div className="chat-container">
        <div className="chat-box">
          <div className="messages">
            {messages.map((msg, i) => (
              <div key={i} className={msg.role === "user" ? "user-msg" : "agent-msg"}>
                <b>{msg.role === "user" ? "You" : "Agent"}:</b> {msg.text}
              </div>
            ))}
            {loading && <div className="agent-msg">Agent is typing...</div>}
          </div>
          <form onSubmit={sendMessage} style={{display: "flex", gap: 8}}>
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
              autoFocus
            />
            <button type="submit" disabled={loading || !input.trim()}>Send</button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
