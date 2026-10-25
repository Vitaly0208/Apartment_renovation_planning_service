from django.contrib import admin
from django.urls import path, include

handler404 = "homepage.views.page_not_found"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path('rooms/', include('rooms.urls')),
    path("estimates/", include("estimates.urls"))
]
