from langchain.tools import tool
from backend.api.calendly_integration import CalendlyService

@tool
async def cancel_appointment_tool(booking_uuid: str, scheduled_event_uuid: str, cancellation_reason: str = "") -> str:
    """
    Cancel an existing appointment.
    
    Args:
        booking_uuid: Invitee UUID of the booking to cancel
        scheduled_event_uuid: UUID of the scheduled event
        cancellation_reason: Optional reason for cancellation
    
    Returns:
        Cancellation confirmation message
    """
    try:
        service = CalendlyService()
        
        try:
            existing_event = await service.get_scheduled_event(booking_uuid)
        except Exception as e:
            return f"Error: Could not find booking with UUID {booking_uuid}. Please verify the booking ID."
        
        if not scheduled_event_uuid:
            return "Error: Scheduled event UUID required for cancellation."
        
        cancel_success = await service.cancel_invitee(booking_uuid, scheduled_event_uuid)
        
        if cancel_success:
            return f"""Appointment cancelled successfully.

Booking ID: {booking_uuid}
Reason: {cancellation_reason if cancellation_reason else "Not specified"}

If you'd like to book a new appointment, I'm here to help!

CANCELLED_BOOKING: {booking_uuid}"""
        else:
            return f"Error: Failed to cancel appointment {booking_uuid}."
    
    except Exception as e:
        return f"Error cancelling appointment: {str(e)}"
