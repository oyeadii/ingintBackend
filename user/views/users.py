from user.tags import ADMIN
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db.models.functions import Coalesce
from custom_lib.api_view_class import AdminAPIView
from user.models import User, Project, UserProjectAssignment
from custom_lib.helper import valid_serializer, admin_post_login, check_email
from user.helper import CustomPagination, UserFilter, handle_user_assignment_v2
from django.db.models import F, Value,Count, Q, OuterRef, IntegerField, Subquery
from user.serializers import UserDataSerializer, EditUserSerializer, RemoveUserSerializer, AddUserSerializer


class UsersDetailsView(AdminAPIView):
    filterset_class = UserFilter

    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login,
        query_serializer=UserDataSerializer
    )
    def get(self, request):
        user_type = request.GET.get("type")
        details = bool(eval(request.GET.get("details").capitalize()))
        project_id = int(request.GET.get("project_id", 0))
        column = request.GET.get("column", None)
        sort_order = request.GET.get("order_by", None)
        user = request.GET.get("user", None)
        if user and len(user) < 2:
            raise Exception("Provide two or more characters for this filter", 12041)
        filterset = self.filterset_class(request.GET, queryset=User.objects.filter(active=True).all())
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)

        userList = filterset.qs.values('id', 'email', 'username', 'is_sa', 'first_name', 'last_name')
        if column:
            if sort_order == "desc":
                column = "-" + column
            userList = userList.order_by(column)

        # Check if the user's user_type is 'admin' and if their details are true,
        # then retrieve the project count and the count of projects for which the user is an admin.
        if user_type == "admin" and details:
            userList = userList.annotate(num_projects=Count('userprojectassignment__project', distinct=True))
            userList = userList.annotate(num_admins=Count('userprojectassignment', distinct=True, filter=Q(userprojectassignment__is_admin=1)))

        # Check if the project_id is obtained from the payload,
        # fetch the project's user, and list of users without the project user.
        if project_id:
            subquery = UserProjectAssignment.objects.filter(
                user_id=OuterRef('id')
            ).filter(project_id=project_id).values('project_id')
            userList = userList.annotate(right_value=F('id')).annotate(
                right_value=Coalesce(Subquery(subquery, output_field=IntegerField()), Value(None, output_field=IntegerField()))
            )
            userList = userList.annotate(is_admin=F("userprojectassignment__is_admin"))
            userList = userList.annotate(project_id_usa=F("userprojectassignment__project_id"))

        userList = userList.filter(tenant_id=request.tenant_id)
        project_user = []

        # Check if the page in params displays the data pagination; if not, all items on a single page.
        if int(request.query_params.get('page')):
            paginator = CustomPagination()
            page = paginator.paginate_queryset(userList, request)
            if page is not None and len(page) > 0:
                return paginator.get_paginated_response({"user_list": page})
        else:
            if project_id:
                project_user = list(userList.filter(project_id_usa=project_id).values("id", "email", "is_admin"))
                remain_user_query = list(userList.filter(Q(project_id_usa__isnull=True) | ~Q(project_id_usa=project_id)).values("id", "email"))
                temp_user_id = [item['id'] for item in project_user]
                remain_user = []
                for data in remain_user_query:
                    if data.get("id") not in temp_user_id:
                        remain_user.append(data)
                remain_user = sorted(remain_user, key=lambda x: x['email'])
                project_user = sorted(project_user, key=lambda x: x['email'])
                userList = remain_user

            return Response({"results": {"user_list": list(userList), "project_user": project_user},
                             "count": len(userList) + len(project_user)})
        
        return Response({"results": {"user_list": []}})


    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login,
        request_body = AddUserSerializer
    )
    def post(self, request):
        data = valid_serializer(AddUserSerializer(data=request.data), error_code=12006)
        emails = data["user_data"]
        invalid_user = []
        for user in emails:
            find_user =User.objects.filter(email__iexact=user["email"])
            if find_user:
                invalid_user.append(user["email"])
                continue
            if project:=user.get('project_id'):
                project = (Project.objects.filter(
                    id=user['project_id'],
                    active=True
                ).first())
                if project:
                    handle_user_assignment_v2([user], project, request)
                else:
                    invalid_user.append(user["email"])
            else:
                handle_user_assignment_v2([user], project, request)
        message = "success"
        if invalid_user:
            message = "Following Users are unable create "+",".join(invalid_user)
            raise Exception(message, 14010)
        return Response(message)

    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters= admin_post_login,
        request_body=EditUserSerializer
    )
    def put(self,request):
        data = valid_serializer(EditUserSerializer(data=request.data), error_code=13005)
        update_user_id = int(data["user_id"])
        to_update = data["to_update"]

        # Check if the given user is already present in the Users table; if not, raise an exception.
        try:
            User.objects.get(id=update_user_id)
        except User.DoesNotExist:
            raise Exception(12007)
        if to_update.get("password",""):
            raise Exception(12005)
        email=to_update.get("email", "")
        if email:
            if not check_email(email):
                raise Exception(12038)
            userObj=User.objects.filter(email__iexact=email)
            # Verify if the email is already present in the Users table and raise an exception if it exists.
            if userObj.exists():
                raise Exception(12050)
        project_id = to_update.pop("project", None)
        if project_id:
            project_id = int(project_id)
            # Verify that the provided project does not already exist in the Project table then raise an exception.
            # Check your project is already present in the UserProjectAssignment table; if not, create a new entry.
            try:
                Project.objects.get(id=project_id)
                UserProjectAssignment.objects.get(project_id=project_id, user_id=update_user_id)
            except Project.DoesNotExist:
                raise Exception(12011)
            except UserProjectAssignment.DoesNotExist:
                new_assign = UserProjectAssignment(user_id=update_user_id, project_id=project_id)
                new_assign.save()
        User.objects.filter(user_id=update_user_id).update(**to_update)
        return Response({"id":update_user_id, "updated_data":to_update})
    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters= admin_post_login,
        request_body=RemoveUserSerializer
    )
    def delete(self,request):
        data = valid_serializer(RemoveUserSerializer(data=request.data), error_code=13005)
        delete_user = int(data["user_id"])
        # Verify that the given user is not already present in the Users table then raise an exception.
        try:
            User.objects.get(id=delete_user)
        except User.DoesNotExist:
            raise Exception(12007)
        User.objects.filter(user_id=delete_user).update(active=0)
        return Response({"id":delete_user})