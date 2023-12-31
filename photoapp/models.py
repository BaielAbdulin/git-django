from django.db import models
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.urls import reverse

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.text[:20]}'

    class Meta:
        ordering = ['-created_at']


class Photo(models.Model):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=250) 
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='photos/')
    submitter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tags = TaggableManager()
    likes = models.ManyToManyField(User, related_name='liked_photos', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_photos', blank=True)

    def __str__(self):
        return self.title