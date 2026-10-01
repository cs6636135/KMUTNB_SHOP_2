from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product, Location, Stock

def home_view(request):
    categories = Category.objects.all()
    featured_products = Product.objects.select_related('category').prefetch_related('stocks__location')[:8]
    locations = Location.objects.all()
    
    return render(request, 'shop/home.html', {
        'categories': categories,
        'products': featured_products,
        'locations': locations,
    })


def products_view(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    reservable = request.GET.get('reservable', '').strip()

    products = Product.objects.select_related('category').prefetch_related('stocks__location').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)
    if reservable == '1':
        products = products.filter(reservable=True)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': query,
        'reservable_filter': reservable,
    }

    # Support HTMX partial swap for responsive instant search/filter
    if request.headers.get('HX-Request') and not request.headers.get('HX-Boosted'):
        return render(request, 'partials/product_list.html', context)

    return render(request, 'shop/products.html', context)


def product_detail_view(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('stocks__location'),
        id=product_id
    )
    # Available stocks with location details
    stocks = product.stocks.select_related('location').all()
    available_locations = [s.location for s in stocks if s.stock > 0]
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'stocks': stocks,
        'available_locations': available_locations,
        'total_stock': product.total_stock,
    })
