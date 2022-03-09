from __future__ import absolute_import, unicode_literals
from .models import account_interest
from time import sleep
from celery import shared_task


@shared_task()  # bind = True
def interest_loop():
    ### celery -A money_moe worker -l info --pool=solo
    while True:
        for each in account_interest.objects.all():
            total_balance = float(each.interest)
            if total_balance != 0:
                b = float(each.interest_rate)
                interest_ = total_balance * 0.01 / 525600  # 3153600
                b = b + interest_
                each.interest_rate = b
                each.save()
        sleep(60)
