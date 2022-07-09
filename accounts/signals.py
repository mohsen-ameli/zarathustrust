from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Account, AccountInterest

# signal to create an AccountInterest, right after an account is created
@receiver(post_save, sender=Account)
def account_created_handler(sender, created, instance, *args, **kwargs):
    if created:
        AccountInterest.objects.create(interest=instance.total_balance, id=instance.pk)

        # Notify us that a new account has been created
        # new_user(instance.created_by)

        # Emailing our business users
        # EMAIL_ID = config.get('EMAIL_ID')
        # print(instance)
        # user = CustomUser.objects.get(pk=instance.pk)
        # email = user.email
        # if user.is_business:
        #     send_mail(instance.created_by.username,
        #                 _(f'WHAT UPP'),
        #                 f'{EMAIL_ID}',
        #                 [f'{email}'],)


@receiver(pre_delete, sender=Account)
def account_delete_hendler(sender, instance, using, *args, **kwargs):
    AccountInterest.objects.get(id=instance.pk).delete()
