from django.contrib import admin
from django.urls import path
from job import views
urlpatterns = [
    # Client
    path("jobs/create/", views.create_job, name="create_job"),
    path("jobs/client/", views.client_jobs, name="client_jobs"),

    # Freelancer
    path("jobs/browse/", views.browse_jobs, name="browse_jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),

    # Job lifecycle
    path("jobs/delete/<int:job_id>", views.delete_job, name="delete_job"),
]
