from django.urls import path
from . import views
# import views as views
urlpatterns = [
    path("lookup/", views.lookup, name="lookup"),
    path("ports/", views.ports, name="ports"),
    path("", views.dashboard_view, name="dashboard-home"),
    path('store-data/', views.store_data, name='store_data'),
    path('view-data/', views.view_data, name='view_data'),
]
