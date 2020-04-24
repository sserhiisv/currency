"""currency URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.contrib.auth import views as auth_views

from webapp.views import (
    SignUpView, HomeView, ExchangeRateView, HistoryRateView, ExchangeRateApiView,
    HistoryRateApiView
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),

    path('', HomeView.as_view(), name='home'),
    path('exchange_rate/', ExchangeRateView.as_view(), name='exchange_rate'),
    path('history_rate/', HistoryRateView.as_view(), name='history_rate'),

    path(r'api/v1/', include([
        path(r'exchange_rate/', ExchangeRateApiView.as_view(),
            name="exchange_rate_api"),
        path(r'history_rate/', HistoryRateApiView.as_view(),
            name="history_rate_api")
    ])),
]
