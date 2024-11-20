import json
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .models import Product
from django.core.exceptions import ValidationError


@csrf_exempt
def product_list(request):
    if request.method == 'GET':
        products = list(Product.objects.values('id', 'name', 'price', 'available'))
        return JsonResponse(products, safe=False)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format.")

        name = data.get('name')
        price = data.get('price')
        available = data.get('available')

        if name is None or price is None or available is None:
            return HttpResponseBadRequest("Missing required fields: name, price, or available.")

        try:
            product = Product(name=name, price=Decimal(str(price)), available=available)
            product.full_clean()
            product.save()
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'available': product.available,
            }, status=201)
        except ValidationError as e:
            return HttpResponseBadRequest(f"Validation error: {e.message_dict}")
    else:
        return HttpResponseBadRequest("Unsupported HTTP method for this endpoint.")


@csrf_exempt
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return HttpResponseNotFound(f"Product with ID {product_id} does not exist.")

    if request.method == 'GET':
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'available': product.available,
        })
    else:
        return HttpResponseBadRequest("Unsupported HTTP method for this endpoint.")
