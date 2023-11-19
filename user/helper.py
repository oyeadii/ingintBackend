import bcrypt
from django.db.models import Count, Q
from custom_lib.helper import check_email
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from user.models import User, Project, UserProjectAssignment


class CustomPagination(PageNumberPagination):
    page_size = 10

class UserFilter(filters.FilterSet):
    project_name = filters.CharFilter(method='filter_by_project')
    created_at = filters.DateFromToRangeFilter()
    email = filters.CharFilter(method='filter_by_email')
    user = filters.CharFilter(method='filter_by_user')

    class Meta:
        model = User
        fields = ['created_at']

    def filter_by_project(self, queryset, name, value):
        return queryset.filter(userprojectassignment__project__project_name=value)
    
    def filter_by_email(self, queryset, name, value):
        return queryset.filter(email__contains=value)
    
    def filter_by_user(self, queryset, name, value):
        return queryset.filter(Q(email__contains=value)| Q(first_name__contains=value)| Q(last_name__contains=value))

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.annotate(num_projects=Count('userprojectassignment__project', distinct=True))
        return queryset


class ProjectFilter(filters.FilterSet):
    project_name = filters.CharFilter(method='filter_by_project')
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Project
        fields = ['created_at']

    def filter_by_project(self, queryset, name, value):
        return queryset.filter(Q(project_name__contains=value))

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset
    
def handle_user_assignment_v2(datas, project_object, request):
    end_point = request.path.split("/")[-1]
    for data in datas:
        # Step 1: Check Email
        if end_point=='project_details':
            try:
                userObj = User.objects.get(id__iexact=data['user_id'])
                data["email"] = userObj.email
            except User.DoesNotExist:
                continue
        if not check_email(data["email"]):
            raise Exception(12016)

        # Step 2: Fetch or Try to Fetch User
        try:
            userObj = User.objects.get(email__iexact=data["email"])
            if project_object:
                try:
                    UserProjectAssignment.objects.get(user_id=userObj.id, project=project_object)
                    raise Exception(12001)
                except UserProjectAssignment.DoesNotExist:
                    userProject = UserProjectAssignment(user_id=userObj.id, project=project_object, is_admin=data["admin"])
                    userProject.save()
        except User.DoesNotExist:
            try:
                userObj = User.objects.get(email__iexact=data["email"])
                raise Exception(12002)
            except User.DoesNotExist:
                pass

            # Step 3: Handle Case Where User Does Not Exist
            # password = generate_password()
            password="Ingint123"
            bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(bytes, salt)
            hash_password = hash.decode('utf-8')
            user = User(email=data["email"], password=hash_password)
            user.save()
    
            if project_object:
                userProject = UserProjectAssignment(project=project_object, user_id=user.pk, is_admin=data["admin"])
                userProject.save()
    return
