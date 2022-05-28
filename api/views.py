from accounts.models import account, account_interest
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.response import Response
from users.models import CustomUser

from .serializers import AccountSerializer, UserSerializer, CustomUserSerializer, InterestSerializer

# Create your views here.

class AccountsApi(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = account.objects.all()


class InterestApi(viewsets.ModelViewSet):
    serializer_class = InterestSerializer
    queryset = account_interest.objects.all()


class UsersApi(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


@api_view(['GET'])
def current_user(request):
    try:
        user = CustomUser.objects.get(pk=request.user.pk)
    except:
        user = None
    serializer = CustomUserSerializer(instance=user, many=False)
    return Response(serializer.data)
        