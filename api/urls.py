from api.views import delivery_fee_calculator
from django.urls import path, include

app_name = "fee_calculator"
urlpatterns = [
    path('fee_calculator/', delivery_fee_calculator, name='fee_calculator'),
]
