from django.db import models
from django.core.exceptions import ValidationError


def validate_positive(value):
    if value <= 0:
        raise ValidationError("Price must be a positive value.")


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[validate_positive])
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Process', 'In Process'),
        ('Sent', 'Sent'),
        ('Completed', 'Completed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    def total_price(self):
        return sum(product.price for product in self.products.all())

    def can_fulfill(self):
        return all(product.available for product in self.products.all())
