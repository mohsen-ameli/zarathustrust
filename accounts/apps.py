from unittest import signals
from django.apps import AppConfig
from stripe import Account


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = 'accounts'

    def ready(self):
        import accounts.signals
