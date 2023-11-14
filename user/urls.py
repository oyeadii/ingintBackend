from django.urls import path
from user.views import (
                        account,
                        login,
                        project_switch,
                        projects,
                        users,
                        file_manager
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

    path('all_files', file_manager.FilesView.as_view(), name='all-files'),
    path('delete_all_files', file_manager.AllFilesDeleteView.as_view(), name='delete-all-files'),
    path('delete_single_file', file_manager.SingleFileDeleteView.as_view(), name='delete-single-file'),
    path('update_file_tag', file_manager.FileTagView.as_view(), name='update-file-tag'),
]
