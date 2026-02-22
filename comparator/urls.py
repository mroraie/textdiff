from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('compare/', views.compare, name='compare'),
    path('info/', views.info, name='info'),
    path('api/compare/', views.api_compare, name='api_compare'),
    path('download-report/', views.download_report_view, name='download_report'),
    path('graph/', views.graph_view, name='graph'),
    path('api/graph-data/', views.api_graph_data, name='api_graph_data'),
    path('upload/', views.upload_and_compare, name='upload_and_compare'),
]

