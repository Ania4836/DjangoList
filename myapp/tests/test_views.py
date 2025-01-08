from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from myapp.models import Product


class ProductApiTest(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Temporary Product', price=1.99, available=True)
        self.product_list_url = reverse('product-list')
        self.product_detail_url = reverse('product-detail', kwargs={'pk': self.product.id})
        self.invalid_product_detail_url = reverse('product-detail', kwargs={'pk': 999})
        self.client = APIClient()
        self.regular_user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='testadmin', password='testpassword')

    def authenticate_regular_user(self):
        token = str(AccessToken.for_user(self.regular_user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def authenticate_admin_user(self):
        token = str(AccessToken.for_user(self.admin))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_get_all_products_as_regular_user(self):
        self.authenticate_regular_user()
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_all_products_as_admin(self):
        self.authenticate_admin_user()
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_product_as_regular_user(self):
        self.authenticate_regular_user()
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_product_as_admin(self):
        self.authenticate_admin_user()
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_product_as_regular_user(self):
        self.authenticate_regular_user()
        response = self.client.get(self.invalid_product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_invalid_product_as_admin(self):
        self.authenticate_admin_user()
        response = self.client.get(self.invalid_product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product_as_regular_user(self):
        self.authenticate_regular_user()
        data = {"name": "New Product", "price": 10.99, "available": True}
        response = self.client.post(self.product_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_as_admin(self):
        self.authenticate_admin_user()
        data = {"name": "New Product", "price": 10.99, "available": True}
        response = self.client.post(self.product_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_with_invalid_data_as_admin(self):
        self.authenticate_admin_user()
        invalid_data = {"name": "", "price": -5, "available": "not_boolean"}
        response = self.client.post(self.product_list_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_invalid_data_as_regular_user(self):
        self.authenticate_regular_user()
        invalid_data = {"name": "", "price": -5, "available": "not_boolean"}
        response = self.client.post(self.product_list_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_modify_product_as_regular_user(self):
        self.authenticate_regular_user()
        data = {"name": "Modified Product"}
        response = self.client.patch(self.product_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_modify_product_as_admin(self):
        self.authenticate_admin_user()
        data = {"name": "Modified Product"}
        response = self.client.patch(self.product_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Modified Product')

    def test_modify_product_with_invalid_data_as_admin(self):
        self.authenticate_admin_user()
        invalid_data = {"price": -10}
        response = self.client.patch(self.product_detail_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_modify_product_with_invalid_data_as_regular_user(self):
        self.authenticate_regular_user()
        invalid_data = {"price": -10}
        response = self.client.patch(self.product_detail_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_as_regular_user(self):
        self.authenticate_regular_user()
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_as_admin(self):
        self.authenticate_admin_user()
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_invalid_product_as_admin(self):
        self.authenticate_admin_user()
        response = self.client.delete(self.invalid_product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_invalid_product_as_regular_user(self):
        self.authenticate_regular_user()
        response = self.client.delete(self.invalid_product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_without_authentication(self):
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(self.product_list_url, {"name": "Unauthorized"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.product_detail_url, {"name": "Unauthorized"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_invalid_endpoint(self):
        response = self.client.get('/invalid-endpoint/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
