from rest_framework import status
from rest_framework.response import Response

class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if isinstance(response, Response) and response.status_code == status.HTTP_403_FORBIDDEN:
            response.status_code = status.HTTP_200_OK 

        return response
