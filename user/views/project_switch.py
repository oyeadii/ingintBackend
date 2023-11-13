import json
from user.tags import USER
from rest_framework.response import Response
from user.models import UserProjectAssignment
from drf_yasg.utils import swagger_auto_schema
from custom_lib.api_view_class import PostLoginAPIView


class ProjectSwitchView(PostLoginAPIView):
    @swagger_auto_schema(
        tags=[USER]
    )
    def get(self, request):
        user_id = request.userid
        current_project = request.project
        current_project_id = current_project.pk

        userProjects = UserProjectAssignment.objects.filter(user_id=user_id)
        project_list = [
            {
                'project_id': user_project.project.pk,
                'project_name': user_project.project.project_name,
            }
            for user_project in userProjects
            if user_project.project.pk != current_project_id
        ]
        return Response({"project_list": project_list, "current_project":{"id": current_project_id, "project_name": current_project.project_name}})

    
    @swagger_auto_schema(
        tags=[USER]
    )
    def post(self, request):
        user_id = request.userid
        request_data = request.body.decode('utf-8')
        data = json.loads(request_data)

        project_id = data.get("project_id", "")
        if not project_id:
            raise Exception(12006)
        
        try:
            userProject=UserProjectAssignment.objects.get(user_id=user_id, project_id=int(project_id))
        except UserProjectAssignment.DoesNotExist:
            raise Exception(12013)
        
        return Response({
                        "current_project": userProject.user.current_project.project_name,
                        "token": userProject.user.current_project.namespace
                        })