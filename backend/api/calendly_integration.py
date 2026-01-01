import httpx
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CalendlyService:
    def __init__(self):
        self.api_key = os.getenv("CALENDLY_API_KEY")
        if not self.api_key:
            raise ValueError("CALENDLY_API_KEY not found in environment variables")
        
        self.api_key = self.api_key.strip()
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_user_uri(self) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/users/me",
                headers=self.headers
            )
            if response.status_code == 401:
                raise Exception("Invalid Calendly API token. Please check your CALENDLY_API_KEY in .env file")
            response.raise_for_status()
            data = response.json()
            return data["resource"]["uri"]
    
    async def get_event_types(self) -> List[Dict]:
        user_uri = await self.get_user_uri()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/event_types",
                headers=self.headers,
                params={"user": user_uri}
            )
            response.raise_for_status()
            data = response.json()
            return data["collection"]
    
    async def get_event_type_details(self, event_type_uri: str) -> Dict:
        event_type_uuid = event_type_uri.split("/")[-1]
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/event_types/{event_type_uuid}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data["resource"]

    async def get_availability(self, event_type_uri: str, start_time: str, end_time: str) -> List[Dict]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/event_type_available_times",
                headers=self.headers,
                params={
                    "event_type": event_type_uri,
                    "start_time": start_time,
                    "end_time": end_time
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("collection", [])
    
    async def create_booking(self, event_type_uri: str, start_time: str, invitee_email: str, invitee_name: str, invitee_notes: str = "", timezone: str = "Asia/Kolkata") -> Dict:
        event_type_details = await self.get_event_type_details(event_type_uri)
        locations = event_type_details.get("locations", [])
        
        location_payload = None
        if locations:
            first_location = locations[0]
            location_kind = first_location.get("kind", "ask_invitee")
            if location_kind == "physical":
                location_payload = {"kind": "physical", "location": first_location.get("location", "")}
            elif location_kind in ["zoom", "google_conference", "microsoft_teams_conference", "gotomeeting"]:
                location_payload = {"kind": location_kind}
            elif location_kind == "outbound_call":
                location_payload = {"kind": "outbound_call"}
            elif location_kind == "inbound_call":
                location_payload = {"kind": "inbound_call", "phone_number": "+1234567890"}
            else:
                location_payload = {"kind": "ask_invitee"}
        else:
            location_payload = {"kind": "ask_invitee"}
        
        payload = {
            "event_type": event_type_uri,
            "start_time": start_time,
            "invitee": {
                "email": invitee_email,
                "name": invitee_name,
                "timezone": timezone
            },
            "location": location_payload
        }
        
        if invitee_notes:
            payload["questions_and_answers"] = [
                {"question": "Reason for visit", "answer": invitee_notes, "position": 0}
            ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/invitees",
                    headers=self.headers,
                    json=payload
                )
                print(f"Calendly Request: {payload}")
                print(f"Calendly Response Status: {response.status_code}")
                print(f"Calendly Response: {response.text}")
                response.raise_for_status()
                data = response.json()
                invitee = data["resource"]
                return {
                    "uri": invitee.get("uri", ""),
                    "invitee_uuid": invitee.get("uri", "").split("/")[-1],
                    "email": invitee.get("email"),
                    "name": invitee.get("name"),
                    "status": invitee.get("status", "active"),
                    "cancel_url": invitee.get("cancel_url", ""),
                    "reschedule_url": invitee.get("reschedule_url", ""),
                    "event_uri": invitee.get("event", "")
                }
            except httpx.HTTPStatusError as e:
                print(f"Calendly API Error: {e.response.text}")
                raise
    
    async def get_scheduled_event(self, event_uuid: str) -> Dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/scheduled_events/{event_uuid}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data["resource"]
    
    async def cancel_invitee(self, invitee_uuid: str, scheduled_event_uuid: str) -> bool:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/scheduled_events/{scheduled_event_uuid}/invitees/{invitee_uuid}/cancellation",
                headers=self.headers,
                json={"reason": "Cancelled by patient"}
            )
            response.raise_for_status()
            return True
