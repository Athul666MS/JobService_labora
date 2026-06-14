from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Job
from .serializers import MyJobSeralizer

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
        print(client_id)

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
@permission_classes([IsAuthenticated])
@freelancer_only
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
@role_required(["client", "freelancer", "admin"])
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



# job/views.py

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