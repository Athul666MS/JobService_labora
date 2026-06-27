from django.contrib import admin
from django.urls import path
from job import views
from .views import InternalJobStatusUpdateView, CompleteJobView, SubmitJobView, InternalJobListView, \
    InternalJobStatsView

urlpatterns = [
    # Client
    path("jobs/create/", views.create_job, name="create_job"),
    path("jobs/client/", views.client_jobs, name="client_jobs"),

    # Freelancer
    path("jobs/browse/", views.browse_jobs, name="browse_jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),

    # Job lifecycle
    path("jobs/delete/<int:job_id>", views.delete_job, name="delete_job"),
path(
    "internal/jobs/<int:job_id>/",
    views.InternalJobDetailView.as_view(),
    name="internal-job-detail"
),
path(
    "internal/jobs/<int:job_id>/status/",
    InternalJobStatusUpdateView.as_view()
),
path(
    "jobs/<int:job_id>/submit/",
    SubmitJobView.as_view(),
    name="submit-job"
),

path(
    "jobs/<int:job_id>/complete/",
    CompleteJobView.as_view(),
    name="complete-job"
),

    path(
        "internal/jobs/",
        InternalJobListView.as_view()
    ),

    path(
        "internal/jobs/stats/",
        InternalJobStatsView.as_view()
    ),
]
