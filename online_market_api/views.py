import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from online_market_app.models import OnlineMarketUser, Role
from online_market_api.models import OnlineMarketOTP
from .serializers import (
    RegistrationUserSerializer,
    LoginUserSerializer,
    SMSVerificationSerializer,
    OTPVerificationSerializer,
    RoleSerializer,
)
from .online_market_decorators import required_fields
from online_market_api.authentication import OnlineMarketTwilioOTPVerification


logger = logging.getLogger(__name__)


@extend_schema_view()
class RegistrationUserView(CreateAPIView):
    queryset = OnlineMarketUser.objects.all()
    serializer_class = RegistrationUserSerializer

    @required_fields()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)

            token = RefreshToken.for_user(user=serializer.instance)
            otp = OnlineMarketOTP.objects.get_or_create(user=serializer.instance)[0]
            data = {
                "data": {
                    "id": serializer.instance.id,
                    "username": serializer.instance.username,
                    "is_verified": otp.is_verified,
                    "token": {
                        "refresh": str(token),
                        "access": str(token.access_token),
                    },
                },
                "message": "Registration successful",
            }
            return Response(data, status=HTTP_201_CREATED)
        else:
            return Response(
                {"errors": serializer.errors, "message": "Registration failed"},
                status=HTTP_400_BAD_REQUEST,
            )


@extend_schema_view()
class LoginUserView(CreateAPIView):
    serializer_class = LoginUserSerializer

    @required_fields()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                # otp = OnlineMarketOTP.objects.get(user=user)
                # if otp.is_verified:
                #     token = Token.objects.get_or_create(user=user)
                #     data = {
                #         "status": HTTP_200_OK,
                #         "success": True,
                #         "message": "Login successful",
                #         "data": {
                #             "id": user.id,
                #             "username": user.username,
                #             "is_verified": otp.is_verified,
                #             "token": str(token[0]),
                #         },
                #     }
                #     return Response(data, status=HTTP_200_OK)
                # else:
                #     data = {
                #         "status": HTTP_401_UNAUTHORIZED,
                #         "success": False,
                #         "message": "Verification Required",
                #         "data": {
                #             "id": user.id,
                #             "username": user.username,
                #             "is_verified": otp.is_verified,
                #         },
                #     }
                #     return Response(data, status=HTTP_401_UNAUTHORIZED)
                token = RefreshToken.for_user(user)
                data = {
                    "message": "Login successful",
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "role": user.role.id,
                        "token": {
                            "refresh": str(token),
                            "access": str(token.access_token),
                        },
                    },
                }
                logger.info(f"Login successful for {user.get_username()}")
                return Response(data, status=HTTP_200_OK)
            else:
                logger.warning( "Unauthorized Login.")
                return Response(data=serializer.errors, status=HTTP_401_UNAUTHORIZED)
        else:
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema_view()
class LogoutUserView(TokenBlacklistView):
    pass


@extend_schema_view()
class SMSVerificationView(CreateAPIView):
    serializer_class = SMSVerificationSerializer

    @required_fields()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            verification = OnlineMarketTwilioOTPVerification(
                serializer.validated_data["user"],
                serializer.validated_data["phone_number"],
            )
            verification.send_sms_code()
            return Response({"message": "OTP Verification Sended"}, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema_view()
class OTPVerificationView(CreateAPIView):
    serializer_class = OTPVerificationSerializer

    @required_fields()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            verification = OnlineMarketTwilioOTPVerification(
                user,
                serializer.validated_data["phone_number"],
            )

            if verification.verify_phone(serializer.validated_data["otp"]):
                return Response(
                    {"message": "OTP verified successfully"}, status=HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "The provided code did not match or has expired"},
                    status=HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema_view()
class RolesViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
