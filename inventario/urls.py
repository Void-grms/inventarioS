from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.avance, name="avance"),
    path("login/", auth_views.LoginView.as_view(
        template_name="inventario/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("buscar/", views.buscar, name="buscar"),
    path("servicio/<int:pk>/", views.servicio_detalle, name="servicio_detalle"),
    path("bien/<int:pk>/", views.bien_detalle, name="bien_detalle"),
    path("reportes/servicio/", views.reporte_servicio, name="reporte_servicio"),
    path("reportes/responsable/", views.reporte_responsable, name="reporte_responsable"),
    path("exportar/", views.exportar, name="exportar"),
]
