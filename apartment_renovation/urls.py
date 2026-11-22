from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

handler404 = "homepage.views.page_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path('rooms/', include('rooms.urls')),
    path("estimates/", include("estimates.urls"))
]


if settings.DEBUG_TOOLBAR_ENABLED:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
