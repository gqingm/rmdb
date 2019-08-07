from django.urls import path,re_path
from R6K.views import api

urlpatterns = [
    re_path('client/node/report/(\w+)',api.service_report),
    re_path('client/ixia/report/(\d+)$',api.report_ixia),
    re_path('client/(\w+)$',api.client_config),
]
