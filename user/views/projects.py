from user.tags import ADMIN
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db.models.functions import Coalesce
from user.models import Project, UserProjectAssignment, User
from custom_lib.helper import admin_post_login, valid_serializer
from custom_lib.api_view_class import AdminAPIView, CustomAPIView
from django.db.models import F,Count, OuterRef, IntegerField, Subquery, Q
from user.helper import CustomPagination, ProjectFilter, handle_user_assignment_v2
from user.serializers import ProjectDeleteSerializer, ProjectDataSerializer, ProjectAddSerializer, UserProjectAssignmentSerializer, PageDataSerializer, ProjectUpdateSerializer


class ProjectsView(CustomAPIView):
    @swagger_auto_schema(
        tags=[ADMIN]
    )
    def get(self, request):
        projects = list(Project.objects.all().values_list("project_name",flat=True))
        return Response({"projects":projects})


class ProjectView(AdminAPIView):
    filterset_class = ProjectFilter
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login,
        query_serializer = ProjectDataSerializer
    )
    def get(self, request):
        # Check if 'page' parameter is present in the request's parameters then raise an exception
        column = request.GET.get("column", None)
        sort_order = request.GET.get("order_by", None)
        project_name = request.GET.get("project_name", None)
        if project_name and len(project_name)<2:
            raise Exception("Provide two or more characters for this filter", 12041)
        filterset = self.filterset_class(request.GET, queryset=Project.objects.filter(active=True).all())
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        
        projects = filterset.qs.values("id", "project_name", "created_at")
        projects = (projects.annotate(assignments=Count('userprojectassignment__user_id', distinct=True))
                    .filter(active=True))
        if column:
            if sort_order=="desc":
                column = "-"+column
        else:
            column = '-created_at'
        if int(request.query_params.get("page",0)):
            paginator = CustomPagination()
            page = paginator.paginate_queryset(projects, request)
            if page is not None and len(page) > 0:
                return paginator.get_paginated_response({"project": page})
        else:
            user_id = int(request.query_params.get("user_id",0))
            user_project = []
            if user_id:
                new_project = []
                subquery = UserProjectAssignment.objects.filter(
                    project_id=OuterRef('id'), user_id=user_id
                ).values('user_id')[:1]
                projects = projects.annotate(
                    user_id=Coalesce(Subquery(subquery, output_field=IntegerField()), 0)
                )
                projects = projects.annotate(is_admin = F("userprojectassignment__is_admin"))
                projects = projects.annotate(user_id_upa = F("userprojectassignment__user_id"))
                # In feature if playground need to be remove from the listing uncomment the below line
                # projects=projects.exclude(project_name__endswith="Playground")

                user_project = list(projects.filter(user_id_upa=user_id).values("id", "project_name", "is_admin"))
                new_project_query = list(projects.filter(Q(user_id_upa__isnull=True) | ~Q(user_id_upa=user_id)).values("id", "project_name"))
                temp_project_id = [item['id'] for item in user_project]
                new_project = []
                for data in new_project_query:
                    if data.get("id") not in temp_project_id:
                        new_project.append(data)
                projects = sorted(new_project, key=lambda x: x['project_name'])
                user_project = sorted(user_project, key=lambda x: x['project_name'])
            return Response({"results":{"project": list(projects),"user_project": user_project},"count":len(user_project)+len(projects)})

    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login,
        request_body = ProjectAddSerializer
    )
    def post(self, request):
        data = valid_serializer(ProjectAddSerializer(data=request.data), error_code=12006)
        project_name = data["project"]
        emails = data["user_data"]
        
        project = Project.objects.filter(project_name__iexact=project_name, active=True).first()
        if project:
            raise Exception(12039)

        project = Project(project_name=project_name)
        project.save()

        if project:
            handle_user_assignment_v2(emails, project, request)
        return Response("success")
    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters= admin_post_login,
        request_body=ProjectUpdateSerializer
    )
    def put(self,request):
        data = valid_serializer(ProjectUpdateSerializer(data=request.data), error_code=13005)
        project_id = int(data["project_id"])
        to_update = data["to_update"]
        # Check if 'project_name' is not in the update data then raise an exception if it's missing.
        if "project_name" not in to_update:
            raise Exception(13025)
        # Check if the given project exists in the 'Project' table then raise an exception if it does not.
        try:
            Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise Exception(12013)
        Project.objects.filter(id=project_id).update(project_name= to_update["project_name"])
        return Response({"id":project_id, "updated_data":to_update})
    
    @swagger_auto_schema(
        tags=[ADMIN],
        manual_parameters=admin_post_login,
        request_body=ProjectDeleteSerializer
    )
    def delete(self, request):
        data = valid_serializer(ProjectDeleteSerializer(data=request.data), error_code=13005)
        delete_project = int(data["project_id"])
        # Check if the given project exists in the 'Project' table then raise an exception if it does not.
        try:
            Project.objects.get(id=delete_project)
        except Project.DoesNotExist:
            raise Exception(12013)
        Project.objects.filter(id=delete_project).update(active=False)
        return Response({"id": delete_project})
    

