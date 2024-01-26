import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

import fastjsonschema

schema = {
    "type": "object",
    "properties": {
        "cart_value": {"type": "integer"},
        "delivery_distance": {"type": "integer"},
        "number_of_items": {"type": "integer", "minimum": 1},
        "time": {"type": "string", "format": "date-time"}
    },
    "required": ["cart_value", "delivery_distance", "number_of_items", "time"]
}
validate = fastjsonschema.compile(schema)


def check_if_friday_rush(time):
    time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    friday_rush_start = time.replace(hour=15, minute=0, second=0)
    friday_rush_end = time.replace(hour=19, minute=0, second=0)

    return friday_rush_start <= time <= friday_rush_end


# Create your views here.
@csrf_exempt
def delivery_fee_calculator(request):
    try:
        json_data = json.loads(request.body.decode('utf-8'))
        validate(json_data)

        cart_value = json_data.get('cart_value')
        delivery_distance = json_data.get('delivery_distance')
        number_of_items = json_data.get('number_of_items')
        time = json_data.get('time')

        defualt_fee = 2000
        additional_fee_per_modulo_500m = 100
        small_order_surcharge_threshold = 1000
        small_order_surcharge_rate = 50
        bulk_fee_threshold = 12
        bulk_fee_rate = 120
        max_delivery_fee = 1500
        free_delivery_threshold = 20000
        friday_rush_multiplier = 1.2
        item_surcharge = 0
        small_order_surcharge = max(0, cart_value - small_order_surcharge_threshold)

        if delivery_distance <= 1000:
            delivery_fee = defualt_fee
        else:
            additional_distance = delivery_distance - 1000
            additional_fee = additional_distance // 500 * additional_fee_per_modulo_500m
            delivery_fee = defualt_fee + min(additional_fee, 1000)

        if number_of_items >= 5:
            item_surcharge = (number_of_items - 4) * small_order_surcharge_rate
            if number_of_items > bulk_fee_threshold:
                item_surcharge += bulk_fee_rate

        total = small_order_surcharge + item_surcharge

        if check_if_friday_rush(time):
            total *= friday_rush_multiplier

        delivery_fee = delivery_fee + total

        # Limit the total delivery fee to the maximum allowed
        delivery_fee = min(delivery_fee, max_delivery_fee)

        # Free delivery if cart value is equal or more than 200€
        if cart_value >= free_delivery_threshold:
            delivery_fee = 0

        # Your actual logic goes here
        result = "delivery Fee Calculated successfully"
        return JsonResponse({"result": result, "delivery_fee": delivery_fee})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
