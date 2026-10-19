from django.urls import path
from .views import recommend_books_api

urlpatterns = [
  path('recommend/', recommend_books_api, name='recommend_books'),
]