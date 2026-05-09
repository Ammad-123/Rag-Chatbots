import React, { useState, useRef, useEffect, useCallback } from 'react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import './ChatWidget.css'

const STORAGE_KEY = 'techstore_chat_history'

const getWelcomeMessage = () => ({
    id: 1,
    text: "I can help you with:\n• Product information & prices\n• Returns & refunds\n• Shipping details\n• Current deals\n\nWhat would you like to know?",
    sender: 'bot',
    timestamp: new Date()
})

const loadMessages = () => {
    try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
            const parsed = JSON.parse(saved)
            return parsed.map(m => ({
                ...m,
                timestamp: new Date(m.timestamp)
            }))
        }
    } catch (e) {
        console.error('Failed to load chat history:', e)
    }
    return [getWelcomeMessage()]
}

const ChatWidget = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState(loadMessages)
    const [isLoading, setIsLoading] = useState(false)
    const [streamingText, setStreamingText] = useState('')
    const messagesEndRef = useRef(null)
    const wsRef = useRef(null)
    const clientIdRef = useRef(`client_${Date.now()}`)

    // Persist messages to localStorage
    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
    }, [messages])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, streamingText, isLoading])

    // WebSocket connection
    useEffect(() => {
        if (!isOpen) return

        const clientId = clientIdRef.current
        const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`)
        wsRef.current = ws

        ws.onopen = () => {
            console.log('WebSocket connected')
        }

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)

            if (data.type === 'chunk') {
                setStreamingText(prev => prev + data.content)
                setIsLoading(true)
            } else if (data.type === 'complete') {
                setStreamingText(prev => {
                    if (prev.trim()) {
                        const botMessage = {
                            id: Date.now(),
                            text: prev,
                            sender: 'bot',
                            timestamp: new Date()
                        }
                        setMessages(msgs => [...msgs, botMessage])
                    }
                    return ''
                })
                setIsLoading(false)
            } else if (data.type === 'start') {
                setStreamingText('')
                setIsLoading(true)
            } else if (data.type === 'sources') {
                // Sources received - can be used for display if needed
            }
        }

        ws.onerror = (error) => {
            console.error('WebSocket error:', error)
            setIsLoading(false)
        }

        ws.onclose = () => {
            console.log('WebSocket disconnected')
            setIsLoading(false)
        }

        return () => {
            ws.close()
        }
    }, [isOpen])

    const sendMessage = useCallback(async (text) => {
        if (!text.trim()) return

        const userMessage = {
            id: Date.now(),
            text: text,
            sender: 'user',
            timestamp: new Date()
        }
        setMessages(prev => [...prev, userMessage])
        setIsLoading(true)
        setStreamingText('')

        // Try WebSocket first
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ message: text }))
        } else {
            // Fallback to REST API
            try {
                const response = await fetch('http://localhost:8000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: text })
                })

                if (!response.ok) {
                    throw new Error('Network response was not ok')
                }

                const data = await response.json()

                const botMessage = {
                    id: Date.now() + 1,
                    text: data.answer,
                    sender: 'bot',
                    timestamp: new Date()
                }
                setMessages(prev => [...prev, botMessage])
            } catch (error) {
                console.error('Error:', error)
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
    }, [])

    const toggleWidget = () => {
        setIsOpen(!isOpen)
    }

    const clearChat = () => {
        const welcome = getWelcomeMessage()
        setMessages([welcome])
        localStorage.removeItem(STORAGE_KEY)
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
                        <div className="header-info">
                            <img src="/images/logo.png" alt="TechStore" className="chat-logo" />
                            <div className="header-text">
                                <h3>TechStore Assistant</h3>
                                <span className="status-indicator">
                                    <span className="status-dot"></span> Live
                                </span>
                            </div>
                        </div>
                        <button className="close-button" onClick={toggleWidget}>×</button>
                    </div>

                    <div className="chat-messages">
                        {messages.map((message) => (
                            <ChatMessage key={message.id} message={message} />
                        ))}
                        {streamingText && (
                            <ChatMessage message={{
                                id: 'streaming',
                                text: streamingText,
                                sender: 'bot',
                                timestamp: new Date()
                            }} />
                        )}
                        {isLoading && !streamingText && (
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