from langchain.tools import tool
from backend.api.calendly_integration import CalendlyService
from datetime import datetime
import json
from zoneinfo import ZoneInfo
import os

@tool
async def book_appointment_tool(slot_time: str, patient_name: str, patient_email: str, event_type_uri: str, start_time_iso: str, patient_notes: str = "") -> str:
    """
    Book an appointment at the specified time slot.
    
    Args:
        slot_time: Appointment time from availability results (e.g., "2025-11-03 12:30 PM")
        patient_name: Full name of the patient
        patient_email: Email address of the patient
        event_type_uri: Event type URI from availability results
        start_time_iso: ISO format start time from availability results
        patient_notes: Optional notes or reason for visit
    
    Returns:
        Confirmation message with booking details
    """
    try:
        timezone = os.getenv("TIMEZONE", "Asia/Kolkata")
        
        if not event_type_uri or not start_time_iso:
            return "Error: Event type URI and start time are required. Please use a slot from the available options."
        
        service = CalendlyService()
        
        booking = await service.create_booking(
            event_type_uri=event_type_uri,
            start_time=start_time_iso,
            invitee_email=patient_email,
            invitee_name=patient_name,
            invitee_notes=patient_notes,
            timezone=timezone
        )
        
        invitee_uuid = booking.get("invitee_uuid", "")
        status = booking.get("status", "active")
        cancel_url = booking.get("cancel_url", "")
        reschedule_url = booking.get("reschedule_url", "")
        event_uri = booking.get("event_uri", "")
        
        result = {
            "booking_uuid": invitee_uuid,
            "event_uri": event_uri,
            "patient_name": patient_name,
            "patient_email": patient_email,
            "slot_time": slot_time,
            "status": status,
            "cancel_url": cancel_url,
            "reschedule_url": reschedule_url
        }
        
        return f"""Appointment booked successfully!

Booking Details:
- Patient: {patient_name}
- Email: {patient_email}
- Time: {slot_time}
- Booking ID: {invitee_uuid}
- Status: {status}

Reschedule: {reschedule_url}
Cancel: {cancel_url}

You will receive a confirmation email at {patient_email}.

BOOKING_DATA: {json.dumps(result)}"""
    
    except Exception as e:
        return f"Error booking appointment: {str(e)}"
