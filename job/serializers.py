from .models import Job
from rest_framework import serializers

class MyJobSeralizer(serializers.ModelSerializer):

    class Meta:
        model=Job
        fields="__all__"

class InternalJobListSerializer(serializers.ModelSerializer):

    class Meta:

        model = Job

        fields = [
            "id",
            "title",
            "client_id",
            "budget_min",
            "budget_max",
            "status",
            "created_at",
        ]