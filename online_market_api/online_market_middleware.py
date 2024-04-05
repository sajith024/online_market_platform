import logging

from .models import OnlineMarketLogs


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OnlineMarketLogMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        logger.info(f"Incoming request: {request.method} {request.path}")
        response = self.get_response(request)
        logger.info(f"Outgoing response: {response.status_code}")

        if hasattr(response, "data"):
            OnlineMarketLogs.objects.create(
                request_method=request.method,
                request_path=request.path,
                request_status=response.status_code,
                response=response.data,
            )
        return response
