from django.urls import path
from . import views

urlpatterns = [
    path("job-roles/get-goal/<int:job_role_id>/", views.get_goal),
    path("job-roles/", views.JobRoleListView.as_view(), name="job-role-list"),


]
