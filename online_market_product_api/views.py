from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

import stripe
from stripe import error as strip_error
from decouple import config

from online_market_api.online_market_decorators import required_fields
from online_market_product.models import Product
from online_market_api.permissions import (
    IsSellerOrReadOnly,
    IsOwnerOrReadOnly,
    BuyerOnly,
)

from .models import CartItem, OrderManagement
from .serializers import (
    ProductSerializer,
    ProductAddSerializer,
    CartItemSerializer,
    CartItemAddSerializer,
    OrderManagementSerializer,
    OrderManagementAddSerializer
)


@extend_schema_view(
    create=extend_schema(
        responses={
            HTTP_201_CREATED: OpenApiResponse(
                response={
                    "status": HTTP_201_CREATED,
                    "success": True,
                    "message": "Product Created Successfully",
                    "data": [],
                },
                examples=[
                    OpenApiExample(
                        name="Example",
                        value={
                            "status": HTTP_201_CREATED,
                            "success": True,
                            "message": "Product Created Successfully",
                            "data": [],
                        },
                    )
                ],
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                {
                    "status": HTTP_400_BAD_REQUEST,
                    "success": False,
                    "message": "Product Creation has Failed",
                    "error": [],
                },
                examples=[
                    OpenApiExample(
                        name="Example",
                        value={
                            "status": HTTP_400_BAD_REQUEST,
                            "success": False,
                            "message": "Product Creation has Failed",
                            "error": [],
                        },
                    )
                ],
            ),
        },
    )
)
class ProductsViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsSellerOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductSerializer
        else:
            return ProductAddSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role.name == "Seller":
            return Product.objects.filter(user=user)
        else:
            return Product.objects.all()

    @required_fields()
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            data = {
                "message": "Product Created Successfully",
                "data": response.data,
            }
            response.data = data
        except ValidationError as error:
            data = {
                "message": "Product Creation has Failed",
                "error": error.detail,
            }
            response = Response(data, status=error.status_code)

        return response

    def perform_create(self, serializer):
        serializer.validated_data["user"] = self.request.user
        return super().perform_create(serializer)


class CartItemsViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    permission_classes = [IsAuthenticated, BuyerOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CartItemSerializer
        else:
            return CartItemAddSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user, is_purchased=False)

    @required_fields()
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            data = {
                "message": "Cart items added successfully",
                "data": response.data,
            }
            response.data = data
        except ValidationError as error:
            data = {
                "message": "Cart items addition failed",
                "error": error.detail,
            }
            response = Response(data, status=error.status_code)

        return response

    def perform_create(self, serializer):
        serializer.validated_data["user"] = self.request.user
        return super().perform_create(serializer)


class OrderManagementViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, BuyerOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderManagementSerializer
        else:
            return OrderManagementAddSerializer

    def get_queryset(self):
        return OrderManagement.objects.filter(user=self.request.user)

    @required_fields()
    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            response = super().create(request, *args, **kwargs)
            data = {
                "message": "Order created successfully",
                "data": response.data,
            }
            response.data = data
        except ValidationError as error:
            data = {
                "message": "Order creattion failed",
                "error": error.detail,
            }
            response = Response(data, status=error.status_code)

        return response

    def perform_create(self, serializer):
        serializer.validated_data["user"] = self.request.user
        return super().perform_create(serializer)


class OnlineMarketPayment(GenericViewSet):
    ENDPOINT_SECRET = config("ENDPOINT_SECRET")

    @action(detail=False, methods=["post"])
    def create_payment_intent(self, request):
        try:
            amount = request.data.get("amount")
            currency = "usd"
            intent = stripe.PaymentIntent.create(amount=amount, currency=currency)
            client_secret = intent.client_secret
            return Response({"client_secret": client_secret})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"])
    def handle_webhook(self, request):
        payload = request.data
        sig_header = request.headers.get("STRIPE_SIGNATURE")
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.ENDPOINT_SECRET
            )
        except ValueError as e:
            return Response("Invalid payload", HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response("Invalid signature", HTTP_400_BAD_REQUEST)

        if event and event["type"] == "payment_intent.succeeded":
            print("Success")
        else:
            print("Failed")

        return Response(status=HTTP_200_OK)
