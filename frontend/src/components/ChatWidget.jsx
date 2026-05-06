import React, { useState, useRef, useEffect } from 'react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import './ChatWidget.css'

const ChatWidget = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: "Hello! I'm your AI assistant. How can I help you today?",
            sender: 'bot',
            timestamp: new Date()
        }
    ])
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async (text) => {
        if (!text.trim()) return

        // Add user message
        const userMessage = {
            id: Date.now(),
            text: text,
            sender: 'user',
            timestamp: new Date()
        }
        setMessages(prev => [...prev, userMessage])
        setIsLoading(true)

        try {
            // Call backend API
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: text, stream: false })
            })

            if (!response.ok) {
                throw new Error('Network response was not ok')
            }

            const data = await response.json()

            // Add bot response
            const botMessage = {
                id: Date.now() + 1,
                text: data.answer,
                sender: 'bot',
                timestamp: new Date()
            }
            setMessages(prev => [...prev, botMessage])
        } catch (error) {
            console.error('Error:', error)
            // Error message
            const errorMessage = {
                id: Date.now() + 1,
                text: "Sorry, I'm having trouble connecting. Please try again later.",
                sender: 'bot',
                timestamp: new Date(),
                isError: true
            }
            setMessages(prev => [...prev, errorMessage])
        } finally {
            setIsLoading(false)
        }
    }

    const toggleWidget = () => {
        setIsOpen(!isOpen)
    }

    return (
        <>
            {/* Chat Button */}
            <button className="chat-button" onClick={toggleWidget}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="white" />
                </svg>
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className="chat-window">
                    <div className="chat-header">
                        <h3>AI Assistant</h3>
                        <button className="close-button" onClick={toggleWidget}>×</button>
                    </div>

                    <div className="chat-messages">
                        {messages.map((message) => (
                            <ChatMessage key={message.id} message={message} />
                        ))}
                        {isLoading && (
                            <div className="typing-indicator">
                                <span>AI is thinking</span>
                                <div className="dot-floating">
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
                </div>
            )}
        </>
    )
}

export default ChatWidget