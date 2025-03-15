from rest_framework import serializers

class GitHubRepositorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    full_name = serializers.CharField()
    description = serializers.CharField(allow_null=True, required=False)
    html_url = serializers.URLField()
    stargazers_count = serializers.IntegerField()
    forks_count = serializers.IntegerField()
