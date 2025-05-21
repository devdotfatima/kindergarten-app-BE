from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChildrenViewSet,TeacherClassesView,ClassChildrenView

router = DefaultRouter()
router.register(r'children', ChildrenViewSet, basename='children')

urlpatterns = [
    path('', include(router.urls)),  
   
    path("classes/teachers", TeacherClassesView.as_view(), name="teacher-classes"),
    path("classes/<int:class_id>/children/", ClassChildrenView.as_view(), name="class-children"),

]