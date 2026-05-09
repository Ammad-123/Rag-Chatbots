import React, { useState } from 'react'
import './ChatInput.css'

const ChatInput = ({ onSendMessage, disabled }) => {
    const [input, setInput] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        if (input.trim() && !disabled) {
            onSendMessage(input)
            setInput('')
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
        }
    }

    return (
        <form className="chat-input-form" onSubmit={handleSubmit}>
            <textarea
                className="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about products, returns, shipping..."
                disabled={disabled}
                rows={1}
            />
            <button
                type="submit"
                className="send-button"
                disabled={disabled || !input.trim()}
            >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor" />
                </svg>
            </button>
        </form>
    )
}

export default ChatInput