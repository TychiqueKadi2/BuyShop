from django.db import models
import uuid
from django.conf import settings

# Create your models here.
class DeviceInfo(models.Model):
    """
    Model representing device information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_info', null=True)
    device_type = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    browser = models.CharField(max_length=50)
    os_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Device {self.id} - {self.browser}"