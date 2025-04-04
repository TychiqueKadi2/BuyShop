from .models import DeviceInfo
from django.utils.timezone import now
from user_agents import parse

class DeviceInfoMiddleware:
    """
    Middleware to extract device information from user requests and save it to the database.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract device information
        ip = self.get_client_ip(request)
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)

        # Determine device type
        if user_agent.is_mobile:
            device_type = "Mobile"
        elif user_agent.is_tablet:
            device_type = "Tablet"
        elif user_agent.is_pc:
            device_type = "Desktop"
        else:
            device_type = "Other"

        # Save device info to the database
        DeviceInfo.objects.create(
            device_type=device_type,
            ip=ip,
            browser=user_agent.browser.family,
            os_version=user_agent.os.family + " " + user_agent.os.version_string,
        )

        # Proceed with the request
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """
        Extract the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
