import jwt
from django import db
from django.conf import settings
from user.models import User, Admin
from rest_framework import authentication


class BaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = None
        self._close_db_connections()
        
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            raise Exception(11014)

        userToken = auth_header[len("Bearer "):].strip()
        if userToken.startswith("b'") and userToken.endswith("'"):
            userToken = userToken[2:-1]

        userId = self._validate_token(userToken)
        user, projObj, = self._get_user_related_data(userId)
        request.session["basic_details"]={"user_id":user.pk, "project_id":projObj.pk}
        self._post_authentication(request, projObj, user)
        return "ok"

    def _post_authentication(self, request, projObj, user):
        request.project = projObj
        request.userid = user.pk
        request.login_user = user
        request.apikey = settings.OPENAI_API_KEY

    def _close_db_connections(self):
        db.connections.close_all()

    def _validate_token(self, token):
        try:
            data = jwt.decode(token, 'ADITYA-SECRET', algorithms=['HS256'])
            jwt_user_id = data.get("userId", "")
            if not jwt_user_id:
                raise Exception(11012)
            return jwt_user_id
        except:
            raise Exception(11001)

    def _get_user_related_data(self, userId):
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            raise Exception(11003)

        project = user.current_project
        if project==None:
            raise Exception(11003)
        return user, project

class PostLoginAuthentication(BaseAuthentication):
    pass

class PostUploadAuthentication(BaseAuthentication):
    def _post_authentication(self, request, projObj, userId):
        super()._post_authentication(request, projObj, userId)
        if projObj.namespace is None:
            raise Exception(11010)
        request.namespace = projObj.namespace

class AdminAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = None
        try:
            db.connections.close_all()
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                raise Exception(11014)

            userToken = auth_header[len("Bearer "):].strip()
            if userToken.startswith("b'") and userToken.endswith("'"):
                userToken = userToken[2:-1]
            try:
                data = jwt.decode(userToken, 'ADMIN-SECRET', algorithms=['HS256'])
                userId = data.get("userId", "")
                if not userId:
                    raise Exception(11012)
            except:
                raise Exception(11001)
            
            try:
                user = Admin.objects.get(id= userId)
            except Admin.DoesNotExist:
                raise Exception(11003)

            request.userid = user.id
            request.session["basic_details"]={"user_id":user.pk}
            return "ok"
        except Exception as e:
            raise Exception(str(e))