from unittest import signals
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = 'accounts'

    def ready(self):
        import accounts.signals
