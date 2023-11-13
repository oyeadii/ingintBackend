import jwt
import json
import bcrypt
from django.conf import settings
from user.tags import USER, ADMIN
from user.models import User, Admin
from datetime import datetime,timedelta
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from custom_lib.api_view_class import CustomAPIView


class LoginView(CustomAPIView):
    @swagger_auto_schema(
        tags=[USER],
    )
    def post(self, request):
        request_data = request.body.decode('utf-8')
        data = json.loads(request_data)
        email = data.get("email","")
        password = data.get("password","")
        
        if not email or not password:
            raise Exception(13009)

        userObjs = User.objects.filter(email__iexact=email)
        if not userObjs.exists():
            raise Exception(13019)
        password = password.encode('utf-8')
        
        userObj=userObjs.first()
        userBytes = userObj.password.encode('utf-8')
        result = bcrypt.checkpw(password, userBytes)
        if not result:
            raise Exception(13011)

        userId=userObj.pk
        payload = {
                "exp" : datetime.utcnow() + timedelta(minutes=int(settings.JWT_EXPIRATION_IN_MINUTES)),
                "iat" : datetime.utcnow(),
                "userId": userObj.pk
                }
        jwtToken = jwt.encode(payload, 'ADITYA-SECRET', algorithm='HS256')
        return Response({"auth": jwtToken, "userId": userId})
        

class AdminLoginView(CustomAPIView):
    @swagger_auto_schema(
        tags=[ADMIN],
    )
    def post(self, request):
        request_data = request.body.decode('utf-8')
        data = json.loads(request_data)
        email = data.get("email","")
        password = data.get("password","")
        
        if not email or not password:
            raise Exception(13012)
        
        suObj = Admin.objects.filter(email__iexact=email)
        if not suObj.exists():
            raise Exception(13010) 

        su=suObj.first()
        password = password.encode('utf-8')
        userBytes =su.password.encode('utf-8')
        result = bcrypt.checkpw(password,userBytes)
        if not result:
            raise Exception(13011)
        id=su.pk
        payload = {
                   "exp" : datetime.utcnow() + timedelta(minutes=int(settings.JWT_EXPIRATION_IN_MINUTES)),
                   "iat" : datetime.utcnow(),
                   "userId": su.pk
                   }
        jwtToken = jwt.encode(payload,'ADMIN-SECRET',algorithm='HS256')
        return Response({"auth":jwtToken, "userId":id})