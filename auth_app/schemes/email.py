from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class EmailPayloadScheme(BaseModel):
    message: str = Field(
        description='Message content',
        example='Test message example',
    )
    subject: str = Field(
        description='Message subject',
        example='Test subject example',
    )
    source: Optional[EmailStr] = Field(
        description='Email sender',
        example='sender@example.com',
        default='sender@example.com',
    )
