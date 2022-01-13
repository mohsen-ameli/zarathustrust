from .models import ReferralCode, CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def post_save_generate_code(sender, instance, created, *args, **kwargs):
    if created:
        ReferralCode.objects.create(user=instance)

# signal to create a account, right after a user is created
# @receiver(post_save, sender=CustomUser)
# def user_created_handler(sender, created, instance, *args, **kwargs):
#     if created:
#         account.objects.create(created_by=instance, total_balance=0)