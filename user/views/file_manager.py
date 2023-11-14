import json
from user.tags import USER
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from user.models import ProjectData,ProjectDataCategory
from data_analytics.common_import import PineconeManager
from user.serializers import FileDeleteSerializer, FileTagSerializer
from custom_lib.helper import post_upload,post_login,valid_serializer
from custom_lib.api_view_class import PostUploadAPIView,PostLoginAPIView


class FilesView(PostLoginAPIView):
    @swagger_auto_schema(
        tags=[USER],
        manual_parameters=post_login
    )
    def get(self, request):
        files_obj = ProjectData.objects.filter(project=request.project, is_delete=0)
        if not files_obj.exists():
            return Response([])
        
        general_files = list(files_obj.filter(is_general=1).values('id', 'name', 'created_at', 'category_id'))
        grouped_files = {"General": {"files":general_files, "upload_url": "/upload"}}

        file_tags = list(ProjectDataCategory.objects.values('id', 'name'))
        return Response({"file_groups": grouped_files, "file_tags": file_tags})


class FileTagView(PostUploadAPIView):
    @swagger_auto_schema(
        tags=[USER],
        manual_parameters= post_upload,
        request_body=FileTagSerializer
        )
    def put(self, request, *args, **kwargs):
        api_key=request.apikey
        namespace=request.namespace
        data = valid_serializer(FileTagSerializer(data=request.data), error_code=12006)
        id = data["id"]
        category_id = data["category_id"]

        try:
            file_obj = ProjectData.objects.get(id=id, is_delete=0)
        except ProjectData.DoesNotExist:
            raise Exception(12046)
        
        try:
            new_category = ProjectDataCategory.objects.get(id=category_id)
        except ProjectDataCategory.DoesNotExist:
            raise Exception(12047)
        
        file_obj.category=new_category
        if file_obj.extra_data:
            dt=json.loads(file_obj.extra_data)
            ids_list=dt.get("chunk_ids", [])
        else:
            ids_list=[]

        pinecone_manager=PineconeManager(openai_api_key=api_key)
        pinecone_manager.update_index_metadata(id_list=ids_list, metadata={"category_id":category_id}, namespace=namespace)
        file_obj.save()
        return Response({"id": id, "category_id": category_id})


class SingleFileDeleteView(PostUploadAPIView):
    @swagger_auto_schema(
        tags=[USER],
        manual_parameters=post_upload,
        request_body=FileDeleteSerializer
    )
    def delete(self, request):
        project=request.project
        namespace=request.namespace
        api_key=request.apikey
        data = valid_serializer(FileDeleteSerializer(data=request.data), error_code=12006)
        
        try:
            fileObj = ProjectData.objects.get(id=data["id"], is_delete=0)
        except ProjectData.DoesNotExist:
            raise Exception(12020)

        file_id=fileObj.data_id
        dt=json.loads(fileObj.extra_data)
        if dt.get("chunk_ids",""):
            pinecone_manager=PineconeManager(openai_api_key=api_key)
            if pinecone_manager.single_delete(file_id=file_id, namespace=namespace)!="success":
                raise Exception(12023)
            
        fileObj.is_delete=1
        fileObj.save()

        fileObj=ProjectData.objects.filter(project=project, is_delete=0)
        if not fileObj.exists():
            project.namespace = None
            project.save()
            return Response({"message":"File Deleted Successfully!", "tokenMessage": "Clear!!"})
        return Response({"message":"File Deleted Successfully!"})

    
class AllFilesDeleteView(PostUploadAPIView):
    @swagger_auto_schema(
        tags=[USER],
        manual_parameters= post_upload
        )
    def delete(self,request):
        api_key=request.apikey
        namespace = request.namespace
        project=request.project

        pinecone_manager=PineconeManager(openai_api_key=api_key)
        if pinecone_manager.complete_delete(namespace=namespace)!="success":
            raise Exception(12023)
        fileObj=ProjectData.objects.filter(project=project)
        fileObj.update(is_delete=1)
        project.namespace = None
        project.save()
        return Response({"message":"Files Deleted Successfully!"})