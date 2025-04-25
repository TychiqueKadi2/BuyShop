from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return HttpResponse("Welcome to the BuyShop API!")

# Define the schema view for Swagger UI
schema_view = get_schema_view(
    openapi.Info(
        title="BuyShop API Documentation",
        default_version="v1",
        description=(
            "Welcome to the BuyShop API documentation! This API is designed to support an online cash "
            "converter platform where individuals can list their used products for sale. It includes features "
            "such as user authentication, KYC updates, and more."
        ),
        terms_of_service="https://www.buyshop.com/terms/",
        contact=openapi.Contact(email="support@buyshop.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Apply csrf_exempt to the schema view
swagger_view = csrf_exempt(schema_view.with_ui("swagger", cache_timeout=0))
redoc_view = csrf_exempt(schema_view.with_ui("redoc", cache_timeout=0))
schema_json_view = csrf_exempt(schema_view.without_ui(cache_timeout=0))

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),  # Home page
    path("swagger/", swagger_view, name="swagger-ui"),
    path("redoc/", redoc_view, name="schema-redoc"),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_json_view, name="schema-json"),
    path("auth/", include("authentication.urls")),  # Auth views
    path("trade/", include("trade.urls")),  # Trade views
    path("product/", include("product.urls")), # Product views
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)