import json
import pandas as pd 
from rest_framework import parsers
from user.models import ProjectData
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from data_analytics.tags import DATA_ANALYTICS
from drf_yasg.utils import swagger_auto_schema
from custom_lib.renderer import DataAnalysisResponseRenderer
from data_analytics.common_import import upload_project_data
from data_analytics.helper import trend_analysis as ta_helper
from custom_lib.api_view_class import PostLoginAPIView, PostUploadAPIView
from custom_lib.helper import post_login, post_upload, single_file, valid_serializer, file_name_changer
from data_analytics.serializers import TAFileSerializer, TAPlotSerializer, TACommentarySerializer, TASummarySerializer
from data_analytics.prompts.trend_analysis_prompts import QUESTIONS_DICT, SUMMARY_PROMPT, TREND_ANALYSIS_PROMPT, temperature, model_name


class TAFileUploadView(PostLoginAPIView):
    parser_classes = [parsers.MultiPartParser,parsers.FormParser,parsers.FileUploadParser]

    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=post_login
    )
    def get(self, request, *args, **kwargs):
        project=request.project

        filesObj = ProjectData.objects.filter(project=project, is_general=0, is_delete=0).values('id', 'name')
        if not filesObj.exists():
            return Response({})
        return Response(list(filesObj))
    
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
        if extension not in ['xls','xlsx']:
            raise Exception(13006)
        
        all_data={}
        trend_helper=ta_helper.TrendAnalysisHelper(uploaded_file=file)
        sheets=trend_helper.get_excel_sheets()
        for sheet in sheets:
            sheet_data=[]
            try:
                tables=trend_helper.get_tables(sheet_name=sheet)
                for i, table in enumerate(tables):
                    try:
                        columns_list=list(trend_helper.get_columns(table=table))
                        data_list=trend_helper.get_clean_list(table=table)
                        x_axis_list=trend_helper.get_x_axis_columns(table=table)
                        table_id=i+1

                        sheet_data.append({
                                            "table_id":table_id,
                                            "columns":columns_list,
                                            "x_axis_value":x_axis_list,
                                            "data_list":data_list
                                        })
                    except:
                        continue
            except:
                continue
            if sheet_data:
                all_data[sheet.strip()]=sheet_data

        data={"all_data": all_data}
        dataObj = upload_project_data(api_key, project, file_name, data)
        dataObj.save()
        return Response({"message":"File uploaded successfully!"})


class TAFileView(PostLoginAPIView):    
    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=post_login,
        request_body=TAFileSerializer
    )
    def delete(self, request, *args, **kwargs):
        project=request.project
        data = valid_serializer(TAFileSerializer(data=request.data), error_code=13005) 
        try:       
            filesObj = ProjectData.objects.get(project=project, id=data["file_id"])
        except ProjectData.DoesNotExist:
            raise Exception(13021)
        
        filesObj.is_delete=1
        filesObj.save()
        return Response("File deleted successfully!")


