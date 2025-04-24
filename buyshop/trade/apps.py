# trade/apps.py
from django.apps import AppConfig

class TradeConfig(AppConfig):
    name = 'trade'

    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import setup_periodic_tasks  # You'll create this

        post_migrate.connect(setup_periodic_tasks, sender=self)
