"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from .swagger import schema_view 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('auth_app.urls')), 
    path("",include('children.urls')),
    path("",include('meals.urls')),
    path("",include('hygiene.urls')),
    path("",include('naps.urls')),
    path("",include('activities.urls')),
    path("",include('mood.urls')),
    path("",include('posts.urls')),
    path("",include('notifications.urls')),
    path("",include('comments.urls')),
    path('', include('kindergarten.urls')),
    path('', include('analytics.urls')),
    path('attendance/', include('attendance.urls')), 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)