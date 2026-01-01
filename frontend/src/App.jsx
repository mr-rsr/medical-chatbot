import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import AppointmentConfirmation from './components/AppointmentConfirmation'

function App() {
  const [bookingDetails, setBookingDetails] = useState(null)

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>🏥 Medical Appointment Scheduling</h1>
        <p style={styles.subtitle}>AI-Powered Healthcare Assistant</p>
      </header>
      
      <div style={styles.content}>
        <ChatInterface onBookingComplete={setBookingDetails} />
        {bookingDetails && (
          <AppointmentConfirmation 
            details={bookingDetails} 
            onClose={() => setBookingDetails(null)} 
          />
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  header: {
    textAlign: 'center',
    padding: '2rem',
    color: 'white'
  },
  title: {
    margin: 0,
    fontSize: '2.5rem',
    fontWeight: '700'
  },
  subtitle: {
    margin: '0.5rem 0 0 0',
    fontSize: '1.1rem',
    opacity: 0.9
  },
  content: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '0 1rem 2rem'
  }
}

export default App
