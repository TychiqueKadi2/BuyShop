# trade/signals.py
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.utils import timezone
from datetime import timedelta

def setup_periodic_tasks(sender, **kwargs):
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.MINUTES,
    )

    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Check expired bids',
        task='trade.tasks.check_expired_bids',
        defaults={
            'expires': timezone.now() + timedelta(days=1),
        },
    )
