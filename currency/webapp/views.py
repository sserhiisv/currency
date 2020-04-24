import requests

from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from datetime import datetime, timedelta
from os.path import join

from currency.settings import NBU_API_URL


class LoginView(TemplateView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        return reverse('webapp:home')


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')

    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name = 'main.html'


class ExchangeRate:
    def get_exchange_rate(self):
        curr_date = datetime.today().strftime('%Y%m%d')
        api_url = join(NBU_API_URL, f'?date={curr_date}&json')

        response = requests.get(api_url)
        data = response.json()
        return data


@method_decorator(login_required, name='dispatch')
class ExchangeRateView(TemplateView, ExchangeRate):
    template_name = 'er_by_date.html'

    def get(self, request):
        data = self.get_exchange_rate()
        return render(request, 'er_by_date.html', {'data': data})


class ExchangeRateApiView(APIView, ExchangeRate):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = self.get_exchange_rate()
        return Response({'items': data}, status=200)


class HistoryRate:
    def get_currencies(self):
        response = requests.get(join(NBU_API_URL, '?json'))
        currencies = [el.get('cc') for el in response.json()]
        return currencies

    def get_history_data(self, currency, daterange):
        date_start = datetime.strptime(
            daterange.split('-')[0].strip(),
            "%m/%d/%Y"
        )
        date_end = datetime.strptime(
            daterange.split('-')[1].strip(),
            "%m/%d/%Y"
        )

        if (date_end-date_start).days == 0:
            daterange = [date_start]
        else:
            daterange = [
                date_start + timedelta(days=x)
                for x in range(0, (date_end-date_start).days)
            ]

        data = self.request_history_data(currency, daterange)
        currencies = self.get_currencies()

        return {
            'data': data,
            'currency': currency,
            'currencies': currencies
        }

    def request_history_data(self, currency, daterange):
        data = []
        for date in daterange:
            print(join(
                NBU_API_URL,
                f'?date={date.strftime("%Y%m%d")}&valcode={currency}&json'
            ))
            response = requests.get(join(
                NBU_API_URL,
                f'?date={date.strftime("%Y%m%d")}&valcode={currency}&json'
            ))
            value = response.json()
            if value:
                data.append(value[0])
        return data


@method_decorator(login_required, name='dispatch')
class HistoryRateView(TemplateView, HistoryRate):
    template_name = 'history_rate.html'

    def get(self, request):
        currencies = self.get_currencies()
        return render(request, 'history_rate.html', {'currencies': currencies})

    def post(self, request):
        currency = request.POST.get('currency')
        data = self.get_history_data(currency, request.POST.get('daterange'))
        return render(request, 'history_rate.html', data)


class HistoryRateApiView(APIView, HistoryRate):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        currency = request.POST.get('currency')
        data = self.get_history_data(currency, request.POST.get('daterange'))
        return Response({'items': data['data']}, status=200)
