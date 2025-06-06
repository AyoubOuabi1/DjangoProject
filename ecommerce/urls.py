# ecommerce/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('shop.urls', namespace='shop')),
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)