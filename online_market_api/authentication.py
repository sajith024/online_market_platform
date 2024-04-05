import environ
from twilio.rest import Client as TwilioClient
from pyotp import TOTP, random_base32

from rest_framework.authentication import TokenAuthentication

from .models import OnlineMaketOTP

env = environ.Env()


# keyword = "Bearer"
class OnlineMarketTokenAuthentication(TokenAuthentication):
    pass


class OnlineMarketTwilioOTPVerification:
    account_sid = env("TWILIO_ACCOUNT_SID")
    auth_token = env("TWILIO_AUTH_TOKEN")
    twilio_phone = env("TWILIO_PHONE")

    def __init__(self) -> None:
        self.client = TwilioClient(self.account_sid, self.auth_token)
        self.user_key = self.generate_key()

    def send_sms_code(self, phone_number, interval=300, format=None):
        time_otp = TOTP(self.user_key, interval=interval)
        time_otp = time_otp.now()
        self.client.messages.create(
            body=format or "Your verification code is " + time_otp,
            from_=self.twilio_phone,
            to=phone_number,
        )

    def verify_phone(self, key, otp, interval=300):
        return self.authenticate(otp, key, interval)

    def authenticate(self, key, otp, interval):
        provided_otp = 0
        try:
            provided_otp = int(otp)
        except:
            return False
        totp = TOTP(key, interval=interval)
        return totp.verify(provided_otp)

    def generate_key(self):
        key = random_base32()
        if self.is_unique(key):
            return key
        self.generate_key()

    def is_unique(self, key):
        try:
            OnlineMaketOTP.objects.get(key=key)
        except OnlineMaketOTP.DoesNotExist:
            return True
        return False
