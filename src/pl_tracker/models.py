from pydantic import BaseModel


class SessionMetadata(BaseModel):
    program: str
    week: int
    day: int
    exercise: str
