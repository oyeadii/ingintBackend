import math
import json as js
from datetime import datetime
from rest_framework.utils import json
from rest_framework.renderers import JSONRenderer


class DateTimeEncoder(js.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class JSONResponseRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_dict = {
            'errorCode': 0,
            'errorMessage': 'Success',
            "data": []
        }

        if data:
            response_dict['data'] = data
        
        return json.dumps(response_dict, default=str)
    
class WorkbookResponseRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = self.handle_nan_values(data)
        return json.dumps(data,default=str)
    
    def handle_nan_values(self, obj):
        if isinstance(obj, list):
            return [self.handle_nan_values(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.handle_nan_values(value) for key, value in obj.items()}
        elif isinstance(obj, float) and math.isnan(obj):
            return ""
        else:
            return obj

class DataAnalysisResponseRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_dict = {
            'errorCode': 0,
            'errorMessage': 'Success',
            'data': [],
        }
        if data:
            data = self.handle_nan_values(data)
            response_dict['data'] = data
        data = response_dict
        return json.dumps(data, default=str)

    def handle_nan_values(self, obj):
        if isinstance(obj, list):
            return [self.handle_nan_values(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.handle_nan_values(value) for key, value in obj.items()}
        elif isinstance(obj, float) and math.isnan(obj):
            return ""
        elif isinstance(obj, datetime):
            return obj.isoformat() 
        else:
            return obj