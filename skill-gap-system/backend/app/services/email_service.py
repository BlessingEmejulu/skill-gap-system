import logging

logger = logging.getLogger(__name__)

# This is a mock email service. In production, connect to SendGrid, SES, or SMTP.
def send_reset_password_email(email: str, token: str):
    logger.info(f"Mock Email Service: Sending password reset token to {email}")
    logger.info(f"Mock Email Service: Reset Token: {token}")
    # In a real implementation, you would construct the email body with a link like:
    # reset_link = f"https://yourfrontend.com/reset-password?token={token}"
    # and send it via an email provider.
    pass
