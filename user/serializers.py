from rest_framework import serializers
from custom_lib.base_serializer import BaseSerializer


class DeleteProjectSerializer(BaseSerializer):
    delete_project_id=serializers.IntegerField(required=True)

class QuestionsDeleteSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)

class AdSignUpSerializer(BaseSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, required=True)

class DeleteAdminSerializer(BaseSerializer):
    delete_user_id=serializers.IntegerField(required=True)

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

class FileDeleteSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)

class FileTagSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)
    category_id = serializers.IntegerField(required=True)

class ProjectRegistrationSerializer(BaseSerializer):
    project = serializers.CharField(required=True)
    same_users = serializers.CharField(required=True)

class LoginSerializer(BaseSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class LoginAdminSerializer(BaseSerializer):
    admin = serializers.BooleanField()

class AdminLoginSerializer(BaseSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class RequestAccessSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    message = serializers.CharField(required=True)

class PostWSNIssueSerializer(BaseSerializer):
    hypotheses = serializers.CharField(required=True)

class WSNIssueDeleteSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)

class FeedbackSerializer(BaseSerializer):
    feedback_type = serializers.CharField(required=True)
    feedback_text = serializers.CharField(required=True)
    user_query = serializers.CharField(required=True)
    ai_response = serializers.CharField(required=True)
    extra_feedback = serializers.ListField(required=False)


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

class PostQueryQuestionsSerializer(BaseSerializer):
    question_id = serializers.IntegerField(required=True)
    question = serializers.CharField(required=True)
    answer = serializers.CharField(required=True)
    chunks = serializers.ListField(child=serializers.DictField(), required=True)
    custom_chunk = serializers.DictField(required=False)

class AuditTrailSerializer(BaseSerializer):
    question_id = serializers.IntegerField(required=True)

class AuditSerializer(BaseSerializer):
    id = serializers.IntegerField(required=True)

class RetrieveImageSerializer(BaseSerializer):
    image_path = serializers.CharField(required=True)
    coordinates = serializers.DictField(required=False)

class CustomChunkSerializer(BaseSerializer):
    question_id = serializers.IntegerField(required=True)
    topic = serializers.CharField(required=True)
    sub_topic = serializers.CharField(required=True)
    text = serializers.CharField(required=True)