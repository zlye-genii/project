from django.urls import path, include

from . import views

urlpatterns = [
    path('user/data/', views.get_user_data),
    path('user/', include('dj_rest_auth.urls')),
    path('user/registration/', include('dj_rest_auth.registration.urls'))
]