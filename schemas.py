"""Schemas for the chat app."""
from pydantic import BaseModel, validator
from typing import Any, Dict, List

class ChatResponse(BaseModel):
    """Chat response schema."""

    sender: str
    message: str
    type: str

    @validator("sender")
    def sender_must_be_bot_or_you(cls, v):
        if v not in ["bot", "you"]:
            raise ValueError("sender must be bot or you")
        return v

    @validator("type")
    def validate_message_type(cls, v):
        if v not in ["start", "stream", "end", "error", "info"]:
            raise ValueError("type must be start, stream or end")
        return v

# class StreamingLLMCallbackHandler:
#     """Callback handler for streaming LLM responses."""

#     def __init__(self):
#         self.messages = []

#     def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
#         self.messages.append({"sender": "bot", "message": token, "type": "stream"})


# class QuestionGenCallbackHandler:
#     """Callback handler for question generation."""

#     def __init__(self):
#         self.messages = []

#     def on_llm_start(
#         self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
#     ) -> None:
#         """Run when LLM starts running."""
#         self.messages.append(
#             {"sender": "bot", "message": "Synthesizing question...", "type": "info"}
#         )
