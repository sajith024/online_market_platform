from rest_framework.response import Response
from rest_framework import status


def required_fields(exclude=[]):
    def decorator(func):
        def wrapper(api_view, request, *args, **kwargs):
            required_fields = []
            for name, field in api_view.get_serializer().fields.items():
                if hasattr(field, "allow_blank"):
                    if not field.allow_blank:
                        required_fields.append(name)
                    else:
                        continue
                else:
                    required_fields.append(name)
            missing_fields = []
            for field in required_fields:
                if field not in exclude and field not in request.data:
                    missing_fields.append(field)

            if missing_fields:
                data = {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "error": {
                        "missing_fields": missing_fields,
                        "message": "Require Fields missing",
                    },
                }
                return Response(
                    data,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return func(api_view, request, *args, **kwargs)

        return wrapper

    return decorator
