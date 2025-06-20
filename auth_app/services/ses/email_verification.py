from aiobotocore.client import AioBaseClient


async def verify_sender(
    ses: AioBaseClient,
) -> None:
    await ses.verify_email_identity(EmailAddress="sender@example.com")
    print("Sender verified.")
