from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_and_predict, name='upload'),
    path('prediction/<int:prediction_id>/', views.prediction_detail, name='prediction_detail'),
    path('capture/', views.capture_and_predict, name='capture_and_predict'),
    # path('feedback/', views.feedback, name='feedback'),

]
