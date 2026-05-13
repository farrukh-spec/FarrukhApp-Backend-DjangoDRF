# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models import User, Post, Tag, Profile

# @receiver(post_save, sender=User)
# def user_created(sender, instance, created, **kwargs):
#     if created:
#         profile = Profile.objects.create(user=instance, bio=f"This is the profile of {instance.name}")
#         # print(f"User created: {instance.name}")
        
        
# @receiver(post_delete, sender=User)
# def user_deleted(sender, instance, **kwargs):
#     # print(f"User deleted: {instance.name}")
#     print(f"User deleted: ")
#     # print(f"User deleted: {instance.title}")
    