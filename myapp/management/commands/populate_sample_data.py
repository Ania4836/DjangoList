from django.core.management.base import BaseCommand
from myapp.models import Product, Customer, Order


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Order.objects.all().delete()

        product1 = Product.objects.create(name='Laptop', price=999.99, available=True)
        product2 = Product.objects.create(name='Smartphone', price=499.99, available=False)
        product3 = Product.objects.create(name='Headphones', price=49.99, available=True)

        customer1 = Customer.objects.create(name='John Doe', address='123 Main Street')
        customer2 = Customer.objects.create(name='Jane Smith', address='456 Elm Street')

        order1 = Order.objects.create(customer=customer1, status='New')
        order1.products.add(product1, product3)

        order2 = Order.objects.create(customer=customer2, status='In Process')
        order2.products.add(product2)

        order3 = Order.objects.create(customer=customer1, status='Completed')
        order3.products.add(product3)

        self.stdout.write("Sample data created successfully.")

