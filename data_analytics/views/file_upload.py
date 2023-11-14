from django.conf import settings
from rest_framework import status
from rest_framework import parsers
from custom_lib.helper import generate_token
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from data_analytics.tags import DATA_ANALYTICS
from drf_yasg.utils import swagger_auto_schema
from custom_lib.storage_service import StorageService
from custom_lib.api_view_class import PostLoginAPIView
from django.core.exceptions import SuspiciousFileOperation
from custom_lib.helper import post_login, multiple_files, file_name_changer
 

class FileUploadView(PostLoginAPIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.FileUploadParser]

    def file_upload_generator(self, files, token):
        bucket_name=settings.AWS_BUCKET_NAME
        storage_service = StorageService()

        folder = f'{token}/'
        total_files = len(files)
        successful_uploads = 0
        for i, file in enumerate(files):
            try:
                file_name = str(file.name)
                extension = file_name.split('.')[-1].lower()
                if extension not in (settings.ALLOWED_EXTENSION).split(","):
                    raise SuspiciousFileOperation(f"Invalid file extension for file: {file_name}")
                file_path = folder + file_name

                progress = (i + 1) / total_files * 90
                yield f"data:{progress}\n\n"

                storage_service.upload_file(file=file, path=file_path, bucket_name=bucket_name)
                successful_uploads += 1
            except SuspiciousFileOperation as e:
                yield f"data:error:{e}\n\n"
                continue

        if successful_uploads == 0:
            yield f"data:error:No files were uploaded successfully.\n\n"
        else:
            yield f"data:100\n\n"
            yield f"data:token:{token}\n\n"

    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=[*post_login, multiple_files],
        consumes=["multipart/form-data"],
    )
    def post(self, request, *args, **kwargs):
        try:
            files = request.FILES.getlist('files')
            files = list(map(file_name_changer, files))
            project = request.project

            if not files:
                raise Exception(13011)

            if project.namespace == None:
                project.namespace = generate_token()
                project.save()

            response = StreamingHttpResponse(self.file_upload_generator(files, project.namespace), content_type='text/event-stream')
            response['Access-Control-Allow-Origin'] = '*' 
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)