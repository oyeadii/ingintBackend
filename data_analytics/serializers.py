from rest_framework import serializers
from custom_lib.base_serializer import BaseSerializer

 
class AnomalySerializer(BaseSerializer):
    workbook = serializers.DictField(required=True)
    sheet_num = serializers.IntegerField(required=True)
    pct_threshold = serializers.FloatField(required=True)
    abs_threshold = serializers.IntegerField(required=True)

class DAFileDeleteSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)

class DataAnalyzeSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)
    column_name = serializers.CharField(required=True)

class DACommentarySerializer(BaseSerializer):
    selected_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

class DataChatbotSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)
    query = serializers.CharField(required=True)

class RevenueTrendsSerializer(BaseSerializer):
    workbook = serializers.DictField(required=True)
    sheet_num = serializers.IntegerField(required=True)
    pct_threshold = serializers.FloatField(required=True)

class TAFileSerializer(BaseSerializer):
    file_id = serializers.CharField(required=True)

class TAPlotSerializer(BaseSerializer):
    table_id = serializers.IntegerField(required=True)
    file_id = serializers.CharField(required=True)
    sheet_name = serializers.CharField(required=True)

class TACommentarySerializer(BaseSerializer):
    commentary_type = serializers.CharField(required=True)
    selected_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    sheet_name = serializers.CharField(required=True)
    table_id = serializers.IntegerField(required=True)
    file_id = serializers.IntegerField(required=False)

class TAPrintSerializer(BaseSerializer):
    slide_data = serializers.DictField(required=True)
    image_data = serializers.CharField(required=True)

class TASummarySerializer(BaseSerializer):
    sheet_name = serializers.CharField(required=True)
    table_id = serializers.IntegerField(required=True)
    file_id = serializers.IntegerField(required=False)
    commentary_type = serializers.CharField(required=True)
    
class DataValidationSerializer(BaseSerializer):
    json_data = serializers.DictField(required=True)
    card_name = serializers.CharField(required=True)
    sample = serializers.BooleanField(default=False)

class DataFetchSerializer(BaseSerializer):
    card_name = serializers.CharField(required=True)

class PostDataQualitySerializer(BaseSerializer):
    log_data = serializers.ListField(required=True)

class GetDataQualitySerializer(BaseSerializer):
    project_id = serializers.IntegerField(required=True)
    
class GetFunctionChoicesSerializer(BaseSerializer):
    function_type = serializers.CharField(required=True)

class FileGPTSerializer(BaseSerializer):
    prompt = serializers.CharField(required=True)
    selected_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

class WebsiteUploadSerializer(BaseSerializer):
    link = serializers.CharField(required=True)

class UploadSerializer(BaseSerializer):
    identifier = serializers.CharField(required=True)