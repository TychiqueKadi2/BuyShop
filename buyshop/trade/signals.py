from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta
from django.utils import timezone

def setup_periodic_tasks(sender, **kwargs):
    # Create or get the interval schedule
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1,  # interval in minutes
        period=IntervalSchedule.MINUTES,
    )

    # Try to get an existing periodic task by name
    task_name = 'Check expired bids'
    task, created = PeriodicTask.objects.get_or_create(
        name=task_name,
        defaults={
            'interval': schedule,
            'task': 'trade.tasks.check_expired_bids',
            'expires': timezone.now() + timedelta(days=1),  # Set expiration date
        },
    )

    if not created:
        # If the task already exists, update the expiration time (or any other fields you need to update)
        task.expires = timezone.now() + timedelta(days=1)
        task.save()
        print(f"Updated task: {task_name}")
    else:
        print(f"Created new task: {task_name}")
