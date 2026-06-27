import requests
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from labora_shared.notification_client import send_notification
from .role_permissions import IsFreelancer
from .models import Job
from .serializers import MyJobSeralizer, InternalJobListSerializer
from django.conf import settings
from .authentication import (
    client_only,
    freelancer_only,
    admin_only,
    role_required
)
from .permissions.internal_service import (
    IsInternalService
)
from django.core.paginator import Paginator

# ================================
# CREATE JOB
# ================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@client_only
def create_job(request):

    try:
        # Get user id from JWT token
        client_id = request.user.id

        if not client_id:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Copy request data
        data = request.data.copy()

        # Automatically attach client id
        data["client_id"] = client_id

        serializer = MyJobSeralizer(data=data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ================================
# CLIENT JOBS
# ================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@client_only
def client_jobs(request):

    try:
        client_id = request.user.id

        jobs = Job.objects.filter(
            client_id=client_id
        ).order_by("-created_at")

        serializer = MyJobSeralizer(
            jobs,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ================================
# BROWSE JOBS
# ================================
from django.core.paginator import Paginator

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsFreelancer])

def browse_jobs(request):
    try:
        jobs = Job.objects.filter(
            status="open"
        ).order_by("-created_at")

        keyword = request.query_params.get("q")

        if keyword:
            jobs = jobs.filter(
                title__icontains=keyword
            )

        if not jobs.exists():
            return Response(
                {"message": "No jobs found matching your search."},
                status=status.HTTP_200_OK
            )

        page = request.query_params.get("page", 1)

        paginator = Paginator(jobs, 5)

        page_obj = paginator.get_page(page)

        serializer = MyJobSeralizer(
            page_obj,
            many=True
        )

        return Response({
            "total_jobs": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "jobs": serializer.data
        })

    except Exception as e:
        return Response(
            {
                "error": "Something went wrong.",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# JOB DETAIL
# ================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(["client", "freelancer", "labora_admin"])
def job_detail(request, job_id):

    try:
        job = get_object_or_404(
            Job,
            id=job_id
        )

        serializer = MyJobSeralizer(job)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ================================
# DELETE JOB
# ================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@admin_only
def delete_job(request, job_id):

    try:
        job = get_object_or_404(
            Job,
            id=job_id
        )

        job.delete()

        return Response(
            {"message": "Job deleted successfully"},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



# job/bbbb.py

class JobChatAccessView(APIView):

    authentication_classes = []

    permission_classes = [
        IsInternalService
    ]

    def get(
        self,
        request,
        job_id
    ):

        user_id = request.GET.get(
            "user_id"
        )

        if not user_id:
            return Response(
                {
                    "error":
                    "user_id required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            job = Job.objects.get(
                id=job_id
            )

        except Job.DoesNotExist:
            return Response(
                {
                    "allowed": False
                },
                status=status.HTTP_404_NOT_FOUND
            )

        user_id = int(user_id)

        allowed = (
            job.client_id == user_id
            or
            job.accepted_freelancer_id
            == user_id
        )

        return Response(
            {
                "allowed": allowed
            }
        )

@api_view(["GET"])
@permission_classes([IsInternalService])
def internal_job_detail(request, job_id):

    try:

        job = Job.objects.get(
            id=job_id
        )

    except Job.DoesNotExist:

        return Response(
            {
                "error": "Job not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            "id": job.id,
            "client_id": job.client_id,
            "freelancer_id": getattr(
                job,
                "freelancer_id",
                None
            ),
            "status": job.status
        }
    )


class InternalJobDetailView(APIView):
    authentication_classes = []
    permission_classes = [IsInternalService]

    def get(self, request, job_id):
        try:

            job = Job.objects.get(
                id=job_id
            )

        except Job.DoesNotExist:

            return Response(
                {
                    "error": "Job not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        freelancer_id = None

        try:

            response = requests.get(
                f"{settings.APPLICATION_SERVICE_URL}/api/internal/jobs/{job_id}/freelancer/",
                headers={
                    "X-Service-Key": settings.SERVICE_API_KEY
                },
                timeout=5
            )

            if response.status_code == 200:

                freelancer_id = response.json().get(
                    "freelancer_id"
                )

        except requests.RequestException:
            pass

        return Response(
            {
                "id": job.id,
                "client_id": job.client_id,
                "freelancer_id": freelancer_id,
                "status": job.status
            }
        )
class InternalJobStatusUpdateView(APIView):

    authentication_classes = []
    permission_classes = [IsInternalService]

    def patch(self, request, job_id):

        try:
            job = Job.objects.get(
                id=job_id
            )

        except Job.DoesNotExist:
            return Response(
                {
                    "error": "Job not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {
                    "error": "status is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        job.status = new_status
        job.save()

        # Send notification when job is completed
        if new_status == "completed":

            freelancer_id = None

            try:
                response = requests.get(
                    f"{settings.APPLICATION_SERVICE_URL}"
                    f"/api/internal/jobs/{job_id}/freelancer/",
                    headers={
                        "X-Service-Key": settings.SERVICE_API_KEY
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    freelancer_id = response.json().get(
                        "freelancer_id"
                    )

            except requests.RequestException:
                pass

            if freelancer_id:

                try:
                    requests.post(
                        f"{settings.NOTIFICATION_SERVICE_URL}"
                        "/api/internal/notifications/create/",
                        headers={
                            "X-Service-Key": settings.SERVICE_API_KEY
                        },
                        json={
                            "user_id": freelancer_id,
                            "type": "job_completed",
                            "title": "Job Completed",
                            "message": (
                                "The client has marked your work as completed."
                            )
                        },
                        timeout=5
                    )

                except requests.RequestException:
                    pass

        return Response(
            {
                "message": "Job status updated successfully",
                "status": job.status
            },
            status=status.HTTP_200_OK
        )
class SubmitJobView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, job_id):

        try:
            job = Job.objects.get(id=job_id)

        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if job.status != "in_progress":
            return Response(
                {
                    "error":
                    "Only in_progress jobs can be submitted"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        job.status = "submitted"
        job.save()

        send_notification(
            user_id=job.client_id,
            notification_type="work_submitted",
            title="Work Submitted",
            message="The freelancer has submitted the work for review."
        )

        return Response(
            {
                "message": "Work submitted successfully",
                "status": job.status
            }
        )

class CompleteJobView(APIView):

        permission_classes = [IsAuthenticated]

        def patch(self, request, job_id):

            try:
                job = Job.objects.get(id=job_id)

            except Job.DoesNotExist:

                return Response(
                    {"error": "Job not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if job.client_id != request.user.id:
                return Response(
                    {
                        "error":
                            "Only the client can complete the job"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            if job.status != "submitted":
                return Response(
                    {
                        "error":
                            "Only submitted jobs can be completed"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            job.status = "completed"
            job.save()

            freelancer_id = None

            try:

                response = requests.get(
                    f"{settings.APPLICATION_SERVICE_URL}"
                    f"/api/internal/jobs/{job_id}/freelancer/",
                    headers={
                        "X-Service-Key":
                            settings.SERVICE_API_KEY
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    freelancer_id = response.json().get(
                        "freelancer_id"
                    )

            except requests.RequestException:
                pass

            if freelancer_id:
                send_notification(
                    user_id=freelancer_id,
                    notification_type="job_completed",
                    title="Job Completed 🎉",
                    message=(
                        "Congratulations! "
                        "The client approved your work "
                        "and marked the job as completed."
                    )
                )

            return Response(
                {
                    "message": "Job completed successfully",
                    "status": job.status
                }
            )


class InternalJobListView(APIView):
    authentication_classes = []

    permission_classes = [IsInternalService]

    def get(self, request):

        jobs = Job.objects.all().order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 20

        page = paginator.paginate_queryset(
            jobs,
            request
        )

        serializer = InternalJobListSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class InternalJobStatsView(APIView):
    authentication_classes = []

    permission_classes = [IsInternalService]

    def get(self, request):

        return Response({

            "total_jobs": Job.objects.count(),

            "open_jobs": Job.objects.filter(
                status="open"
            ).count(),

            "in_progress_jobs": Job.objects.filter(
                status="in_progress"
            ).count(),

            "completed_jobs": Job.objects.filter(
                status="completed"
            ).count(),

            "cancelled_jobs": Job.objects.filter(
                status="cancelled"
            ).count(),

        })



class InternalJobDetailViewAdmin(APIView):

    authentication_classes = []
    permission_classes = [IsInternalService]

    def get(
            self,
            request,
            job_id
    ):

        try:

            job = Job.objects.get(
                pk=job_id
            )

        except Job.DoesNotExist:

            return Response(
                {
                    "error": "Job not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = InternalJobListSerializer(job)

        return Response(
            serializer.data
        )