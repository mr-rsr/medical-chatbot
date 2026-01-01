from langchain.tools import tool
from backend.api.calendly_integration import CalendlyService
from datetime import datetime, timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo
import os
import json


@tool
async def get_availability_tool(date_preference: str, appointment_type: str, time_preference: str = "any") -> str:
    """
    Fetch available appointment slots from Calendly.
    
    Args:
        date_preference: Preferred date in YYYY-MM-DD format
        appointment_type: Type of appointment (General Consultation, Follow-up, Physical Exam, Specialist Consultation)
        time_preference: Time preference - "morning" (before 12 PM), "afternoon" (12 PM - 5 PM), "evening" (after 5 PM), or "any"
    
    Returns:
        Formatted string of available time slots
    """
    try:
        timezone = os.getenv("TIMEZONE", "Asia/Kolkata")
        tz = ZoneInfo(timezone)
        requested_date = datetime.fromisoformat(date_preference).date()
        today = datetime.now(tz).date()
        
        if requested_date < today:
            return f"Cannot fetch availability for past dates. Requested: {date_preference}, Today: {today}. Please provide a future date."
        
        service = CalendlyService()
        event_types = await service.get_event_types()
        
        if not event_types:
            return "No event types available. Please contact support."
        
        appointment_mapping = {
            "general consultation": "30min",
            "follow-up": "15min",
            "physical exam": "45min",
            "specialist consultation": "60min"
        }
        
        target_duration = appointment_mapping.get(appointment_type.lower())
        event_type_uri = None
        
        for event_type in event_types:
            if target_duration and target_duration in event_type.get("name", "").lower():
                event_type_uri = event_type["uri"]
                break
        
        if not event_type_uri:
            event_type_uri = event_types[0]["uri"]
        
        start_date = datetime.fromisoformat(date_preference).date()
        start_time = datetime.combine(start_date, datetime.min.time()).isoformat()
        end_time = datetime.combine(start_date + timedelta(days=7), datetime.min.time()).isoformat()
        
        availability = await service.get_availability(event_type_uri, start_time, end_time)
        
        if not availability:
            return f"No available slots found for {appointment_type} around {date_preference}. Please try a different date or call (555) 123-4567 for last-minute cancellations."
        
        slots_by_date = defaultdict(list)
        slot_data = []
        
        for slot in availability:
            if not isinstance(slot, dict):
                continue
                
            slot_time_utc = datetime.fromisoformat(slot["start_time"].replace("Z", "+00:00"))
            slot_time = slot_time_utc.astimezone(tz)
            hour = slot_time.hour
            
            if time_preference == "morning" and hour >= 12:
                continue
            elif time_preference == "afternoon" and (hour < 12 or hour >= 17):
                continue
            elif time_preference == "evening" and hour < 17:
                continue
            
            start_time_iso = slot["start_time"]
            
            date_key = slot_time.strftime('%A, %B %d')
            time_str = slot_time.strftime('%I:%M %p')
            slots_by_date[date_key].append({"time": time_str})
            slot_data.append({
                "time": slot_time.strftime('%Y-%m-%d %I:%M %p'),
                "start_time": start_time_iso,
                "event_type_uri": event_type_uri
            })
        
        if not slots_by_date:
            return f"No {time_preference} slots available for {appointment_type}. Available times are outside your preferred time range. Would you like to see all available times?"
        
        result = f"Available {time_preference} slots for {appointment_type}:\n\n"
        for date, times in list(slots_by_date.items())[:5]:
            result += f"{date}:\n"
            for slot_info in times[:5]:
                result += f"  - {slot_info['time']}\n"
        
        if slot_data:
            result += f"\n\nSLOT_DATA:{json.dumps(slot_data[:10])}"
        return result.strip()
    
    except ValueError as e:
        return f"Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}"
    except Exception as e:
        return f"Error fetching availability: {str(e)}"
