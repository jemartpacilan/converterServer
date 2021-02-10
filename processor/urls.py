from django.urls import re_path
from .views import JobView, JobProcessorView


urlpatterns = [
    re_path(r'^job-queue/$', JobView.as_view(), name='job-view'),
    re_path(r'^job-processor/$', JobProcessorView.as_view(), name='job-processor'),
]
