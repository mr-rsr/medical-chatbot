from langchain_aws import ChatBedrock
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from backend.agent.prompts import get_agent_prompt
from backend.tools.availability_tool import get_availability_tool
from backend.tools.booking_tool import book_appointment_tool
from backend.tools.reschedule_tool import reschedule_appointment_tool
from backend.tools.cancel_tool import cancel_appointment_tool
from backend.tools.faq_tool import search_faq_tool
import os
import json
import re
import boto3
from botocore.config import Config

class SchedulingAgent:
    def __init__(self):
        retry_config = Config(
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )
        
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            config=retry_config
        )
        
        self.llm = ChatBedrock(
            client=bedrock_client,
            model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            model_kwargs={"temperature": 0.7, "max_tokens": 2000},
            streaming=False
        )
        
        self.tools = [
            get_availability_tool,
            book_appointment_tool,
            reschedule_appointment_tool,
            cancel_appointment_tool,
            search_faq_tool
        ]
        
        self.prompt = get_agent_prompt()
        
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.sessions = {}
    
    def get_memory(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "memory": ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                ),
                "booking_data": {}
            }
        return self.sessions[session_id]["memory"]
    
    def get_booking_data(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "memory": ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                ),
                "booking_data": {}
            }
        return self.sessions[session_id]["booking_data"]
    
    def update_booking_data(self, session_id: str, data: dict):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "memory": ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                ),
                "booking_data": {}
            }
        self.sessions[session_id]["booking_data"].update(data)
    
    def clear_booking_data(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["booking_data"] = {}

    async def process_message(self, message: str, session_id: str):
        memory = self.get_memory(session_id)
        
        agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        result = await agent_executor.ainvoke({"input": message})
        
        output = result.get("output", "")
        if isinstance(output, list):
            response_text = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in output])
        else:
            response_text = str(output)
        
        booking_details = None
        action_performed = None
        
        if "BOOKING_DATA:" in response_text:
            match = re.search(r'BOOKING_DATA: ({.*?})', response_text)
            if match:
                try:
                    booking_details = json.loads(match.group(1))
                    self.update_booking_data(session_id, booking_details)
                    action_performed = "booking"
                    response_text = response_text.replace(f"BOOKING_DATA: {match.group(1)}", "").strip()
                except:
                    pass
        
        if "CANCELLED_BOOKING:" in response_text:
            match = re.search(r'CANCELLED_BOOKING: (\S+)', response_text)
            if match:
                self.clear_booking_data(session_id)
                action_performed = "cancellation"
                response_text = response_text.replace(f"CANCELLED_BOOKING: {match.group(1)}", "").strip()
        
        return {
            "response": response_text.strip(),
            "booking_details": booking_details,
            "action_performed": action_performed
        }

agent_instance = SchedulingAgent()
