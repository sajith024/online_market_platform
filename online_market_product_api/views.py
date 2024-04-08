from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from online_market_api.online_market_decorators import required_fields
from online_market_product.models import Product
from .serializers import ProductSerializer, ProductEditSerializer


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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductEditSerializer
        else:
            return ProductSerializer

    @required_fields()
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            data = {
                "status": HTTP_201_CREATED,
                "success": True,
                "message": "Product Created Successfully",
                "data": response.data,
            }
            response.data = data
        except ValidationError as error:
            data = {
                "status": HTTP_400_BAD_REQUEST,
                "success": False,
                "message": "Product Creation has Failed",
                "error": error.detail,
            }
            response = Response(data, status=error.status_code)

        return response
