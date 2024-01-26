from django.db import models


# Create your models here.
class ShoppingCart(models.Model):
    cart_value = models.IntegerField()
    delivery_distance = models.IntegerField()
    number_of_items = models.IntegerField()
    time = models.DateTimeField()
