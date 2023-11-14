import json
from rest_framework import parsers
from rest_framework.response import Response
from data_analytics.tags import DATA_ANALYTICS
from drf_yasg.utils import swagger_auto_schema
from custom_lib.api_view_class import PostLoginAPIView
from data_analytics.serializers import AnomalySerializer
from custom_lib.renderer import WorkbookResponseRenderer
from data_analytics.helper import anomaly_detection as adh
from custom_lib.workbook_helper import WorkbookLoader, WorkbookDeLoader
from custom_lib.helper import post_login, post_upload, single_file, file_name_changer


class WorkbookUploadView(PostLoginAPIView):
    renderer_classes = [WorkbookResponseRenderer]
    parser_classes = [parsers.MultiPartParser,parsers.FormParser,parsers.FileUploadParser]
    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=[*post_upload, single_file],
        consumes=["multipart/form-data"],
    )
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            raise Exception(13007)
        file=file_name_changer(file=file)
        file_name = file.name
        extension=file_name.split('.')[-1].lower()
        if extension not in ['xls','xlsx','csv']:
            raise Exception(13006)

        output_dict = WorkbookLoader().get_output_dict(file, extension)
        resp=output_dict
        return Response(resp)


class AnomalyDetectionView(PostLoginAPIView):
    @swagger_auto_schema(
    tags=[DATA_ANALYTICS],
    manual_parameters=post_login,
    request_body=AnomalySerializer
    )
    def post(self, request, *args, **kwargs):
        request_data = request.body.decode('utf-8')
        data = json.loads(request_data)
        workbook=data.get("workbook","")
        sheet_num=data.get("sheet_num",[])
        abs_threshold=data.get("abs_threshold",[])
        pct_threshold=data.get("pct_threshold",[])

        if not workbook:
            raise Exception(13005)
        if (len(sheet_num) ==0)  or (len(pct_threshold)==0) or (len(abs_threshold)==0):
            raise Exception(13005)
        
        abs_threshold = int(abs_threshold[0])
        pct_threshold = float(pct_threshold[0])
        sheet_num = int(sheet_num[0])
        if abs_threshold<0:
            raise Exception(13025)
        if not (0.0<=pct_threshold<=100.0):
            raise Exception(13025)
        
        wdh = WorkbookDeLoader()
        ad_helper = adh.AnomalyDetection()
        df = wdh.get_dataframe(output_dict=workbook, sheet_number=sheet_num)
        resp = ad_helper.get_anomalies_list(df, abs_threshold, pct_threshold, True)
        return Response(resp)