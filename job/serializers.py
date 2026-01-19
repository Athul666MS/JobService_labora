from .models import Job
from rest_framework import serializers

class MyJobSeralizer(serializers.ModelSerializer):

    class Meta:
        model=Job
        fields="__all__"