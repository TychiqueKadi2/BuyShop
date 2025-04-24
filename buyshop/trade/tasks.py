# trade/tasks.py
from celery import shared_task
from trade.utils import mark_expired_bids

@shared_task
def check_expired_bids():
    mark_expired_bids()
