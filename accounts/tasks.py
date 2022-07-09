from __future__ import absolute_import, unicode_literals
from .models import AccountInterest
from time import sleep
from celery import shared_task


@shared_task()  # bind = True
def interest_loop():
    ### celery -A money_moe worker -l info --pool=solo
    for each in AccountInterest.objects.all():
        total_balance = float(each.interest)
        # if total_balance != 0:
        rate = float(each.interest_rate)
        interest = total_balance * 0.01 / 525600  # 3153600
        rate = rate + interest
        each.interest_rate = format(rate, ".20f")
        each.save()
    sleep(60)
    interest_loop()
