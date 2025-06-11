from aiobotocore.client import AioBaseClient

from auth_app.services.aws.send_otp_email import generate_otp


async def reset_password(email_to: str, ses: AioBaseClient) -> str:
    """
    Generate and send a new password for the User
    """
    password = generate_otp(12)
    await ses.send_email(
        Destination={
            'ToAddresses': [email_to]
        },
        Message={
            'Body': {
                "Text": {
                    'Charset': 'UTF-8',
                    'Data': (
                        f'Your password was changed and sent to email: {email_to}'
                    )
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Test email',
            },
        },
        Source="sender@example.com",
    )
    print("---------------------------------")
    print(f"Password {password} was sent to {email_to}")
    print("---------------------------------")
    return password
