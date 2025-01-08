from django.test import TestCase
from myapp.models import Product, Customer, Order
from django.core.exceptions import ValidationError


class ProductModelExtendedTest(TestCase):
    def test_create_product_with_valid_data(self):
        product = Product.objects.create(name="Valid Product", price=10.00, available=True)
        self.assertEqual(product.name, "Valid Product")
        self.assertEqual(product.price, 10.00)
        self.assertTrue(product.available)

    def test_create_product_missing_name(self):
        with self.assertRaises(ValidationError):
            product = Product(name=None, price=10.00, available=True)
            product.full_clean()

    def test_create_product_blank_name(self):
        with self.assertRaises(ValidationError):
            product = Product(name="", price=10.00, available=True)
            product.full_clean()

    def test_create_product_missing_price(self):
        with self.assertRaises(ValidationError):
            product = Product(name="No Price", price=None, available=True)
            product.full_clean()

    def test_create_product_missing_available(self):
        product = Product.objects.create(name="No Available Field", price=10.00)
        self.assertEqual(product.name, "No Available Field")
        self.assertEqual(product.price, 10.00)
        self.assertTrue(product.available)  # Default value should be True

    def test_create_product_with_long_name(self):
        long_name = "A" * 255
        product = Product.objects.create(name=long_name, price=20.00, available=True)
        self.assertEqual(product.name, long_name)

    def test_create_product_with_exceedingly_long_name(self):
        long_name = "A" * 256
        with self.assertRaises(ValidationError):
            product = Product(name=long_name, price=20.00, available=True)
            product.full_clean()

    def test_create_product_with_zero_price(self):
        with self.assertRaises(ValidationError):
            product = Product(name="Zero Price", price=0.00, available=True)
            product.full_clean()

    def test_create_product_with_negative_price(self):
        with self.assertRaises(ValidationError):
            product = Product(name="Negative Price", price=-5.00, available=True)
            product.full_clean()

    def test_create_product_with_exceeding_max_price(self):
        max_price = 10**8  # Assuming a logical threshold for maximum price
        with self.assertRaises(ValidationError):
            product = Product(name="Exceeding Max Price", price=max_price, available=True)
            product.full_clean()

    def test_create_product_with_high_price_edge(self):
        high_price = 99999999.99  # Maximum allowed for 10 digits and 2 decimals
        product = Product.objects.create(name="High Price", price=high_price, available=True)
        self.assertEqual(product.price, high_price)

    def test_create_product_with_invalid_price_format(self):
        with self.assertRaises(ValidationError):
            product = Product(name="Invalid Price Format", price=10.123, available=True)
            product.full_clean()

    def test_create_product_with_minimal_valid_price(self):
        product = Product.objects.create(name="Minimal Valid Price", price=0.01, available=True)
        self.assertEqual(product.price, 0.01)

    def test_create_product_with_non_numeric_price(self):
        with self.assertRaises(ValidationError):
            product = Product(name="Non-Numeric Price", price="Ten Dollars", available=True)
            product.full_clean()

    def test_create_product_with_null_fields(self):
        with self.assertRaises(ValidationError):
            product = Product(name=None, price=None, available=None)
            product.full_clean()

    def test_product_str_representation(self):
        product = Product.objects.create(name="Test Product", price=50.00, available=True)
        self.assertEqual(str(product), "Test Product")


class CustomerModelTest(TestCase):
    def test_create_customer_with_valid_data(self):
        customer = Customer.objects.create(name="John Doe", address="123 Main St")
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.address, "123 Main St")

    def test_create_customer_missing_name(self):
        with self.assertRaises(ValidationError):
            customer = Customer(name=None, address="123 Main St")
            customer.full_clean()

    def test_create_customer_blank_name(self):
        with self.assertRaises(ValidationError):
            customer = Customer(name="", address="123 Main St")
            customer.full_clean()

    def test_create_customer_with_long_name(self):
        long_name = "A" * 101
        with self.assertRaises(ValidationError):
            customer = Customer(name=long_name, address="123 Main St")
            customer.full_clean()

    def test_create_customer_missing_address(self):
        with self.assertRaises(ValidationError):
            customer = Customer(name="John Doe", address=None)
            customer.full_clean()

    def test_customer_str_representation(self):
        customer = Customer.objects.create(name="John Doe", address="123 Main St")
        self.assertEqual(str(customer), "John Doe")


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer", address="123 Main St")
        self.product1 = Product.objects.create(name="Product 1", price=10.00, available=True)
        self.product2 = Product.objects.create(name="Product 2", price=15.00, available=False)

    def test_create_order_with_valid_data(self):
        order = Order.objects.create(customer=self.customer, status="New")
        order.products.add(self.product1, self.product2)
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, "New")
        self.assertIn(self.product1, order.products.all())
        self.assertIn(self.product2, order.products.all())

    def test_create_order_missing_customer(self):
        with self.assertRaises(ValidationError):
            order = Order(status="New")
            order.full_clean()

    def test_create_order_invalid_status(self):
        with self.assertRaises(ValidationError):
            order = Order(customer=self.customer, status="Invalid Status")
            order.full_clean()

    def test_total_price_with_products(self):
        order = Order.objects.create(customer=self.customer, status="New")
        order.products.add(self.product1, self.product2)
        self.assertEqual(order.total_price(), 25.00)

    def test_total_price_without_products(self):
        order = Order.objects.create(customer=self.customer, status="New")
        self.assertEqual(order.total_price(), 0.00)

    def test_can_fulfill_with_available_products(self):
        order = Order.objects.create(customer=self.customer, status="New")
        order.products.add(self.product1)
        self.assertTrue(order.can_fulfill())

    def test_can_fulfill_with_unavailable_products(self):
        order = Order.objects.create(customer=self.customer, status="New")
        order.products.add(self.product2)
        self.assertFalse(order.can_fulfill())