from django.urls import path

from . import views

app_name = "games"
urlpatterns = [
    path("", views.AwaitView.as_view(), name="index"),
    path("weekly/", views.WeeklyView.as_view(), name="weekly"),
    path("sendweekly/", views.sendWeekly, name="sendweekly"),
    path("rejected/", views.RejectedView.as_view(), name="rejected"),
    path("send/<int:game_id>", views.send, name="send"),
    path("reject/<int:game_id>", views.reject, name="reject"),
]