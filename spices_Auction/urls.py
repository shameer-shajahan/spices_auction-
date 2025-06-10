from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adminapi/', include("adminapi.urls")),
    path('', include("userapi.urls")),
    path('store/', include('store.urls')),
    path('delivery_app/', include('delivery_app.urls')),  # app URLs
]

# Serve media files only during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
