import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

function ChatInterface({ onBookingComplete }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your medical appointment assistant. How can I help you today?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await axios.post('/api/chat', {
        message: userMessage,
        session_id: sessionId
      })

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response 
      }])

      if (response.data.booking_details) {
        onBookingComplete(response.data.booking_details)
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.messagesContainer}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            ...styles.message,
            ...(msg.role === 'user' ? styles.userMessage : styles.assistantMessage)
          }}>
            <div style={styles.messageContent}>{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div style={{...styles.message, ...styles.assistantMessage}}>
            <div style={styles.messageContent}>
              <span style={styles.typing}>●●●</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} style={styles.inputForm}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          style={styles.input}
          disabled={loading}
        />
        <button type="submit" style={styles.button} disabled={loading}>
          Send
        </button>
      </form>
    </div>
  )
}

const styles = {
  container: {
    background: 'white',
    borderRadius: '12px',
    boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    height: '600px'
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem'
  },
  message: {
    display: 'flex',
    maxWidth: '75%'
  },
  userMessage: {
    alignSelf: 'flex-end',
    justifyContent: 'flex-end'
  },
  assistantMessage: {
    alignSelf: 'flex-start'
  },
  messageContent: {
    padding: '0.75rem 1rem',
    borderRadius: '12px',
    lineHeight: '1.5',
    whiteSpace: 'pre-wrap'
  },
  userMessage: {
    alignSelf: 'flex-end'
  },
  'userMessage messageContent': {
    background: '#667eea',
    color: 'white'
  },
  assistantMessage: {
    alignSelf: 'flex-start'
  },
  typing: {
    animation: 'pulse 1.5s infinite'
  },
  inputForm: {
    display: 'flex',
    gap: '0.5rem',
    padding: '1rem',
    borderTop: '1px solid #e5e7eb',
    background: '#f9fafb'
  },
  input: {
    flex: 1,
    padding: '0.75rem 1rem',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '1rem',
    outline: 'none'
  },
  button: {
    padding: '0.75rem 2rem',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer'
  }
}

styles.userMessage.messageContent = {
  background: '#667eea',
  color: 'white'
}

styles.assistantMessage.messageContent = {
  background: '#f3f4f6',
  color: '#1f2937'
}

export default ChatInterface
