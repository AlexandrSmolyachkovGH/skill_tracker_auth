from aiobotocore.client import AioBaseClient

from auth_app.schemes.email import EmailPayloadScheme


def generate_email_payload(
    message: str,
    subject: str,
    source: str | None = None,
) -> EmailPayloadScheme:
    payload = {
        'message': message,
        'subject': subject,
    }
    if source:
        payload['source'] = source
    return EmailPayloadScheme(**payload)


async def send_email(
    email_to: str,
    ses: AioBaseClient,
    payload: EmailPayloadScheme,
) -> None:
    """
    Basic email sending
    """
    await ses.send_email(
        Destination={'ToAddresses': [email_to]},
        Message={
            'Body': {
                "Text": {
                    'Charset': 'UTF-8',
                    'Data': payload.message,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': payload.subject,
            },
        },
        Source=payload.source,
    )
