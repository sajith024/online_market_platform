from rest_framework.serializers import ModelSerializer

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
