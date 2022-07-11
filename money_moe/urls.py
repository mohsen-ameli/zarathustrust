from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

app_name = "money_moe"

urlpatterns = [
    # admin
    path('g0atch33se&pizz1', admin.site.urls),

    # matrix
    # path("matrix/", matrix, name="matrix"),
    
    # api
    path("api/", include("users.urls"), name="api-users"),
    path("api/", include("accounts.urls"), name="api-accounts"),
]

# match all other pages (React)
urlpatterns += [re_path(r'^.*',TemplateView.as_view(template_name='index.html'))]