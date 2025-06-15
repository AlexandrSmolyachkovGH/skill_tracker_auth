from aiobotocore.client import AioBaseClient

from auth_app.schemes.email import EmailPayload


def generate_email_payload(
    message: str,
    subject: str,
    source: str | None = None,
) -> EmailPayload:
    payload = {
        'message': message,
        'subject': subject,
    }
    if source:
        payload['source'] = source
    return EmailPayload(**payload)


async def send_email(
    email_to: str,
    ses: AioBaseClient,
    payload: EmailPayload,
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
