from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import MeSerializer


def index(request):
    return HttpResponse("Accounts index")


@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def me_api(request):
    if request.method == 'GET':
        s = MeSerializer(request.user)
        return JsonResponse(s.data, safe=False)
    s = MeSerializer(instance=request.user, data=request.data, partial=True)
    s.is_valid(raise_exception=True)
    s.save()
    return JsonResponse(s.data, safe=False)