from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KindergartenViewSet, AttachAdminView, DetachAdminView, ClassView, TeacherClassViewSet,TeacherViewSet

router = DefaultRouter()
router.register(r'kindergarten', KindergartenViewSet, basename='kindergarten')
router.register(r'teacher-classes', TeacherClassViewSet, basename='teacher-classes')
router.register(r'teachers', TeacherViewSet, basename='teachers')

urlpatterns = [
    path('kindergarten/attach-admin/', AttachAdminView.as_view(), name='attach_admin'),
    path('kindergarten/detach-admin/', DetachAdminView.as_view(), name='detach_admin'),
    path('kindergarten/classes/', ClassView.as_view(), name='classes'),
    path('', include(router.urls)),
]