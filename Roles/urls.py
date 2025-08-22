from django.urls import path
from .views import RolesView , PermissionsView


urlpatterns = [
    path("roles/", RolesView.as_view()),            # GET, POST
    path("roles/<str:name>/", RolesView.as_view()), # PUT, DELETE
    path("permission/", PermissionsView.as_view()),            # GET, POST
    path("permission/<str:code>/", PermissionsView.as_view()), # PUT, DELETEs
]