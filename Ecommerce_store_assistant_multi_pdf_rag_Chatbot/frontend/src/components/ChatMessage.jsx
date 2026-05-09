import React from 'react'
import './ChatMessage.css'

const ChatMessage = ({ message }) => {
    const isUser = message.sender === 'user'

    return (
        <div className={`message-container ${isUser ? 'user' : 'bot'}`}>
            <div className={`message-bubble ${isUser ? 'user-bubble' : 'bot-bubble'} ${message.isError ? 'error' : ''}`}>
                <div className="message-text">{message.text}</div>
                <div className="message-time">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
            </div>
        </div>
    )
}

export default ChatMessage