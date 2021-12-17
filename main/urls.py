from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kvint.urls')),
    path('api/', include('kvint.api.urls')),
]
