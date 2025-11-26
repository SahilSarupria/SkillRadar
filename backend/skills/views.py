from django.http import HttpResponse
from requests import request

# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import JobRole
from rest_framework import generics

@api_view(["GET"])
@permission_classes([AllowAny])
def get_goal(request, job_role_id):
    try:
        role = JobRole.objects.get(id=job_role_id)
    except JobRole.DoesNotExist:
        return Response({"error": "Job role not found"}, status=404)

    return Response({
        "required_skills": list(role.required_skills.values_list("name", flat=True)),
        "min_experience_years": role.min_experience_years,
        "weight_skills": role.weight_skills,
    })

from .serializers import JobRoleSerializer
from rest_framework.permissions import AllowAny

class JobRoleListView(generics.ListAPIView):
    queryset = JobRole.objects.filter(is_active=True)
    serializer_class = JobRoleSerializer
    permission_classes = [AllowAny]  # 👈 Add this
