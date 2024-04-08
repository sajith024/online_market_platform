import environ
from twilio.rest import Client as TwilioClient
from pyotp import TOTP, random_base32

from rest_framework.authentication import TokenAuthentication
from django.utils import timezone

from .models import OnlineMarketOTP

env = environ.Env()


class OnlineMarketTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class OnlineMarketTwilioOTPVerification:
    account_sid = env("TWILIO_ACCOUNT_SID")
    auth_token = env("TWILIO_AUTH_TOKEN")
    twilio_phone = env("TWILIO_PHONE")

    def __init__(self, user, phone_number, interval=300) -> None:
        self.client = TwilioClient(self.account_sid, self.auth_token)
        self.interval = interval
        otp = OnlineMarketOTP.objects.get_or_create(user=user)[0]
        otp.phone_number = phone_number
        otp.save()

        self.otp = otp

    def send_sms_code(self, format=None):
        totp = TOTP(self.otp.key, interval=self.interval)
        time = timezone.now()
        time_otp = totp.at(time)

        self.client.messages.create(
            body=format or "Your verification code is " + time_otp,
            from_=self.twilio_phone,
            to=self.otp.phone_number,
        )

        self.otp.created_at = time
        self.otp.save()

    def verify_phone(self, user_otp):
        if self.authenticate(self.otp.key, user_otp, self.otp.created_at):
            self.otp.is_verified = True
            self.otp.save()
            return True
        else:
            return False

    def authenticate(self, key, otp, time):
        totp = TOTP(key, interval=self.interval)
        return totp.verify(otp, time)

    def generate_key(self):
        return random_base32()
