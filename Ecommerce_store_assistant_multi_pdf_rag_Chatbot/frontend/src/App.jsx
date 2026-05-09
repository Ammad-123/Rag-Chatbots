import React, { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{
    id: 'welcome',
    text: "🛍️ Welcome to TechStore Pro!\n\nI can help you with:\n• Product information & prices\n• Returns & refunds\n• Shipping details\n\nWhat would you like to know?",
    sender: 'bot',
    timestamp: new Date()
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // Restored Product Data
  const products = [
    { id: 1, name: "iPhone 15 Pro", price: "$999", image: "📱", tag: "HOT" },
    { id: 2, name: "MacBook Pro M3", price: "$1,599", image: "💻", tag: "NEW" },
    { id: 3, name: "AirPods Pro 2", price: "$199", image: "🎧", tag: "SALE" },
    { id: 4, name: "Samsung S24 Ultra", price: "$1,199", image: "📱", tag: "PRE-ORDER" }
  ];

  const quickQuestions = [
    { text: "📦 Return policy", query: "What's your return policy?" },
    { text: "🚚 Shipping time", query: "How long does shipping take?" },
    { text: "🏷️ Current deals", query: "What are this week's deals?" }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const sendMessage = async (text = input) => {
    if (!text.trim() || isLoading) return;

    const userMsg = {
      id: Date.now(),
      text: text,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    if (!isOpen) setIsOpen(true);

    try {
      const response = await fetch('http://127.0.0.1:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: data.content,
        sources: data.sources,
        sender: 'bot',
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: "❌ Sorry, I'm having trouble connecting to the server. Please check if the backend is running.",
        sender: 'bot',
        timestamp: new Date(),
        error: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app ecommerce">
      <div className="hero-section">
        <h1>🛍️ TechStore Pro</h1>
        <p>Your AI-Powered Electronics Shopping Assistant</p>

        {/* Products Grid */}
        <div className="products-grid">
          {products.map(product => (
            <div key={product.id} className="product-card">
              <div className="product-image">{product.image}</div>
              <div className="product-info">
                <h3>{product.name}</h3>
                <div className="product-price">{product.price}</div>
                {product.tag && <span className="product-tag">{product.tag}</span>}
                <button className="ask-button" onClick={() => sendMessage(`Tell me about ${product.name}`)}>
                  Ask AI
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Questions */}
        <div className="quick-help">
          <h3>⚡ Quick Questions</h3>
          <div className="quick-buttons">
            {quickQuestions.map((q, i) => (
              <button key={i} onClick={() => sendMessage(q.query)}>
                {q.text}
              </button>
            ))}
          </div>
        </div>
      </div>

      {!isOpen && (
        <button className="chat-button" onClick={() => setIsOpen(true)}>💬</button>
      )}

      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="header-info">
              <span className="bot-icon">🤖</span>
              <div>
                <h3>Assistant</h3>
                <p className="status-text">Online</p>
              </div>
            </div>
            <button className="close-button" onClick={() => setIsOpen(false)}>✕</button>
          </div>

          <div className="chat-messages">
            {messages.map(msg => (
              <div key={msg.id} className={`message ${msg.sender}`}>
                <div className={`bubble ${msg.error ? 'error' : ''}`}>
                  <div className="message-text">{msg.text}</div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">📚 Sources: {msg.sources.join(', ')}</div>
                  )}
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message bot">
                <div className="bubble typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
              placeholder="Type your message..."
              disabled={isLoading}
            />
            <button onClick={() => sendMessage()} disabled={!input.trim() || isLoading}>
              {isLoading ? '...' : 'Send'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;