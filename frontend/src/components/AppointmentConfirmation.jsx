function AppointmentConfirmation({ details, onClose }) {
  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={styles.title}>✅ Appointment Confirmed</h2>
          <button style={styles.closeButton} onClick={onClose}>×</button>
        </div>
        
        <div style={styles.content}>
          <div style={styles.field}>
            <span style={styles.label}>Patient Name:</span>
            <span style={styles.value}>{details.patient_name}</span>
          </div>
          
          <div style={styles.field}>
            <span style={styles.label}>Email:</span>
            <span style={styles.value}>{details.patient_email}</span>
          </div>
          
          <div style={styles.field}>
            <span style={styles.label}>Appointment Time:</span>
            <span style={styles.value}>{details.slot_time}</span>
          </div>
          
          <div style={styles.field}>
            <span style={styles.label}>Booking ID:</span>
            <span style={styles.value}>{details.booking_uuid}</span>
          </div>
          
          {details.reschedule_url && (
            <div style={styles.actions}>
              <a href={details.reschedule_url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                Reschedule
              </a>
              <a href={details.cancel_url} target="_blank" rel="noopener noreferrer" style={{...styles.link, ...styles.cancelLink}}>
                Cancel
              </a>
            </div>
          )}
        </div>
        
        <div style={styles.footer}>
          <p style={styles.note}>A confirmation email has been sent to {details.patient_email}</p>
        </div>
      </div>
    </div>
  )
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  },
  modal: {
    background: 'white',
    borderRadius: '16px',
    maxWidth: '500px',
    width: '90%',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
    overflow: 'hidden'
  },
  header: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '1.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  title: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: '600'
  },
  closeButton: {
    background: 'transparent',
    border: 'none',
    color: 'white',
    fontSize: '2rem',
    cursor: 'pointer',
    lineHeight: 1
  },
  content: {
    padding: '2rem'
  },
  field: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '0.75rem 0',
    borderBottom: '1px solid #e5e7eb'
  },
  label: {
    fontWeight: '600',
    color: '#6b7280'
  },
  value: {
    color: '#1f2937',
    fontWeight: '500'
  },
  actions: {
    display: 'flex',
    gap: '1rem',
    marginTop: '1.5rem'
  },
  link: {
    flex: 1,
    textAlign: 'center',
    padding: '0.75rem',
    background: '#667eea',
    color: 'white',
    textDecoration: 'none',
    borderRadius: '8px',
    fontWeight: '600'
  },
  cancelLink: {
    background: '#ef4444'
  },
  footer: {
    background: '#f9fafb',
    padding: '1rem 2rem',
    borderTop: '1px solid #e5e7eb'
  },
  note: {
    margin: 0,
    fontSize: '0.875rem',
    color: '#6b7280',
    textAlign: 'center'
  }
}

export default AppointmentConfirmation
