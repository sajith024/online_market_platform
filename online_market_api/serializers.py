from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import CharField, PrimaryKeyRelatedField

from online_market_app.models import OnlineMarketUser, Role


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class RegistrationUserSerializer(ModelSerializer):
    class Meta:
        model = OnlineMarketUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
        )

    def create(self, validated_data):
        user = OnlineMarketUser.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        return user


class LoginUserSerializer(Serializer):
    username = CharField()
    password = CharField()


class SMSVerificationSerializer(Serializer):
    user = PrimaryKeyRelatedField(queryset=OnlineMarketUser.objects.all())
    phone_number = CharField(max_length=15)


class OTPVerificationSerializer(SMSVerificationSerializer):
    otp = CharField(max_length=6)
