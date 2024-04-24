from logging import getLogger

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
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

import stripe
from stripe import error as strip_error
from decouple import config

from online_market_api.online_market_decorators import required_fields
from online_market_app.models import OnlineMarketStripeCustomer
from online_market_product.models import Product
from online_market_api.permissions import (
    IsSellerOrReadOnly,
    IsOwnerOrReadOnly,
    BuyerOnly,
)

from .models import CartItem, OrderManagement, Cart
from .serializers import (
    ProductSerializer,
    ProductAddSerializer,
    CartSerializer,
    CartAddSerializer,
    CartItemSerializer,
    CartItemAddSerializer,
    OrderManagementSerializer,
    OrderManagementAddSerializer,
)


logger = getLogger(__name__)


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


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartAddSerializer
    permission_classes = [IsAuthenticated, BuyerOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CartSerializer

        return self.serializer_class

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, order__isnull=True)

    @required_fields()
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            data = {
                "message": "Cart added successfully",
                "data": response.data,
            }
            response.data = data
        except ValidationError as error:
            data = {
                "message": "Cart addition failed",
                "error": error.detail,
            }
            response = Response(data, status=error.status_code)

        return response


class CartItemsViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemAddSerializer
    permission_classes = [IsAuthenticated, BuyerOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CartItemSerializer

        return self.serializer_class

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user,
            cart__order__isnull=True,
        )

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


class OnlineMarketPaymentViewSet(GenericViewSet):
    STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
    STRIPE_API_KEY = config("STRIPE_SECRET_KEY")

    @action(detail=False, methods=["GET"])
    def stripe_config(self, request):
        return Response(
            {"publishableKey": config("STRIPE_PUBLISHABLE_KEY")}, status=HTTP_200_OK
        )

    @action(detail=False, methods=["POST"])
    def create_payment(self, request):
        try:
            order_id = request.data.get("order_id")
            try:
                order = OrderManagement.objects.get(id=order_id)
            except OrderManagement.DoesNotExist:
                return Response(
                    {"errors": "Order not found"}, status=HTTP_400_BAD_REQUEST
                )

            if order.payment_status == "processing":
                return Response(
                    {"errors": "Order in processing fee."}, status=HTTP_400_BAD_REQUEST
                )
            elif order.payment_status == "paid":
                return Response({"errors": "Order paid"}, status=HTTP_400_BAD_REQUEST)

            order.payment_status = "processing"
            order.save()
            try:
                stripe_customer = OnlineMarketStripeCustomer.objects.get(
                    user=order.user
                )
            except OnlineMarketStripeCustomer.DoesNotExist:
                customer = stripe.Customer.create(
                    name=order.user.get_full_name(),
                    email=order.user.email,
                    address={
                        "line1": "Thiruvananthapuram",
                        "city": "Thiruvananthapuram",
                        "country": "IN",
                        "state": "Kerala",
                        "postal_code": "605036",
                    },
                    api_key=self.STRIPE_API_KEY,
                )

                stripe_customer = OnlineMarketStripeCustomer.objects.create(
                    user=order.user, client_id=customer.id
                )

            logger.debug(f"customer id: {stripe_customer.client_id}")

            checkout_session = stripe.checkout.Session.create(
                customer=stripe_customer.client_id,
                line_items=[
                    {
                        "price_data": {
                            "currency": "INR",
                            "unit_amount_decimal": int(order.total_price * 100),
                            "product_data": {
                                "name": "name of the product",
                            },
                        },
                        "quantity": 1,
                    },
                ],
                payment_intent_data={
                    "metadata": {
                        "order_id": order.id,
                    }
                },
                allow_promotion_codes=True,
                mode="payment",
                success_url="http://127.0.0.1:8000/payments/success/",
                cancel_url="http://127.0.0.1:8000/payments/cancel/",
                api_key=self.STRIPE_API_KEY,
            )

            logger.debug(f"sesssion {checkout_session}")

            return Response(
                {"session_url": checkout_session.url}, status=HTTP_201_CREATED
            )
        except strip_error.StripeError as e:
            return Response({"errors": str(e)}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"errors": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["POST"])
    def handle_webhook(self, request):
        raw_payload = request.body
        sig_header = request.headers.get("Stripe-Signature")
        event = None
        try:
            event = stripe.Webhook.construct_event(
                raw_payload, sig_header, self.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            print("value:", e)
            return Response("Invalid payload", HTTP_400_BAD_REQUEST)
        except strip_error.SignatureVerificationError as e:
            print("stripe", e)
            return Response("Invalid signature", HTTP_400_BAD_REQUEST)

        session_intent = event.data.object
        logger.debug(f"Invalid payment_intent {session_intent}")
        metadata = session_intent.get("metadata")
        try:
            order_id = metadata.get("order_id")
            order = OrderManagement.objects.get(id=int(order_id))
        except Exception:
            order = None
            logger.debug(f"Invalid order {order_id}")

        if event and order and order.payment_status != "paid":
            if event["type"] == "payment_intent.succeeded":
                order.payment_status = "paid"
            elif event["type"] == "payment_intent.payment_failed":
                order.payment_status = "failed"
                logger.debug(f"Failed {event['type']}")
            else:
                order.payment_status = "processing"
            order.save()

        return Response(status=HTTP_200_OK)
