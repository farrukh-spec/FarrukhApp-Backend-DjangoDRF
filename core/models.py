from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    age=models.IntegerField(null=True,blank=True)
    role=models.CharField(max_length=100,default="user")
    def __str__(self):
        return self.username
# class User(models.Model):
#     name=models.CharField(max_length=220)
#     age=models.IntegerField(null=True,blank=True)
#     password=models.CharField(max_length=255)
#     role=models.CharField(max_length=100,default="user")
    
#     def __str__(self):
#         return self.name
    
class Post(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="posts")
    
    
    def __str__(self):
        return self.title
    
class Tag(models.Model):
    name=models.CharField(max_length=200)
    users=models.ManyToManyField(User,related_name="tags")
    
    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    bio = models.TextField(null=True, blank=True)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    # The 'upload_to' creates a folder inside your S3 bucket
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    def __str__(self):
        # return f"{self.user.name}'s profile"
        return f"{self.user.username}'s profile"
    