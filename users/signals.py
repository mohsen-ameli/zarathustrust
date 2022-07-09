from .models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import random, string

@receiver(post_save, sender=CustomUser)
def post_save_generate_code(sender, instance, created, *args, **kwargs):
    if created:
        code_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        CustomUser.objects.filter(username=instance.username).update(referral_code=code_string)