class UserProjectAssignmentView(AdminAPIView):
    @swagger_auto_schema(
            tags=[ADMIN],
            manual_parameters=admin_post_login,
            request_body=UserProjectAssignmentSerializer,
            query_serializer=PageDataSerializer
    )
    def put(self, request):
        q = request.query_params.get('q')
        valid_fields = ("users", "projects")
        assert q in valid_fields, "not a valid fields"
        data = valid_serializer(UserProjectAssignmentSerializer(data=request.data), error_code=13005)

        new_assignment = []
        update_assignment = []
        id_list = {}
        remove_ids = []
        for user in data["details"]:
            param = user['param']
            assert param in valid_fields, "not a valid fields"
            assert param != q, "Both the query params and the user params are same"
            id_list.update({user["id"]:user["is_admin"]})
            if user["remove"]:
                remove_ids.append(user["id"])
        if q=='users':
            datas = Project.objects.filter(id__in=id_list.keys()).values_list('id')
        else:
            datas = User.objects.filter(id__in=id_list.keys()).values_list('id')
        currect_user = { user_id[0] for user_id in datas}
        diff_id = list(set(id_list.keys()).difference(currect_user))
        if diff_id:
            return Response("Following Project or Users is invalid "+",".join(str(num) for num in diff_id))

        query = Q(user_id=data['id']) if q == 'users' else Q(project_id=data['id'])
        query1 = Q(project_id__in=id_list.keys()) if q == 'users' else Q(user_id__in=id_list.keys())
        find_users =UserProjectAssignment.objects.filter(query, query1)
        if q=='users':
            old_datas = {find_user.project_id for find_user in find_users}
        else:
            old_datas = {find_user.id for find_user in find_users}

        if find_users:
            id = 'project_id' if q == 'users' else 'id'
            for value in find_users:
                current_id = getattr(value,id)
                if current_id in id_list.keys():
                    value.is_admin = True if id_list[current_id] else False
                    update_assignment.append(value)
        new_assigns = list(set(id_list.keys()).difference(old_datas))
        if new_assigns:
            for new_assign in new_assigns:
                new_assignment.append(
                    UserProjectAssignment(
                        user_id=data["id"] if q=='users' else new_assign,
                        project_id=new_assign if q=='users' else data["id"],
                        is_admin=True if id_list[new_assign] else False
                    )
                )
        if update_assignment:
            UserProjectAssignment.objects.bulk_update(update_assignment, ['is_admin'])
        if new_assignment:
            UserProjectAssignment.objects.bulk_create(new_assignment)
        if remove_ids:
            query1 = Q(project_id__in=remove_ids) if q == 'users' else Q(user_id__in=remove_ids)
            UserProjectAssignment.objects.filter(query1).delete()
        return Response("Successfully user added to project")
