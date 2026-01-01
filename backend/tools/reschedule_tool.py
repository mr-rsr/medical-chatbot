from langchain.tools import tool
from backend.api.calendly_integration import CalendlyService
from datetime import datetime, timedelta
import json
from zoneinfo import ZoneInfo

@tool
async def reschedule_appointment_tool(current_booking_uuid: str, current_scheduled_event_uuid: str, new_slot_time: str, new_scheduled_event_uuid: str, patient_email: str, patient_name: str) -> str:
    """
    Reschedule an existing appointment to a new time slot.
    
    Args:
        current_booking_uuid: Invitee UUID of the existing booking
        current_scheduled_event_uuid: UUID of current scheduled event
        new_slot_time: New appointment time
        new_scheduled_event_uuid: UUID of new scheduled event slot
        patient_email: Patient email (from memory)
        patient_name: Patient name (from memory)
    
    Returns:
        Confirmation message with new booking details
    """
    try:
        ist = ZoneInfo("Asia/Kolkata")
        service = CalendlyService()
        
        try:
            existing_event = await service.get_scheduled_event(current_booking_uuid)
        except Exception as e:
            return f"Error: Could not find booking with UUID {current_booking_uuid}. Please verify the booking ID."
        
        event_types = await service.get_event_types()
        if not event_types:
            return "Error: No event types available."
        
        event_type_uri = event_types[0]["uri"]
        
        try:
            if "T" in new_slot_time:
                new_datetime = datetime.fromisoformat(new_slot_time.replace("Z", "+00:00")).astimezone(ist)
            else:
                new_datetime = datetime.strptime(new_slot_time, "%Y-%m-%d %I:%M %p").replace(tzinfo=ist)
        except:
            return f"Error: Invalid date format for new slot time: {new_slot_time}"
        
        if new_datetime < datetime.now(ist):
            return f"Error: Cannot reschedule to a past date. Requested: {new_slot_time}"
        
        if not new_scheduled_event_uuid:
            return "Error: New scheduled event UUID required. Please select from available slots."
        
        cancel_success = await service.cancel_invitee(current_booking_uuid, current_scheduled_event_uuid)
        
        if not cancel_success:
            return "Error: Failed to cancel the existing appointment. Rescheduling aborted."
        
        new_booking = await service.create_booking(
            scheduled_event_uuid=new_scheduled_event_uuid,
            invitee_email=patient_email,
            invitee_name=patient_name,
            invitee_notes="Rescheduled appointment"
        )
        
        new_invitee_uuid = new_booking.get("invitee_uuid", "")
        
        result = {
            "booking_uuid": new_invitee_uuid,
            "scheduled_event_uuid": new_scheduled_event_uuid,
            "patient_name": patient_name,
            "patient_email": patient_email,
            "slot_time": new_slot_time
        }
        
        return f"""Appointment rescheduled successfully!

New Booking Details:
- Patient: {patient_name}
- Email: {patient_email}
- New Time: {new_slot_time}
- New Booking ID: {new_invitee_uuid}

You will receive a confirmation email.

BOOKING_DATA: {json.dumps(result)}"""
    
    except Exception as e:
        return f"Error rescheduling appointment: {str(e)}"
