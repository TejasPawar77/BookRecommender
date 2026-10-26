from django.urls import path
from .views import AdminProfileView

urlpatterns = [
  path("me/", AdminProfileView.as_view(), name="admin-profile")
]