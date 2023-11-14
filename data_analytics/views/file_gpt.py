import pandas as pd
from django.conf import settings
from rest_framework import parsers
from data_analytics.tags import DATA_ANALYTICS
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from drf_yasg.utils import swagger_auto_schema
from data_analytics.helper import file_gpt as fgh
from data_analytics.common_import import FileAnalyzer
from user.models import ProjectDataCategory, ProjectData
from data_analytics.serializers import FileGPTSerializer
from custom_lib.api_view_class import PostLoginAPIView, PostUploadAPIView
from custom_lib.helper import post_login,post_upload,single_file,valid_serializer,generate_token, file_name_changer


class FileGPTView(PostLoginAPIView):
    parser_classes = [parsers.MultiPartParser,parsers.FormParser,parsers.FileUploadParser]

    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=post_upload
    ) 
    def get(self,request):
        project=request.project

        filesObj=ProjectData.objects.filter(project=project, is_general=1, is_delete=0)
        if not filesObj.exists():
            return Response({})
        
        df_result=pd.DataFrame(list(filesObj.values('id','name')))
        return Response(df_result.to_dict(orient='records'))
    
    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=[*post_login, single_file],
        consumes=["multipart/form-data"],
    )
    def post(self, request, *args, **kwargs):
        api_key=request.apikey
        project=request.project
        file = request.FILES.get('file')
        if not file:
            raise Exception(13007)
        file=file_name_changer(file=file)
        file_name = file.name
        extension=file_name.split('.')[-1].lower()
        if extension not in (settings.ALLOWED_EXTENSION).split(","):
            raise Exception(13006) 
        
        if project.namespace == None:
            project.namespace = generate_token()
            project.save()
 
        category_dict = {category.id: category.name for category in ProjectDataCategory.objects.all()}
        file_analyzer=FileAnalyzer(project=project, api_key=api_key, category_dict=category_dict) 
        file_analyzer.analyze_file(file=file, is_general=1)
        return Response({"message":"File Uploaded Successfully!"})
    

class FileGPTQueryView(PostUploadAPIView):
    @swagger_auto_schema(
    tags=[DATA_ANALYTICS],
    manual_parameters=post_upload,
    request_body=FileGPTSerializer
)
    def post(self, request, *args, **kwargs):
        user_id=request.userid
        api_key=request.apikey
        project=request.project
        template=request.template
        model_name=request.modelname
        temperature=request.temperature
        data = valid_serializer(FileGPTSerializer(data=request.data), error_code=13005)

        fileObj=ProjectData.objects.filter(project=project)
        selected_ids = data["selected_ids"]
        if len(selected_ids)==0:
            raise Exception(13027)

        file_ids = list(fileObj.filter(id__in=selected_ids).values_list('data_id', flat=True))
        filter={"doc_id": {"$in":file_ids}}
        resp = fgh.FileGPT(
                                       user_id=user_id,
                                       project_id=project.id,
                                       input_prompt=data["prompt"],
                                       namespace=project.namespace,
                                       api_key=api_key,
                                       template=template,
                                       temperature=temperature,
                                       model_name=model_name,
                                       filter=filter
                                       )
        return StreamingHttpResponse(resp.get_response(), content_type='text/event-stream')