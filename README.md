# Medical Appointment Scheduling Agent

Production-grade AI-powered medical appointment scheduling system using AWS Bedrock Claude 3.5 Sonnet, LangChain, and Calendly API.

## Features

- **Intelligent Scheduling**: Book, reschedule, and cancel appointments via natural conversation
- **Multi-Tool Agent**: LangChain agent with 5 specialized tools
- **RAG-Powered FAQ**: Answer clinic questions using ChromaDB vector store
- **Real Calendly Integration**: Direct API integration for appointment management
- **Conversation Memory**: Session-based memory for context retention
- **4 Appointment Types**: General Consultation, Follow-up, Physical Exam, Specialist Consultation

## Architecture

- **Backend**: FastAPI with async/await
- **LLM**: AWS Bedrock Claude 3.5 Sonnet via LangChain ChatBedrock
- **Agent**: LangChain create_tool_calling_agent with AgentExecutor
- **Vector DB**: ChromaDB with BedrockEmbeddings
- **Calendar**: Calendly API with httpx

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- CALENDLY_API_KEY
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION

3. Initialize vector store (optional):
```python
from backend.rag.vector_store import initialize_vector_store
initialize_vector_store()
```

4. Run the server:
```bash
python -m uvicorn backend.main:app --reload
```

## API Usage

**Endpoint**: POST /api/chat

**Request**:
```json
{
  "message": "I need to book an appointment for next Monday",
  "session_id": "user-123"
}
```

**Response**:
```json
{
  "response": "I'd be happy to help you book an appointment...",
  "booking_details": {
    "booking_uuid": "abc123",
    "patient_name": "John Doe",
    "patient_email": "john@example.com",
    "slot_time": "2024-01-15 10:00 AM"
  },
  "action_performed": "booking"
}
```

## Agent Capabilities

1. **Check Availability**: Fetch available slots by date and appointment type
2. **Book Appointments**: Create new appointments with patient details
3. **Reschedule**: Atomic reschedule (check availability → cancel → book)
4. **Cancel**: Cancel with confirmation and optional reason
5. **Answer FAQs**: RAG-based clinic information retrieval

## Project Structure

```
lyzr/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── api/
│   │   ├── chat.py               # Chat endpoint
│   │   └── calendly_integration.py  # Calendly service
│   ├── agent/
│   │   ├── scheduling_agent.py   # LangChain agent
│   │   └── prompts.py            # Agent prompts
│   ├── tools/
│   │   ├── availability_tool.py  # Check slots
│   │   ├── booking_tool.py       # Book appointments
│   │   ├── reschedule_tool.py    # Reschedule logic
│   │   ├── cancel_tool.py        # Cancel appointments
│   │   └── faq_tool.py           # FAQ search
│   ├── rag/
│   │   ├── faq_rag.py            # RAG chain
│   │   ├── embeddings.py         # Bedrock embeddings
│   │   └── vector_store.py       # ChromaDB
│   └── models/
│       └── schemas.py            # Pydantic models
├── data/
│   ├── clinic_info.json          # FAQ data
│   └── vectordb/                 # Chroma persistence
├── requirements.txt
└── .env.example
```

## Conversation Flow Examples

**Booking**:
- User: "I need a general consultation next week"
- Agent: Shows available slots
- User: "Book me for Monday at 2pm"
- Agent: Collects name/email and confirms booking

**Rescheduling**:
- User: "I need to reschedule my appointment"
- Agent: Asks for booking UUID
- User: Provides UUID and new preferred time
- Agent: Shows availability, confirms, executes reschedule

**Cancellation**:
- User: "Cancel my appointment"
- Agent: "Are you sure you want to cancel?"
- User: "Yes"
- Agent: Cancels and offers to book new appointment

## Error Handling

- Invalid booking UUIDs
- Unavailable time slots during reschedule
- Calendly API failures
- AWS Bedrock rate limits
- Race conditions on slot booking
