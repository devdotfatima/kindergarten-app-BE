from django.db.models import Count, Sum, F
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from auth_app.models import User
from kindergarten.models import Kindergarten, KindergartenClass, Teacher
from kindergarten.permissions import IsSuperAdmin
from children.models import Children
from posts.models import Post
from comments.models import Comment
from activities.models import Activity
from attendance.models import Attendance
from meals.models import Meal
from hygiene.models import Hygiene
from naps.models import Nap
from mood.models import ChildMood

class StatisticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    MODEL_MAP = {
        "posts": Post,
        "comments": Comment,
        "activities": Activity,
        "attendance": Attendance,
        "meals": Meal,
        "hygiene": Hygiene,
        "naps": Nap,
        "moods": ChildMood,
        "users":User,
        "children":Children,
    }

    PREDEFINED_RANGES = {
        "past_hour": timedelta(hours=1),
        "past_4_hours": timedelta(hours=4),
        "past_day": timedelta(days=1),
        "past_7_days": timedelta(days=7),
        "past_30_days": timedelta(days=30),
        "past_90_days": timedelta(days=90),
        "past_12_months": timedelta(days=365),
        "past_5_years": timedelta(days=365 * 5),
        "since_2004": datetime(2004, 1, 1),
    }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("model", openapi.IN_QUERY, description="Model name (posts, comments, users, children,hygiene,meals,activities)", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("interval", openapi.IN_QUERY, description="Grouping interval (day, week, month, year)", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter("time_range", openapi.IN_QUERY, description="Predefined time range", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter("start_date", openapi.IN_QUERY, description="Custom start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter("end_date", openapi.IN_QUERY, description="Custom end date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: openapi.Response("Success", openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)))},
    )
    def get(self, request):
        model_name = request.GET.get("model")
        interval = request.GET.get("interval", "month")  # Default: month
        time_range = request.GET.get("time_range")  # Predefined range
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if model_name not in self.MODEL_MAP:
            return Response({"error": "Invalid model name."}, status=status.HTTP_400_BAD_REQUEST)

        Model = self.MODEL_MAP[model_name]

        if time_range in self.PREDEFINED_RANGES:
            if isinstance(self.PREDEFINED_RANGES[time_range], timedelta):
                end_date = datetime.today()
                start_date = end_date - self.PREDEFINED_RANGES[time_range]
            else:
                start_date = self.PREDEFINED_RANGES[time_range]
                end_date = datetime.today()
        else:
            try:
                if not start_date or not end_date:
                    return Response({"error": "Provide a valid time range or custom start_date and end_date."}, status=status.HTTP_400_BAD_REQUEST)
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"stats_{model_name}_{start_date}_{end_date}_{interval}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        print(request.GET.get("model")=="users",request.GET.get("model"))
        if request.GET.get("model")=="users":
          data = Model.objects.filter(date_joined__date__range=[start_date, end_date])
          trunc_map = {
              "day": TruncDay("date_joined"),
              "week": TruncWeek("date_joined"),
              "month": TruncMonth("date_joined"),
              "year": TruncYear("date_joined"),
          }
        else:
          data = Model.objects.filter(created_at__date__range=[start_date, end_date])

          trunc_map = {
              "day": TruncDay("created_at"),
              "week": TruncWeek("created_at"),
              "month": TruncMonth("created_at"),
              "year": TruncYear("created_at"),
          }

        if interval not in trunc_map:
            return Response({"error": "Invalid interval. Use 'day', 'week', 'month', or 'year'."}, status=status.HTTP_400_BAD_REQUEST)

        data = (
            data.annotate(period=trunc_map[interval])
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        response_data = list(data)
        cache.set(cache_key, response_data, timeout=600)
        return Response(response_data)

@swagger_auto_schema(
    method="get",
    responses={200: openapi.Response("Success", openapi.Schema(type=openapi.TYPE_OBJECT))},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_statistics(request):
    user = request.user

    if user.role == "superadmin":
        stats = {
            "total_kindergartens": Kindergarten.objects.count(),
            "total_classes": KindergartenClass.objects.count(),
            "total_teachers": Teacher.objects.count(),
            "total_parents": User.objects.filter(role="parent").count(),
            "total_children": Children.objects.count(),
            "total_posts": Post.objects.count(),
            "total_comments": Comment.objects.count(),
            "total_activities": Activity.objects.count(),
            "total_attendance_records": Attendance.objects.count(),
            "total_meals_logged": Meal.objects.count(),
            "total_hygiene_records": Hygiene.objects.count(),
            "total_nap_records": Nap.objects.count(),
            "total_moods_recorded": ChildMood.objects.count(),
        }
    elif user.role == "admin":
        try:
            kindergarten = user.kindergarten_admin.kindergarten
        except AttributeError:
            return Response({"error": "User is not assigned to a kindergarten"}, status=400)

        stats = {
            "total_classes": KindergartenClass.objects.filter(kindergarten=kindergarten).count(),
            "total_teachers": Teacher.objects.filter(kindergarten=kindergarten).count(),
            "total_parents": User.objects.filter(children__kindergarten=kindergarten).distinct().count(),
            "total_children": Children.objects.filter(kindergarten=kindergarten).count(),
            "total_posts": Post.objects.filter(kindergarten=kindergarten).count(),
            "total_comments": Comment.objects.filter(post__kindergarten=kindergarten).count(),
            "total_activities": Activity.objects.filter(class_id__kindergarten=kindergarten).count(),
            "total_attendance_records": Attendance.objects.filter(child__kindergarten=kindergarten).count(),
            "total_meals_logged": Meal.objects.filter(child__kindergarten=kindergarten).count(),
            "total_hygiene_records": Hygiene.objects.filter(child__kindergarten=kindergarten).count(),
            "total_nap_records": Nap.objects.filter(child__kindergarten=kindergarten).count(),
            "total_moods_recorded": ChildMood.objects.filter(child__kindergarten=kindergarten).count(),
        }
    else:
        return Response({"error": "Access Denied"}, status=403)

    return Response(stats)


class TeacherActivityView(APIView):
    """GET /analytics/teacher-activity/ — per-teacher activity summary (superadmin/admin)"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('kindergarten_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='YYYY-MM-DD'),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='YYYY-MM-DD'),
        ],
        responses={200: openapi.Response('Success', openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)))},
    )
    def get(self, request):
        user = request.user
        if user.role not in ('superadmin', 'admin'):
            return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        kindergarten_id = request.GET.get('kindergarten_id')

        teachers_qs = Teacher.objects.select_related('user', 'kindergarten')

        if user.role == 'admin':
            try:
                kindergarten = user.kindergarten_admin.kindergarten
            except AttributeError:
                return Response({"error": "Not assigned to a kindergarten"}, status=400)
            teachers_qs = teachers_qs.filter(kindergarten=kindergarten)
        elif kindergarten_id:
            teachers_qs = teachers_qs.filter(kindergarten_id=kindergarten_id)

        result = []
        for teacher in teachers_qs:
            class_ids = teacher.teacher_classes.values_list('class_id', flat=True)

            post_qs = Post.objects.filter(class_id__in=class_ids)
            activity_qs = Activity.objects.filter(class_id__in=class_ids)
            attendance_qs = Attendance.objects.filter(child__class_id__in=class_ids)

            if start_date:
                post_qs = post_qs.filter(created_at__date__gte=start_date)
                activity_qs = activity_qs.filter(time__date__gte=start_date)
                attendance_qs = attendance_qs.filter(date__gte=start_date)
            if end_date:
                post_qs = post_qs.filter(created_at__date__lte=end_date)
                activity_qs = activity_qs.filter(time__date__lte=end_date)
                attendance_qs = attendance_qs.filter(date__lte=end_date)

            result.append({
                'teacher_id': teacher.id,
                'user_id': teacher.user.id,
                'email': teacher.user.email,
                'full_name': f"{teacher.user.first_name} {teacher.user.last_name}".strip(),
                'kindergarten': teacher.kindergarten.name,
                'total_posts': post_qs.count(),
                'total_activities': activity_qs.count(),
                'total_attendance_records': attendance_qs.count(),
            })

        return Response(result)


class StudentProgressView(APIView):
    """GET /analytics/student-progress/<child_id>/ — aggregated progress for one child"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='YYYY-MM-DD'),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='YYYY-MM-DD'),
        ],
        responses={200: openapi.Response('Success', openapi.Schema(type=openapi.TYPE_OBJECT))},
    )
    def get(self, request, child_id):
        user = request.user
        child = get_object_or_404(Children, id=child_id)

        # Access control
        if user.role == 'parent' and child.parent != user:
            return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)
        if user.role == 'admin':
            try:
                if child.kindergarten != user.kindergarten_admin.kindergarten:
                    return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)
            except AttributeError:
                return Response({"error": "Not assigned to a kindergarten"}, status=400)
        if user.role == 'teacher':
            teacher_class_ids = user.teacher_profile.teacher_classes.values_list('class_id', flat=True)
            if child.class_id_id not in teacher_class_ids:
                return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        def date_filter(qs, field='date'):
            if start_date:
                qs = qs.filter(**{f'{field}__gte': start_date})
            if end_date:
                qs = qs.filter(**{f'{field}__lte': end_date})
            return qs

        attendance_qs = date_filter(child.attendances.all())
        meals_qs = date_filter(child.meals.all())
        moods_qs = date_filter(child.moods.all())
        naps_qs = date_filter(child.naps.all())
        hygiene_qs = date_filter(child.hygiene_records.all())

        mood_distribution = dict(
            moods_qs.values('mood').annotate(count=Count('id')).values_list('mood', 'count')
        )

        return Response({
            'child_id': child.id,
            'child_name': child.name,
            'attendance_days': attendance_qs.count(),
            'total_meals_logged': meals_qs.count(),
            'mood_distribution': mood_distribution,
            'total_naps': naps_qs.count(),
            'total_hygiene_records': hygiene_qs.count(),
        })


