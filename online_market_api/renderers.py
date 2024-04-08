from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_client_error, is_server_error


class OnlineMarketResponeRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]

        modified_data = {}
        modified_data["status"] = response.status_code
        modified_data["success"] = not self.is_error(response.status_code)

        if isinstance(data, dict):
            if data.get("message"):
                modified_data["message"] = data.pop("message")

            if data:
                if self.is_error(response.status_code):
                    modified_data["errors"] = data.get("errors") or data
                else:
                    modified_data["data"] = data.get("data") or data

            return super().render(modified_data, accepted_media_type, renderer_context)
        else:
            if self.is_error(response.status_code):
                modified_data["errors"] = data
            else:
                modified_data["data"] = data

            return super().render(modified_data, accepted_media_type, renderer_context)

    def is_error(self, status_code):
        return is_client_error(status_code) or is_server_error(status_code)
