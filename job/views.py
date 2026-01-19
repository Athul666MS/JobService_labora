from .models import Job
from .serializers import MyJobSeralizer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .authentication import (client_only, freelancer_only, admin_only, client_or_admin, freelancer_or_admin,
                             role_required
                             )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@client_only
def create_job(request):
    print(request.data)

    try:
        client_id = request.auth["user_id"]
        print(client_id)

        if not client_id:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        data = request.data
        data["client_id"] = client_id

        serializer = MyJobSeralizer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@client_only
def client_jobs(request):
    try:
        client_id = request.auth.get("user_id")

        jobs = Job.objects.filter(client_id=client_id)
        serializer = MyJobSeralizer(jobs, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@freelancer_only
def browse_jobs(request):
    try:
        jobs = Job.objects.all()

        keyword = request.query_params.get("q")
        if keyword:
            jobs = jobs.filter(title__icontains=keyword)

        serializer = MyJobSeralizer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(["CLIENT", "FREELANCER", "ADMIN"])
def job_detail(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id)
        serializer = MyJobSeralizer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@admin_only
def delete_job(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id)
        job.delete()
        return Response(
            {"message": "Job deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