class TAPlotDataView(PostLoginAPIView):
    renderer_classes = [DataAnalysisResponseRenderer]
    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=post_login,
        query_serializer=TAFileSerializer
    )
    def get(self, request, *args, **kwargs):
        project=request.project
        data = valid_serializer(TAFileSerializer(data=request.query_params), error_code=13005)
        try:
            trendObjs=ProjectData.objects.get(project=project, id=data["file_id"])
        except ProjectData.DoesNotExist:
            raise Exception(13021)
    
        result_data = {}
        all_data = json.loads(trendObjs.extra_data)
        data = all_data["all_data"]
        for sheet, sheet_data in data.items():
            table_ids = [table["table_id"] for table in sheet_data]
            result_data[sheet] = table_ids
        return Response(result_data)
    
    @swagger_auto_schema(
    tags=[DATA_ANALYTICS],
    manual_parameters=post_login,
    request_body=TAPlotSerializer
)
    def post(self, request):
        project=request.project
        data = valid_serializer(TAPlotSerializer(data=request.data), error_code=13005)
        file_id=data["file_id"]
        sheet_name=data["sheet_name"]
        table_id=data["table_id"]

        try:
            trendObjs=ProjectData.objects.get(project=project, id=file_id)
        except:
            raise Exception(13021)
        
        all_data = json.loads(trendObjs.extra_data)
        data = all_data["all_data"]

        plot_data={}
        sheet_data = data.get(sheet_name, [])
        for table in sheet_data:
            if table["table_id"] == table_id:
                year = table.get("x_axis_value", [])
                data_list = table.get("data_list", [])
                plot_data = {
                    "x_axis_data": year,
                    "y_axis_data": data_list,
                    "x_axis": "Year",
                    "id": table_id
                }
        
        if not plot_data:
            raise Exception(13021)
        
        for key, value in dict(plot_data["y_axis_data"]).items():
            y_axis_data = list(value)
            converted_list = []
            for item in y_axis_data:
                if isinstance(item, (int, float)):
                    converted_list.append(round(item, 2))
                elif isinstance(item, str):
                    try:
                        converted_list.append(round(float(item), 2))
                    except ValueError:
                        converted_list.append(0.0)
                else:
                    converted_list.append(0.0)
            plot_data["y_axis_data"][key]=converted_list

        plot_data={"x_axis_data":year, "y_axis_data": data_list, "x_axis":"Year", "id": trendObjs.pk}
        return Response({"plot_data":plot_data}) 
    

class TACommentaryView(PostUploadAPIView):
    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters= post_upload
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
    manual_parameters=post_upload,
    request_body=TACommentarySerializer
)
    def post(self, request):
        user_id=request.userid
        api_key=request.apikey
        project=request.project
        content = None
        data = valid_serializer(TACommentarySerializer(data=request.data), error_code=13005)
        commentary_type=data["commentary_type"]
        selected_ids=data["selected_ids"]
        question=QUESTIONS_DICT.get(commentary_type.lower(),'')
        ta_obj = None
        if not question:
            raise Exception(13022)
        
        fileObj=ProjectData.objects.filter(project=project, is_delete=0, is_general=1)
        file_ids = fileObj.filter(id__in=selected_ids).values_list('data_id', flat=True)
        file_id_list=list(file_ids)

        filter={"doc_id": {"$in":file_id_list}}
        summary=""
        columns=[]
        if commentary_type in SUMMARY_PROMPT.keys():
            if not data["file_id"]:
                raise Exception(13011)
            try:
                ta_obj = ProjectData.objects.get(id=data["file_id"])
            except ProjectData.DoesNotExist:
                raise Exception(13013)
            
            extra_dt=json.loads(ta_obj.extra_data)
            extra_dt=extra_dt["all_data"]
            sheet_data=extra_dt.get(data["sheet_name"],[])
            for table in sheet_data:
                if table["table_id"] == data["table_id"]:
                    columns=table.get("columns", [])
                    summary=table.get("summary", "")
            content = TREND_ANALYSIS_PROMPT.get(commentary_type).replace("{categories}", str(columns))
            
        resp=ta_helper.TrendGPT(user_id=user_id,
                                project_id=project.id,
                                api_key=api_key,
                                namespace=project.namespace,
                                model_name=model_name, 
                                temperature=temperature,
                                filter=filter)
        return StreamingHttpResponse(resp.run_trend_analysis(question=question, summary=summary, content=content, columns=columns if columns else None), content_type="text/event-stream")


class TASummaryView(PostLoginAPIView):
    @swagger_auto_schema(
        tags=[DATA_ANALYTICS],
        manual_parameters=post_login,
        request_body=TASummarySerializer
    )
    def post(self, request):
        user_id=request.userid
        api_key=request.apikey
        project=request.project
        data = valid_serializer(TASummarySerializer(data=request.data), error_code=13005)
        summary_prompt = SUMMARY_PROMPT.get(data["commentary_type"])
        if not summary_prompt:
            raise Exception(13022)
        
        resp=ta_helper.TrendGPT(user_id=user_id,
                                project_id=project.id,
                                api_key=api_key,
                                namespace=project.namespace,
                                model_name=model_name, 
                                temperature=temperature
                                )
        return StreamingHttpResponse(resp.run_trend_summary(summary_prompt,data['file_id'],data["sheet_name"], data["table_id"], data["commentary_type"]), content_type='text/event-stream')