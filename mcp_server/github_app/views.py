from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .contexts import GitHubContext
from .serializers import GitHubRepositorySerializer
from django.shortcuts import render



class GitHubRepositoryView(APIView):
    def get(self, request, owner, repo_name):
        # Use our context to fetch repository data from GitHub API
        repo_data = GitHubContext.get_repository(owner, repo_name)
        if repo_data:
            serializer = GitHubRepositorySerializer(repo_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Repository not found"}, status=status.HTTP_404_NOT_FOUND)
