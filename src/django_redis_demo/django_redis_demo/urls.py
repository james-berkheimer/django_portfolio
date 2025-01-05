from api.views import ItemsView, home  # added home import
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("items/", ItemsView.as_view(), name="items"),  # URL pattern for all items
    path("items/<str:key>/", ItemsView.as_view(), name="item"),  # URL pattern for individual item
    path("", home, name="home"),  # corrected this line
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
