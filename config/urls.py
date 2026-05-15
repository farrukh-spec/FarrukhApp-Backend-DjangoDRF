"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from core import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
router = DefaultRouter()
router.register('users', views.UserViewSet)
# urlpatterns = router.urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/create/',views.create_user),
    path("all/users/",views.get_all_users),
    path("users/<int:user_id>/",views.get_users_byId),
    path("users/del/<int:user_id>/",views.delete_users),
    path("users/update/<int:user_id>/",views.update_users),
    path("users/posts/",views.create_post),
    path("all/posts/",views.get_all_posts),
    path("users/tags/",views.create_tag),
    path("all/tags/",views.get_all_tags),
    path("users/filter/",views.filter_users),
    path("users/paginate/",views.paginate_users),
    path("users/paginate/limit_offset/",views.paginate_users_limit_offset),
    path("users/paginate/filter/",views.paginate_and_filter_users),
    path("users/all/posts/<int:id>/",views.get_users_with_posts),
    path("users/all/posts/<int:id>/",views.get_users_with_posts),
    path("posts/all/users/<int:id>/",views.get_posts_with_users),
    path("users/inner/join/",views.inner_join_users_with_posts),
    path("users/left/join/",views.left_join_users_with_posts),
    path("users/right/join/",views.right_join_users_with_posts),
    path("users/outer/join/",views.outer_join_users_with_posts),
    path("users/cross/join/",views.cross_join_users_with_posts),
    path("users/<int:user_id>/tags/<str:tag_ids>/",views.assign_tags_to_user),
    path("users/<int:user_id>/tags/",views.get_users_with_tags),
    path("users/<int:tag_id>/users/<str:user_ids>/",views.assign_users_to_tags),
    path("tag/<int:tag_id>/users/",views.get_tag_with_users),
    path("user/profiles/",views.create_profile),
    path("user/profiles/<int:user_id>/",views.get_users_with_profile),
    path('users/create/serializer/', views.create_user_with_serializer),
    path('users/get/serializer/', views.get_users),
    path('users/get/serializer/<int:user_id>/', views.get_user_by_id),
    path('users/update/serializer/<int:user_id>/', views.update_user_with_serializer),
    path('users/delete/serializer/<int:user_id>/', views.delete_user_with_serializer),
    path('users/get/serializer/<int:id>/', views.get_users_with_posts_serializer),
    path('users/with/posts/serializer/<int:id>/', views.get_users_with_posts_serializer),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('register/', views.register_user, name='register_user'),
    path("protected/", views.profile, name="protected_view"),
    path("delete/post/<int:post_id>/", views.delete_post, name="delete_post"),
    path("auth/google/", views.google_login),
    path("auth/google/callback/", views.google_callback),
    path("forgot-password/", views.forgot_password),
    path("reset-password/", views.reset_password),
    path("test-endpoint/", views.test_endpoint),
    path("get-all-users-cache/", views.get_all_users_cache),
    # path('',views.home)get_all_users_cache
]


# #urlpatterns = [
#     path("users/", views.get_users),
#     path("users/create/", views.create_user),
#     path("users/<int:user_id>/", views.get_user),
#     path("users/delete/<int:user_id>/", views.delete_user),
# ]