class AttendanceReportView(APIView):
    """GET /analytics/attendance-report/ — attendance summary by class/kindergarten"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('kindergarten_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='YYYY-MM-DD'),
            openapi.Parameter('end_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='YYYY-MM-DD'),
        ],
        responses={200: openapi.Response('Success', openapi.Schema(type=openapi.TYPE_OBJECT))},
    )
    def get(self, request):
        user = request.user
        if user.role not in ('superadmin', 'admin', 'teacher'):
            return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)

        qs = Attendance.objects.all()

        if user.role == 'admin':
            try:
                qs = qs.filter(child__kindergarten=user.kindergarten_admin.kindergarten)
            except AttributeError:
                return Response({"error": "Not assigned to a kindergarten"}, status=400)
        elif user.role == 'teacher':
            class_ids = user.teacher_profile.teacher_classes.values_list('class_id', flat=True)
            qs = qs.filter(child__class_id__in=class_ids)

        kindergarten_id = request.GET.get('kindergarten_id')
        if kindergarten_id and user.role == 'superadmin':
            qs = qs.filter(child__kindergarten_id=kindergarten_id)

        class_id = request.GET.get('class_id')
        if class_id:
            qs = qs.filter(child__class_id=class_id)

        start_date = request.GET.get('start_date')
        if start_date:
            qs = qs.filter(date__gte=start_date)

        end_date = request.GET.get('end_date')
        if end_date:
            qs = qs.filter(date__lte=end_date)

        by_class = (
            qs.values('child__class_id', 'child__class_id__name', 'child__kindergarten__name')
            .annotate(attendance_count=Count('id'))
            .order_by('child__class_id')
        )

        return Response({
            'total_attendance_records': qs.count(),
            'by_class': list(by_class),
        })
