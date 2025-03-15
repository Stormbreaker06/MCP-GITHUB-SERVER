from django.urls import path
from .views import GitHubRepositoryView

urlpatterns = [
    path('repo/<str:owner>/<str:repo_name>/', GitHubRepositoryView.as_view(), name='github-repo'),
]
