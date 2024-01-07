from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import manage_item, manage_items

urlpatterns = {
    path("", manage_items, name="items"),
    path("<slug:key>", manage_item, name="single_item"),
}
urlpatterns = format_suffix_patterns(urlpatterns)
