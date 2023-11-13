from django.urls import path
from user.views import (
                        account,
                        login,
                        project_switch,
                        projects,
                        users
)


urlpatterns = [
    path('user_login', login.LoginView.as_view(), name='user-login'),
    path('admin_login', login.AdminLoginView.as_view(), name='admin-login'),

    path('projects', projects.ProjectsView.as_view(), name='projects'),
    path('details', users.UsersDetailsView.as_view(), name='user-details'),
    path('project_details', projects.ProjectView.as_view(), name='project-details'),
    path('create_new_user', account.CreateNewUserView.as_view(), name='create-new-user'),
    path('project_switch', project_switch.ProjectSwitchView.as_view(), name='project-switch'),
    path('user_project_assignment', projects.UserProjectAssignmentView.as_view(), name='project-details'),
]
