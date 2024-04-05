from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes

from online_market_app.models import OnlineMarketUser, Role
from .serializers import RegistrationUserSerializer, RoleSerializer
from .online_market_decorators import required_fields
from online_market_api.authentication import OnlineMarketTwilioOTPVerification
from online_market_api.models import OnlineMaketOTP


@extend_schema_view()
class RegistrationUserView(CreateAPIView):

    queryset = OnlineMarketUser.objects.all()
    serializer_class = RegistrationUserSerializer

    @required_fields()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)

            token = Token.objects.get_or_create(user=serializer.instance)
            data = {
                "status": HTTP_201_CREATED,
                "success": True,
                "message": "Registration successfull",
                "token": str(token[0]),
            }
            return Response(data, status=HTTP_201_CREATED)
        else:
            data = {
                "status": HTTP_400_BAD_REQUEST,
                "success": False,
                "errors": serializer.errors,
                "message": "Registration failed",
            }
            return Response(data, status=HTTP_400_BAD_REQUEST)


@extend_schema_view()
class RolesViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


@api_view(["POST"])
def send_sms_code(request, format=None):
    pk = request.data.get("user_id")
    phone_number = request.data.get("phone_number")
    if phone_number and pk:
        user = get_object_or_404(OnlineMarketUser, pk=pk)
        verify_phone = OnlineMarketTwilioOTPVerification()
        verify_phone.send_sms_code(phone_number=phone_number)
        verify_otp = OnlineMaketOTP.objects.get_or_create(
            user=user,
            phone_number=phone_number,
        )
        
        
        verify_otp[0].key=verify_phone.user_key
        verify_otp[0].save()
        return Response(
            data={
                "status": HTTP_200_OK,
                "success": True,
                "message": "OTP Verification Sended",
            },
            status=HTTP_200_OK,
        )
    else:
        return Response(
            data={
                "status": HTTP_400_BAD_REQUEST,
                "success": False,
                "message": "Error",
            },
            status=HTTP_200_OK,
        )


@api_view(["POST"])
def verify_phone(request):
    pk = request.data.get("user_id")
    otp_code = request.data.get("otp")
    if pk:
        verify_phone = OnlineMarketTwilioOTPVerification()
        user = get_object_or_404(OnlineMarketUser, pk=pk)
        otp = get_object_or_404(OnlineMaketOTP, user=user)

        if verify_phone.verify_phone(key=otp.key, otp=otp_code):
            otp.is_verified = True
            otp.save()
            return Response(
                {
                    "status": HTTP_201_CREATED,
                    "success": True,
                    "message": "Phone number verified successfully",
                },
                status=HTTP_201_CREATED,
            )
        return Response(
            data={
                "status": HTTP_400_BAD_REQUEST,
                "success": False,
                "message": "The provided code did not match or has expired",
            },
            status=HTTP_400_BAD_REQUEST,
        )
