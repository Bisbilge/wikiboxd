from .models import Category

def navbar_categories(request):
    categories = Category.objects.filter(parent=None).prefetch_related('subcategories')
    return {'navbar_categories': categories}
