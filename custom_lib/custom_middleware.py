from custom_lib.helper import get_error_msg
from django.http import  JsonResponse
from rest_framework import status


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        error = str(exception)
        try:
            err_msg,errorCode=eval(error)
        except:
            err_msg=''
            errorCode=error
            if not str(errorCode).isdigit():
                err_msg = errorCode
        if  str(errorCode).isdigit():
            err_msg=err_msg or get_error_msg(errorCode)
            if int(errorCode)==11001:
                response = JsonResponse({"errorCode": int(errorCode),"errorMessage":err_msg}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                response = JsonResponse({"errorCode": int(errorCode),"errorMessage":err_msg}, status=status.HTTP_400_BAD_REQUEST)
        else:
            err_msg=error
            response = JsonResponse({"errorCode": 11000,"errorMessage":"Oops,unknown error occured! Please try again"}, status=status.HTTP_400_BAD_REQUEST) #errorCode
        if hasattr(request,"logObj"):
            code = 11000
            if str(errorCode).isdigit():
                code = errorCode
            request.logObj.print_log(f"{code} - {err_msg}","error")
        
        return response