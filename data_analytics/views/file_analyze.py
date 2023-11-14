import json
import uuid
from django.conf import settings
from django.http import StreamingHttpResponse
from data_analytics.tags import DATA_ANALYTICS
from drf_yasg.utils import swagger_auto_schema
from data_analytics.helper import crawler as wch
from custom_lib.helper import extract_text_from_file
from custom_lib.storage_service import StorageService
from user.models import ProjectData, ProjectDataCategory
from data_analytics.serializers import WebsiteUploadSerializer
from custom_lib.helper import post_login,post_upload,generate_token
from data_analytics.common_import import PineconeManager, FileTagger
from custom_lib.api_view_class import PostUploadAPIView, PostLoginAPIView


class AnalyzeFileView(PostUploadAPIView):
    def analyze_files(self, project, engagement, token, api_key, request=None):
        storage_service = StorageService()
        bucket_name=settings.AWS_BUCKET_NAME
        objects = storage_service.list_files(token, bucket_name)
        total_files = len(objects)
        categories = list(ProjectDataCategory.objects.values_list('name', flat=True))
        file_tagger = FileTagger(api_key=api_key)

        text_list = []
        metadata_list = []
        for i, obj in enumerate(objects):
            identifier = obj['Key']

            try:
                file_id = str(uuid.uuid4())
                file_contents, content_type = storage_service.get_file_content(identifier, bucket_name)
                
                filename = identifier.split('/')[-1]
                text_content = extract_text_from_file(file_contents, filename)
                text_list.append(text_content)

                category = file_tagger.classify_text(text=text_content, categories=categories[1:],request=request)
                tagObj = ProjectDataCategory.objects.filter(name__iexact=category)

                if not tagObj.exists():
                    category_id = 1
                else:
                    category_id = tagObj.first().id
                    
                metadata = {"file_name": filename, "doc_id": file_id, "category_id": category_id}
                metadata_list.append(metadata)
                fileObj = ProjectData(data_id=file_id, name=filename, category_id=category_id, project=project, is_general=1)
                fileObj.save()
            except Exception as e:
                print(f"Error with file {filename}: {str(e)}")
                storage_service.delete_file(identifier, bucket_name)

            progress = (i + 1) / total_files * 90
            yield f"data:{progress}\n\n"

        pinecone_manager = PineconeManager(openai_api_key=api_key)
        pinecone_manager.add_files_to_index(text_list=text_list, metadata_list=metadata_list, namespace=token)

        for obj in objects:
            identifier = obj['Key']
            storage_service.delete_file(identifier, bucket_name)
        yield f"data:100\n\n"

    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=post_upload
    )
    def get(self, request, *args, **kwargs):
        api_key=request.apikey
        token=request.namespace
        project=request.project
        engagement=request.engagement
        
        response = StreamingHttpResponse(self.analyze_files(project, engagement, token, api_key, request=request), content_type='text/event-stream')
        response['Access-Control-Allow-Origin'] = '*'
        return response


class AnalyzeWebsiteView(PostLoginAPIView):
    def analyze_website(self, project, engagement, api_key, link,request=None):
        crawler=wch.Crawler(url=link)
        website_content=crawler.get_all_site_content()
        website_id = str(uuid.uuid4())
        
        yield f"data:25\n\n"

        categories = list(ProjectDataCategory.objects.values_list('name', flat=True))
        file_tagger = FileTagger(api_key=api_key)
        category = file_tagger.classify_text(text=website_content, categories=categories[1:],request=request)
        tagObj = ProjectDataCategory.objects.filter(name__iexact=category)
        if not tagObj.exists():
            category_id = 1
        else:
            category_id = tagObj.first().id

        yield f"data:50\n\n"

        metadata = {"file_name": link, "doc_id": website_id, "category_id": category_id}
        fileObj = ProjectData(data_id=website_id, name=link, category_id=category_id, project=project, is_general=1)
        fileObj.save()

        yield f"data:75\n\n"

        pinecone_manager = PineconeManager(openai_api_key=api_key)
        pinecone_manager.add_files_to_index(text_list=[website_content], metadata_list=[metadata], namespace=project.namespace)
        yield f"data:100\n\n"

    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=post_login,
        request_body=WebsiteUploadSerializer
    )
    def post(self, request):
        api_key=request.apikey
        project=request.project
        engagement=request.engagement 
        request_data = request.body.decode('utf-8')
        data = json.loads(request_data)
        link = data.get("link","")
        if not link:
            raise Exception(13005)
        
        if project.namespace == None:
            project.namespace = generate_token()
            project.save()

        response = StreamingHttpResponse(self.analyze_website(project, engagement, api_key, link, request=request), content_type='text/event-stream')
        response['Access-Control-Allow-Origin'] = '*'
        return response