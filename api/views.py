from accounts.models import account, account_interest
from users.models import CustomUser
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import CustomUser
from django.core.mail import send_mail
import os, json

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


@api_view(['GET'])
def countries(request):
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = f'{project}/json/currencies.json' # getting the file containing all country codes

    with open(file, 'r') as json_currency: # opening and reading the json file
        data = json.load(json_currency)

    # try:
    #     user = CustomUser.objects.get(pk=request.user.pk)
    # except:
    #     user = None
    # serializer = CustomUserSerializer(instance=user, many=False)
    return Response(data)


@api_view(['POST'])
def deposit(request, pk):
    user = CustomUser.objects.get(pk=pk)

    with open('/etc/config.json') as config_file:
        config = json.load(config_file)

    symbol = request.data['symbol']
    amount = request.data['amount']
    EMAIL_ID        = config.get('EMAIL_ID')
    EMAIL_ID_MAIN   = config.get('EMAIL_ID_MAIN')

    send_mail(f'{pk}', 
            f'{user.username} with account number : {pk} has requested to deposit {symbol}{amount}',
            f'{EMAIL_ID}',
            [f'{EMAIL_ID_MAIN}'],)

    account.objects.filter(pk=pk).update(add_money=0)
    
    return Response()
