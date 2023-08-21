from pydantic import BaseModel, Field


class InputRequest(BaseModel):
    """
    input Request object
    """
    question: str = Field(None)
    session_id: str = Field(None,alias="sessionId")
    

