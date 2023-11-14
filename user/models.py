from django.db import models

class BaseFields(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ModelConfigs(BaseFields):
    id = models.BigAutoField(primary_key=True)
    model_name = models.CharField(max_length=500)
    model_type = models.CharField(max_length=500)
    max_length = models.IntegerField()
    temperature = models.FloatField()

    class Meta:
        managed = False
        db_table = 'model_configs'

class Project(BaseFields):
    id = models.BigAutoField(primary_key=True)
    project_name = models.CharField(max_length=500)
    namespace = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=1)

    class Meta:
        managed = False
        db_table = 'project'

class ProjectDataCategory(BaseFields):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'project_data_category'

class ProjectData(BaseFields):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    category = models.ForeignKey(ProjectDataCategory, on_delete=models.PROTECT)
    name = models.TextField()
    data_id = models.CharField(max_length=500)
    extra_data = models.JSONField(null=True, blank=True)
    is_general = models.IntegerField(default=0)
    is_delete = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'project_data'

class User(BaseFields):
    id = models.BigAutoField(primary_key=True)
    current_project = models.ForeignKey(Project, on_delete=models.PROTECT)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=70)
    active = models.BooleanField(default=1)
    timestamp = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'user'

class UserProjectAssignment(BaseFields):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    is_admin = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'user_project_assignment'

class UserRequest(BaseFields):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=500)
    project_name = models.CharField(max_length=500)
    is_approved = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'user_request'

class Admin(BaseFields):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=70)

    class Meta:
        managed = False
        db_table = 'admin'