from django.db.models import Count
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from auth_app.models import User
from kindergarten.models import Kindergarten, KindergartenClass, Teacher
from children.models import Children
from posts.models import Post
from comments.models import Comment
from activities.models import Activity
from attendance.models import Attendance
from meals.models import Meal
from hygiene.models import Hygiene
from naps.models import Nap
from mood.models import ChildMood
from auth_app.models import User
from children.models import Children

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
