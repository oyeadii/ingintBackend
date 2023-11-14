from rest_framework import serializers
from custom_lib.base_serializer import BaseSerializer


class SignUpSerializer(BaseSerializer):
    email = serializers.EmailField(required=True)

class AdminSignUpSerializer(BaseSerializer):
    email = serializers.EmailField(required=True)
    project = serializers.CharField(required=True)
    is_admin = serializers.IntegerField(required=True)
    is_existing = serializers.IntegerField(required=True)

class UpdateUserSerializer(BaseSerializer):
    to_update = serializers.DictField(required=True)
    update_user_id=serializers.IntegerField(required=True)

class DeleteUserSerializer(BaseSerializer):
    delete_user_id=serializers.IntegerField(required=True)

class UserDataSerializer(BaseSerializer):
    page = serializers.IntegerField(required=True)
    type = serializers.CharField(required=True)
    details = serializers.BooleanField(required=True)
    project_id = serializers.IntegerField(required=False)
    column = serializers.CharField(required=False)
    order_by = serializers.CharField(required=False)

class AddDataUserSerializer(BaseSerializer):
    email = serializers.CharField(required=True)
    admin = serializers.BooleanField(required=True)
    project_id = serializers.IntegerField(required=True, allow_null=True)

class AddUserSerializer(BaseSerializer):
    user_data = AddDataUserSerializer(many=True)

class EditUserSerializer(BaseSerializer):
    to_update = serializers.DictField(required=True)
    user_id=serializers.IntegerField(required=True)

class RemoveUserSerializer(BaseSerializer):
    user_id=serializers.IntegerField(required=True)

class ProjectDataSerializer(BaseSerializer):
    page = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=False)
    column = serializers.CharField(required=False)
    order_by = serializers.CharField(required=False)

class ProjectUpdateSerializer(BaseSerializer):
    project_id = serializers.IntegerField(required=True)
    to_update = serializers.DictField(required=True)

class ProjectDeleteSerializer(BaseSerializer):
    project_id=serializers.IntegerField(required=True)

class ProjectUserSerializer(BaseSerializer):
    user_id = serializers.IntegerField(required=True)
    admin = serializers.BooleanField(required=True)

class ProjectAddSerializer(BaseSerializer):
    user_data = ProjectUserSerializer(many=True)
    project = serializers.CharField(required=True)

class UserProjectAssignmentDataSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)
    param = serializers.CharField(required=True)
    is_admin = serializers.BooleanField(default=0)
    remove = serializers.BooleanField(default=0)

class UserProjectAssignmentSerializer(BaseSerializer):
    details = UserProjectAssignmentDataSerializer(many=True)
    id = serializers.IntegerField(required=True)

class PageDataSerializer(BaseSerializer):
    q=serializers.CharField(required=True)

class FileDeleteSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)

class FileTagSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)
    category_id = serializers.IntegerField(required=True)