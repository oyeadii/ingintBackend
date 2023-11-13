from rest_framework.views import APIView
from custom_lib.custom_mixin import LoggingMixin
from custom_lib.renderer import JSONResponseRenderer
from custom_lib.authentication import PostLoginAuthentication,PostUploadAuthentication,AdminAuthentication


class CustomAPIView(JSONResponseRenderer, LoggingMixin, APIView):
    permission_classes=()
    authentication_classes=[]

class PostLoginAPIView(JSONResponseRenderer, LoggingMixin, APIView):
    permission_classes=()
    authentication_classes=[PostLoginAuthentication]

class PostUploadAPIView(JSONResponseRenderer, LoggingMixin, APIView):
    permission_classes=()
    authentication_classes=[PostUploadAuthentication]

class AdminAPIView(JSONResponseRenderer, LoggingMixin, APIView):
    permission_classes=()
    authentication_classes=[AdminAuthentication]