from django.db import models


class GitHubRepository(models.Model):
    owner = models.CharField(max_length=255)
    repo_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    html_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner}/{self.repo_name}"
