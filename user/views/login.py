import jwt
import json
import bcrypt
from django.conf import settings
from user.tags import USER, ADMIN
from datetime import datetime,timedelta
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from custom_lib.helper import extract_username
from custom_lib.api_view_class import CustomAPIView
from user.models import User, Admin, UserProjectAssignment


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
            raise Exception(12006) 

        userObjs = User.objects.filter(email__iexact=email)
        if not userObjs.exists():
            raise Exception(12016)
        password = password.encode('utf-8')
        
        userObj=userObjs.first()
        userBytes = userObj.password.encode('utf-8')
        result = bcrypt.checkpw(password, userBytes)
        if not result:
            raise Exception(12019)
        
        try:
            userObj.current_project
        except:
            userProjectObjs=UserProjectAssignment.objects.filter(user_id=userObj.pk)
            if not userProjectObjs.exists():
                raise Exception(12003)
            user=User.objects.get(id=userObj.pk)
            user.current_project=userProjectObjs.first().project
            user.save()

        userId=userObj.pk
        payload = {
                "exp" : datetime.utcnow() + timedelta(minutes=int(settings.JWT_EXPIRATION_IN_MINUTES)),
                "iat" : datetime.utcnow(),
                "userId": userObj.pk
                }
        jwtToken = jwt.encode(payload, 'ADITYA-SECRET', algorithm='HS256')
        return Response({"auth": jwtToken, "userId": userId, "userName": extract_username(email=email)})
        

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
            raise Exception(12006)
        
        suObj = Admin.objects.filter(email__iexact=email)
        if not suObj.exists():
            raise Exception(12016) 

        su=suObj.first()
        password = password.encode('utf-8')
        userBytes =su.password.encode('utf-8')
        result = bcrypt.checkpw(password,userBytes)
        if not result:
            raise Exception(12019)
        id=su.pk
        payload = {
                   "exp" : datetime.utcnow() + timedelta(minutes=int(settings.JWT_EXPIRATION_IN_MINUTES)),
                   "iat" : datetime.utcnow(),
                   "userId": su.pk
                   }
        jwtToken = jwt.encode(payload,'ADMIN-SECRET',algorithm='HS256')
        return Response({"auth":jwtToken, "userId":id})