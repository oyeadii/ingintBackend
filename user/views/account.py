import bcrypt
from user.tags import ADMIN
from django.db.models import Q
from django.db.models import Count
from django_filters.views import FilterView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from custom_lib.api_view_class import AdminAPIView
from user.helper import CustomPagination,UserFilter
from user.models import User,Project,UserProjectAssignment
from custom_lib.helper import admin_post_login,check_email,valid_serializer
from user.serializers import AdminSignUpSerializer,SignUpSerializer,UpdateUserSerializer,DeleteUserSerializer


def handle_user_assignment(request_data, serializer, project_object, is_admin):
    # Step 1: Validate Serializer
    data = valid_serializer(serializer(data=request_data), error_code=12006)
    email = data["email"]

    # Step 2: Check Email
    if not check_email(email):
        raise Exception(12038)

    # Step 3: Fetch or Try to Fetch User
    try:
        userObj = User.objects.get(email__iexact=email)
        try:
            UserProjectAssignment.objects.get(user_id=userObj.id, project=project_object)
            raise Exception(12056)
        except UserProjectAssignment.DoesNotExist:
            userProject = UserProjectAssignment(user_id=userObj.user_id, project=project_object, is_admin=is_admin)
            userProject.save()
    except User.DoesNotExist:
        try:
            userObj = User.objects.get(email__iexact=email)
            raise Exception(12050)
        except User.DoesNotExist:
            pass

        # Step 4: Handle Case Where User Does Not Exist
        # password=generate_password()
        password = "Ingint123"
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)
        hash_password = hash.decode('utf-8')
        user = User(email=email, password=hash_password)
        user.save()
        userProject = UserProjectAssignment(project=project_object, user_id=user.id, is_admin=is_admin)
        userProject.save()
    return

    

class AdminCreateUserView(AdminAPIView, FilterView):
    filterset_class = UserFilter
    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login
    )
    def get(self, request): 
        filterset = self.filterset_class(request.GET, queryset=User.objects.all())
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        
        userList = filterset.qs.values('id', 'email')
        userList = userList.annotate(num_projects=Count('userprojectassignment__project', distinct=True))
        userList = userList.annotate(num_admins=Count('userprojectassignment', distinct=True, filter=Q(userprojectassignment__is_admin=1)))
        
        paginator = CustomPagination()
        page = paginator.paginate_queryset(userList, request)
        if page is not None and len(page) > 0:
            return paginator.get_paginated_response({"user_list": page})

        return Response({"user_list": []})
    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login,
        request_body=AdminSignUpSerializer
    )
    def post(self, request):
        data = valid_serializer(AdminSignUpSerializer(data=request.data), error_code=12006)
        email, project_name = data["email"], data["project"]
        is_admin, is_existing = data["is_admin"], data["is_existing"]

        project = Project.objects.filter(project_name__iexact=project_name).first()
        if is_existing:
            if not project:
                raise Exception(12045)
        else:
            if project:
                raise Exception(12039)

            project = Project(project_name=project_name)
            project.save()

        handle_user_assignment(request.data, AdminSignUpSerializer, project, is_admin)
        return Response("success")

    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters= admin_post_login,
        request_body=UpdateUserSerializer
    )
    def put(self,request):
        data = valid_serializer(UpdateUserSerializer(data=request.data), error_code=12004)
        update_user_id = data["update_user_id"]
        to_update = data["to_update"]

        if to_update.get("password",""):
            raise Exception(12005)
        email=to_update.get("email", "")
        if email:
            if not check_email(email):
                raise Exception(12038)
            userObj=User.objects.filter(email__iexact=email)
            if userObj.exists():
                raise Exception(12050)

        user = User.objects.filter(id=update_user_id).update(**to_update)
        return Response({"id":update_user_id, "updated_data":to_update})
    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters= admin_post_login,
        request_body=DeleteUserSerializer
    )
    def delete(self,request):
        data = valid_serializer(DeleteUserSerializer(data=request.data), error_code=12012)
        userObj=UserProjectAssignment.objects.filter(user_id=data["delete_user_id"])
        userObj.delete()
        try:
            user=User.objects.get(id=data["delete_user_id"])
            user.delete()
        except User.DoesNotExist:
            raise Exception(12007)
        return Response({"id":data["delete_user_id"]})
    

class CreateNewUserView(AdminAPIView):
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login,
        request_body=SignUpSerializer
    )
    def post(self, request):
        data = valid_serializer(SignUpSerializer(data=request.data), error_code=12006)
        email = data["email"]

        if not check_email(email):
            raise Exception(12038)

        try:
            userObj = User.objects.get(email__iexact=email)
            raise Exception(12050)
        except User.DoesNotExist:
            pass

        # password=generate_password()
        password="Ingint123"
        bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)
        password = hash.decode('utf-8')

        user = User(password=password,email=email)
        user.save()
        return Response("User Created Successfully")