import React, { useState, useEffect, useRef, useCallback } from 'react'
import './App.css'

function App() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState([{
        id: 1,
        text: "👋 Hi! I'm your assistant. I can help you with pricing, features, and product details.\n\nWhat would you like to know?",
        sender: 'bot'
    }])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [currentResponse, setCurrentResponse] = useState('')
    const [isStreaming, setIsStreaming] = useState(false)
    const [isConnected, setIsConnected] = useState(false)

    const messagesEnd = useRef(null)
    const wsRef = useRef(null)
    const reconnectTimeoutRef = useRef(null)
    const isConnectingRef = useRef(false)

    const scrollToBottom = () => {
        messagesEnd.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, currentResponse])

    // Setup WebSocket connection - runs once
    useEffect(() => {
        let isMounted = true

        const connectWebSocket = () => {
            // Prevent multiple connection attempts
            if (isConnectingRef.current) {
                console.log('Connection already in progress, skipping...')
                return
            }

            isConnectingRef.current = true
            const wsUrl = `ws://localhost:8000/ws/client_${Date.now()}`
            console.log('Connecting to WebSocket...')

            const ws = new WebSocket(wsUrl)

            ws.onopen = () => {
                if (!isMounted) return
                console.log('WebSocket connected successfully')
                setIsConnected(true)
                isConnectingRef.current = false
            }

            ws.onmessage = (event) => {
                if (!isMounted) return
                try {
                    const data = JSON.parse(event.data)

                    switch (data.type) {
                        case 'connected':
                            console.log('Connected with ID:', data.client_id)
                            break

                        case 'start':
                            setIsStreaming(true)
                            setIsLoading(false)
                            setCurrentResponse('')
                            break

                        case 'context':
                            setMessages(prev => [...prev, {
                                id: Date.now(),
                                text: data.message,
                                sender: 'system',
                                isContext: true
                            }])
                            break

                        case 'chunk':
                            setCurrentResponse(prev => prev + data.content)
                            break

                        case 'complete':
                            if (data.full_response) {
                                setMessages(prev => [...prev, {
                                    id: Date.now(),
                                    text: data.full_response,
                                    sender: 'bot'
                                }])
                            }
                            setCurrentResponse('')
                            setIsStreaming(false)
                            break

                        case 'error':
                            setMessages(prev => [...prev, {
                                id: Date.now(),
                                text: data.content,
                                sender: 'bot',
                                error: true
                            }])
                            setIsStreaming(false)
                            setIsLoading(false)
                            break
                    }
                } catch (error) {
                    console.error('Error parsing message:', error)
                }
            }

            ws.onerror = (error) => {
                console.error('WebSocket error:', error)
                if (isMounted) {
                    setIsConnected(false)
                }
                isConnectingRef.current = false
            }

            ws.onclose = () => {
                console.log('WebSocket disconnected')
                if (isMounted) {
                    setIsConnected(false)
                    // Attempt to reconnect after 5 seconds (only once)
                    if (reconnectTimeoutRef.current) {
                        clearTimeout(reconnectTimeoutRef.current)
                    }
                    reconnectTimeoutRef.current = setTimeout(() => {
                        if (isMounted) {
                            console.log('Attempting to reconnect...')
                            connectWebSocket()
                        }
                    }, 5000)
                }
                isConnectingRef.current = false
            }

            wsRef.current = ws
        }

        connectWebSocket()

        // Cleanup function
        return () => {
            isMounted = false
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current)
            }
            if (wsRef.current) {
                wsRef.current.close()
                wsRef.current = null
            }
        }
    }, []) // Empty dependency array - only run once

    const sendMessage = useCallback(() => {
        if (!input.trim() || isLoading || isStreaming) return

        const userMsg = {
            id: Date.now(),
            text: input,
            sender: 'user'
        }
        setMessages(prev => [...prev, userMsg])
        const question = input
        setInput('')
        setIsLoading(true)

        // Check if WebSocket is connected
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ message: question }))
        } else {
            console.error('WebSocket not connected')
            setMessages(prev => [...prev, {
                id: Date.now(),
                text: "📡 Connection issue. Please refresh the page if the problem persists.",
                sender: 'bot',
                error: true
            }])
            setIsLoading(false)
        }
    }, [input, isLoading, isStreaming])

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    const suggestedQuestions = [
        { text: "💰 Pricing", question: "What are your pricing plans?" },
        { text: "⚡ Features", question: "What features do you offer?" },
        { text: "🔌 Integrations", question: "What integrations are available?" },
        { text: "🎧 Support", question: "How do I get support?" },
        { text: "🔒 Security", question: "Tell me about security" }
    ]

    return (
        <div className="app">
            <div className="content">
                <h1><img src="/public/logo.png" alt="" style={{ width: '100px', marginLeft: '52px' }} />    Krimx Solutions</h1>
                <p>AI-Powered Customer Support Automation</p>
                <div className="connection-status">
                    {isConnected ? (
                        <span className="status-connected">✅ Connected</span>
                    ) : (
                        <span className="status-connecting">⏳ Connecting...</span>
                    )}
                </div>
                <div className="examples">
                    {suggestedQuestions.map((q, i) => (
                        <button key={i} onClick={() => setInput(q.question)}>
                            {q.text}
                        </button>
                    ))}
                </div>
            </div>

            {!isOpen && (
                <button className="chat-button" onClick={() => setIsOpen(true)}>
                    💬
                </button>
            )}

            {isOpen && (
                <div className="chat-window">
                    <div className="chat-header">
                        <div className="header-info">
                            <span className="bot-icon"><img src="/public/logo.png" alt="" style={{ width: '40px', borderRadius: '15px' }} /></span>
                            <div>
                                <h3>Krimx Assistant</h3>
                                <p className="status-text">
                                    {isConnected ? '🟢 Online' : '🟡 Connecting...'}
                                </p>
                            </div>
                        </div>
                        <button className="close-button" onClick={() => setIsOpen(false)}>
                            ✕
                        </button>
                    </div>

                    <div className="chat-messages">
                        {messages.map(msg => (
                            <div key={msg.id} className={`message ${msg.sender}`}>
                                <div className={`bubble ${msg.error ? 'error' : ''} ${msg.isContext ? 'context' : ''}`}>
                                    <div className="message-text">
                                        {msg.text.split('\n').map((line, i) => {
                                            if (line.trim().startsWith('•')) {
                                                return <div key={i} className="bullet-point">{line}</div>
                                            }
                                            return <div key={i}>{line}</div>
                                        })}
                                    </div>
                                </div>
                            </div>
                        ))}

                        {isStreaming && currentResponse && (
                            <div className="message bot">
                                <div className="bubble streaming">
                                    <div className="message-text">
                                        {currentResponse.split('\n').map((line, i) => {
                                            if (line.trim().startsWith('•')) {
                                                return <div key={i} className="bullet-point">{line}</div>
                                            }
                                            return <div key={i}>{line}</div>
                                        })}
                                    </div>
                                    <span className="cursor">▊</span>
                                </div>
                            </div>
                        )}

                        {isLoading && !isStreaming && (
                            <div className="message bot">
                                <div className="bubble typing">
                                    <span>●</span>
                                    <span>●</span>
                                    <span>●</span>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEnd} />
                    </div>

                    <div className="chat-input">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your question..."
                            rows="1"
                            disabled={isLoading || isStreaming || !isConnected}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={isLoading || isStreaming || !input.trim() || !isConnected}
                        >
                            {isStreaming ? '⋯' : isLoading ? '⋯' : 'Send'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default App