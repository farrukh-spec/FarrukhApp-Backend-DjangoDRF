from email import message

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.http import JsonResponse
import json
from . import services
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer, PostSerializer, TagSerializer, ProfileSerializer, UserwithPostsSerializer, RegisterSerializer
from .models import User, Post, Tag, Profile
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import redirect
from config import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from celery.result import AsyncResult # Importer to check status inside Redis
from .tasks import process_heavy_calculation, send_future_alert_task
# ==============================>create user<=================
@csrf_exempt
def create_user(request):
    data=json.loads(request.body)
    if not data:
        return
    user=services.create_user(
        name=data["name"],
        age=data.get("age"),
        password=data["password"],
        role=data.get("role","user")
        
    )
    
    return JsonResponse({
        "id":user.id,
        "name":user.name
    })
    
    # ==============================>to get all user<================= 
@csrf_exempt   # hers its optional
def get_all_users(request):
    data=services.get_all_users()
    users=list(data.values())
    return JsonResponse({"count":len(users),"users":users}, safe=False)


# ==============================>to get user by id<=================

@csrf_exempt
def get_users_byId(request,user_id):
    user = services.get_user_by_id(user_id)
    
    if not user:
        return JsonResponse({"error":"user not found"},status=404) 
    
    return JsonResponse({
        "id":user.id,
        "name":user.name,
        "age":user.age,
        "role":user.role
    })


# ==============================>to get user by id and delete<=================
@csrf_exempt
def delete_users(request,user_id):
    user=services.delete_user(user_id)
    
    if not user:
        return JsonResponse({"error":"user not found"},status=404)
    return JsonResponse({"message":"user deleted"})
    
# ==============================>to get user by id<=================
@csrf_exempt
def update_users(request,user_id):
    
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({"error":"Method not allowed"},status=405)
    try:
        data=json.loads(request.body)
    except:
         return JsonResponse({"error": "Invalid JSON"}, status=400)
     
    user= services.update_user(data,user_id)
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    return JsonResponse({
        "id": user.id,
        "name": user.name,
        "age": user.age,
        "role": user.role
    })
     
 # ===========================================================================>now the time for the posts<=================
 #  =================================create post============================
@csrf_exempt   
def create_post(request):
    try:
        data=json.loads(request.body)
    except:
         return JsonResponse({"error": "Invalid JSON"}, status=400)
    # post= services.create_posts(data)
    post= services.create_posts(
        title=data["title"],
        content=data["content"],
        user_id=data["user_id"]
    )
    
    # return JsonResponse({"count":len(post),"posts":post})
    return JsonResponse({
    "success": True,
    "data": {
        "id": post.id,
        "title": post.title
    }
})
    

#  =================================get all posts============================
        
def get_all_posts(request):
    
    posts=services.get_all_posts()
    
    all_posts=list(posts.values())
    
    return JsonResponse({
        "success":True,
        "count":len(all_posts),
        "posts":all_posts
    })
        
        # ===========================================================================>now the time for the tags<=================
        #  =================================create tag============================
@csrf_exempt  
def create_tag(request):
    try:
        data=json.loads(request.body)
    except:
         return JsonResponse({"error": "Invalid JSON"}, status=400)
    # post= services.create_posts(data)
    tag= services.create_tags(
        name=data["name"],
        
    )
    
    # return JsonResponse({"count":len(post),"posts":post})
    return JsonResponse({
    "success": True,
    "data": {
        "id": tag.id,
        "title": tag.name
    }
})
        
   
def get_all_tags(request):
    tags=services.get_all_tags()
    all_tags=list(tags.values())
    return JsonResponse({
        "success":True,
        "count":len(all_tags),
        "data":all_tags
    })
        
        
        # ====================================================================== FILTERING =================
        
def filter_users(request):
    data=json.loads(request.body)
    name=data.get("name")
    age=data.get("age")
    filtered_users=services.filter_users(name,age)
    all_users=list(filtered_users.values())
    if not all_users:
        return JsonResponse({"message":"No users found matching the criteria"}, status=404)
    return JsonResponse({
        "success":True,
        "count":len(all_users),
        "data":all_users
    })
    
     # ====================================================================== paginations =================
def paginate_users(request):
    data=json.loads(request.body)
    page_number=data.get("page",1)
    limit=data.get("limit",10)
    paginated_users=services.paginate_users(page_number,limit)
    # all_users=list(paginated_users.values())
    all_users=paginated_users
    return JsonResponse({
        "success":True,
        "count":all_users.get("count"),
        "total":all_users["total"],
        "page":all_users["page"].number,
        "pages":all_users["pages"],
        "data":all_users["data"]
    })
    
     # ====================================================================== paginations by limit offset =================
def paginate_users_limit_offset(request):
    data=json.loads(request.body)
    offset=data.get("offset",0)
    limit=data.get("limit",10)
    paginated_users=services.paginate_users_by_queryset(offset,limit)
    all_users=paginated_users
    return JsonResponse({
        "success":True,
        "count":all_users.get("count"),
        "total":all_users["total"],
        "offset":offset,
        "limit":limit,
        "data":all_users["data"]
    })
    
    
     # ====================================================================== paginations and filtering mixed =================
    
def paginate_and_filter_users(request):
    data=json.loads(request.body)
    name=data.get("name")
    age=data.get("age")
    offset=data.get("offset",0)
    limit=data.get("limit",10)
    queryset=services.filter_users(name,age)
    
    paginated_data=services.paginate_queryset(queryset,offset,limit)
    
    return JsonResponse({
        "success":True,
        "count":paginated_data.get("count"),
        "total":paginated_data["total"],
        "offset":paginated_data["offset"],
        "limit":paginated_data["limit"],
        "data":paginated_data["data"]
        })
    
    
     # ====================================================================== now the joins =================
     # ====================================================================== simple left join =================
def get_users_with_posts(request,id):
    user=services.get_users_with_posts(id)
    if not user:
        return JsonResponse({"message":"User not found"}, status=404)
    posts=user.posts.all()
    posts_data=list(posts.values())
    user_data={
        "id":user.id,
        "name":user.name,
        "posts":posts_data
    }
    return JsonResponse({
        "success":True,
        "data":user_data
    })
    
    # ====================================================================== simple right join =================
            
def get_posts_with_users(request,id):
    post=services.get_posts_with_users(id)
    if not post:
        return JsonResponse({"message":"Post not found"}, status=404)
    user=post.user
    # user_data={
    #     "id":user.id,
    #     "name":user.name,
    #     "posts":[post]
    # }
    
    user_data = {
        "id": user.id,
        "name": user.name,
        # "posts":post
        "posts": [
    {
        "id": p.id,
        "title": p.title,
        "content": p.content,
    }
    for p in user.posts.all()
]
    }
    return JsonResponse({
        "success":True,
        "data":user_data
    })
    
    
    # ========================================================================now the django recomended inner joins ============================
    
    
def inner_join_users_with_posts(request):
    users=services.inner_join_users_with_posts()
    
    data=[]
    
    for user in users:
        posts=user.posts.all()
        posts_data=list(posts.values())
        user_data={
            "id":user.id,
            "name":user.name,
            "posts_data":{
                "count":len(posts_data),
                "posts":posts_data
            }
        }
        data.append(user_data)
        
    return JsonResponse({
        "success":True,
        "count":len(data),
        "data":data
    })
        
     # ========================================================================now the django recomended left joins ============================
def left_join_users_with_posts(request):
    users=services.left_join_users_with_posts()
    
    data=[]
    
    for user in users:
        posts=user.posts.all()
        posts_data=list(posts.values())
        user_data={
            "id":user.id,
            "name":user.name,
            "posts_data":{
                "count":len(posts_data),
                "posts":posts_data
            }
        }
        data.append(user_data)
        
    return JsonResponse({
        "success":True,
        "count":len(data),
        "data":data
    })
       
    
    
    # ========================================================================now the django recomended right joins ============================
def right_join_users_with_posts(request):
    posts=services.right_join_users_with_posts()
    
    data=[]
    for post in posts:
        user=post.user
        user_data={
            "id":user.id,
            "name":user.name,
            "posts":[
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                }
            ]
        }
        data.append(user_data)
    return JsonResponse({
        "success":True,
        "count":len(data),
        "data":data
    })
    
     # ========================================================================now the django recomended outer joins ============================
    
def outer_join_users_with_posts(request):
    users,posts=services.outer_join_users_with_posts() 
    
    data = []

    for user in users:
        data.append({
            "type": "user",
            "id": user.id,
            "name": user.name,
            "posts": list(user.posts.values())
        })

    for post in posts:
        data.append({
            "type": "post",
            "title": post.title,
            "user": post.user.name if post.user else None
        })

    return JsonResponse({"data": data})
    
    # data=[]  
    # for user in users:
    #     data.append({
    #         "id":user.id,
    #         "name":user.name,
    #         "posts":[
    #             {
    #                 "id": post.id,
    #                 "title": post.title,
    #                 "content": post.content,
    #             }
    #             for post in user.posts.all()
    #         ]
    #     })
        
    #     for post in posts:
    #         if post.user is None:
    #             data.append({
    #                 "id": None,
    #                 "name": None,
    #                 "posts":[
    #                     {
    #                         "id": post.id,
    #                         "title": post.title,
    #                         "content": post.content,
    #                     }
    #                 ]
    #             })
    # return JsonResponse({
    #     "success":True,
    #     "count":len(data),
    #     "data":data
    # }) 
    



 # ========================================================================now the django recomended cross joins ============================
 
def cross_join_users_with_posts(request):
    users,posts=services.cross_join_users_with_posts()
    data = []
    for user in users:
        for post in posts:
            data.append({
                "user_id": user.id,
                "user_name": user.name,
                "post_id": post.id,
                "post_title": post.title,
                "post_content": post.content
            })
    return JsonResponse({
        "success": True,
        "count": len(data),
        "data": data
    })



# ========================================================================now many to many relationships ============================
# ======================================================now assign tags to users ============================
@csrf_exempt
def assign_tags_to_user(request,user_id,tag_ids):
    
    user=services.assign_tags_to_user(user_id,tag_ids)
    if not user:
        return JsonResponse({"error":"User or Tag not found"},status=404)
    tags=user.tags.all()
    tags_data=list(tags.values())
    
    return JsonResponse({
        "success":True,
        "message":"Tags assigned to user successfully",
        "data":{
            "id":user.id,
            "name":user.name,
            "tags":tags_data
        }
    })

# ======================================================now get users with  tags to users ============================

@csrf_exempt
def get_users_with_tags(request,user_id):
    user=services.get_users_with_tags(user_id)
    if not user:
        return JsonResponse({"error":"User not found"},status=404)
    tags=user.tags.all()
    tags_data=list(tags.values())
    
    return JsonResponse({
        "success":True,
        "data":{
            "id":user.id,
            "name":user.name,
            "tags":tags_data
        }
    })
    
# ====================================================== now assign users to the tags  ============================

@csrf_exempt
def assign_users_to_tags(request,tag_id,user_ids):
    tag=services.assign_users_to_tags(tag_id,user_ids)
    if not tag:
        return JsonResponse({"error":"User or Tag not found"},status=404)
    users=tag.users.all()
    user_data=list(users.values())
    return JsonResponse({
        "success":True,
        "message":"Users assigned to tag successfully",
        "data":{
            "id":tag.id,
            "name":tag.name,
            "users":user_data
        }
    })
    
    # ====================================================== now get users with tags  ============================
@csrf_exempt
def get_tag_with_users(request,tag_id):
        tag=services.get_tag_with_users(tag_id)
        if not tag:
            return JsonResponse({"error":"Tag not found"},status=404)
        users=tag.users.all()
        user_data=list(users.values())
        return JsonResponse({
            "success":True,
            "data":{
                "id":tag.id,
                "name":tag.name,
                "users":user_data
            }
        })  

# @csrf_exempt
# def create_profile(request):
#     # try:
#     #      data=json.loads(request.body)
#     # except:
#     #      return JsonResponse({"error": "Invalid JSON"}, status=400) 
#     # user_id=data.get("user_id")
#     # bio=data.get("bio")
#     # avatar=data.get("avatar")
#     # profile_picture=request.FILES.get("profile_picture")
#     user_id=request.POST.get("user_id")
#     bio=request.POST.get("bio")
#     avatar=request.POST.get("avatar")
#     profile_picture=request.FILES.get("profile_picture")
#     profile=services.create_profile(user_id,bio,avatar,profile_picture)
#     if not profile:
#         return JsonResponse({"error":"User not found"},status=404)
#     return JsonResponse({
#         "success":True,
#         "data":{
#             "id":profile.id,
#             "user_id":profile.user.id,
#             "bio":profile.bio,
#             "avatar":profile.avatar,
#             # "profile_picture":profile.profile_picture
#             "profile_picture": profile.profile_picture.url if profile.profile_picture else None
#         }
#     })

@csrf_exempt
def create_profile(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # 1. Read Text data from form-data using request.POST
    user_id = request.POST.get("user_id")
    bio = request.POST.get("bio")
    avatar = request.POST.get("avatar")
    
    # 2. Read the binary Image file from request.FILES
    profile_picture = request.FILES.get("profile_picture")

    # Validate that we got a user_id
    if not user_id:
        return JsonResponse({"error": "user_id is required"}, status=400)

    # 3. Call your service to process and save to S3
    profile = services.create_profile(user_id, bio, avatar, profile_picture)
    
    if not profile:
        return JsonResponse({"error": "User not found"}, status=404)
        
    # 4. Return success response
    return JsonResponse({
        "success": True,
        "data": {
            "id": profile.id,
            "user_id": profile.user.id,
            "bio": profile.bio,
            "avatar": profile.avatar,
            # .url will give you the full automatic AWS S3 bucket string path!
            "profile_picture": profile.profile_picture.url if profile.profile_picture else None
        }
    })

# {
#     "user_id": 2,
#     "avatar": " s3 management",
#     "bio": "bio of the farrukh"
# }

# ======================================================get users with profile  ============================

@csrf_exempt
def get_users_with_profile(request,user_id):
    user=services.get_users_with_profile(user_id)
    if not user:
        return JsonResponse({"error":"User not found"},status=404)
    return JsonResponse({
        "success":True,
        "data":{
            "id":user.id,
            "name":user.name,
            "profile":{
                "id":user.profile.id,
                "bio":user.profile.bio,
                "avatar":user.profile.avatar
            } if hasattr(user,"profile") else None
        }
    })




# ====================================================== now with the serializers  ============================
# ============================================= now create user  ============================
@api_view(['POST'])
def create_user_with_serializer(request):
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid():
        # user=serializer.save()
        serializer.save()
        # INVALIDATION: New user added, so the list cache is now wrong
        cache.delete('all_users_list')
        return Response({
            "success":True,
            "data":serializer.data
        })

    return Response({
        "success":False,
        "errors":serializer.errors
    },status=400)
    
    # ========================================= get users  ============================
    
@api_view(['GET'])
def get_users(request):
    cache_key = 'all_users_list'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response({"success": True, "source": "cache", "data": cached_data})
    users=User.objects.all()
    serializer=UserSerializer(users,many=True)
    cache.set(cache_key, serializer.data, timeout=60)
    return Response({
        "success":True,
        "count":len(serializer.data),
        "data":serializer.data
    })
    
# ========================================= get users  by id ============================
# @api_view(['GET'])
# def get_user_by_id(request,user_id):
#     user=User.objects.filter(id=user_id).first()
#     if not user:
#         return Response({
#             "success":False,
#             "message":"User not found"
#         },status=404)
#     serializer=UserSerializer(user)
#     return Response({
#         "success":True,
#         "data":serializer.data
#     })

@api_view(['GET'])
def get_user_by_id(request, user_id):
    cache_key = f"user_profile_{user_id}"
    cached_user = cache.get(cache_key)

    if cached_user:
        return Response({"success": True, "source": "cache", "data": cached_user})

    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"success": False, "message": "User not found"}, status=404)

    serializer = UserSerializer(user)
    cache.set(cache_key, serializer.data, timeout=300)

    return Response({"success": True, "source": "database", "data": serializer.data})
    
    # ========================================= update users  with serializer============================
    
@api_view(['PUT','PATCH'])
def update_user_with_serializer(request,user_id):
        user=User.objects.filter(id=user_id).first()
        if not user:
            return Response({
                "success":False,
                "message":"User not found"
            },status=404)
        serializer=UserSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            # PRO TIP: Delete the list cache so the next 'GET' sees the update
            cache.delete('all_users_list')
            cache.delete(f"user_profile_{user_id}")
            return Response({
                "success":True,
                "data":serializer.data
            })
            
        return Response({
            "success":False,
            "errors":serializer.errors
        },status=400)   
        
    # ========================================= delete users  with serializer============================
    
@api_view(['DELETE'])
def delete_user_with_serializer(request,user_id):
        user=User.objects.filter(id=user_id).first()
        if not user:
            return Response({
                "success":False,
                "message":"User not found"
            },status=404)
        user.delete()
        # INVALIDATION: User is gone
        cache.delete('all_users_list')
        cache.delete(f"user_profile_{user_id}")
        return Response({
            "success":True,
            "message":"User deleted successfully"
        })
    
     # ========================================= users with their posts with serializer============================
@api_view(['GET'])
def get_users_with_posts_serializer(request,id):
    user=User.objects.filter(id=id).first()
    if not user:
        return Response({
            "success":False,
            "message":"User not found"
        },status=404)
    serializer=UserwithPostsSerializer(user)
    return Response({
        "success":True,
        "data":serializer.data
    })
        
    
    # ========================================= all the cruds in the DRF with viewsets ============================
    
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
     # ========================================= register user ============================
@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "success": True,
            "user": RegisterSerializer(user).data
        })

    return Response(serializer.errors, status=400)


 # ========================================= protected routes  ============================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response({
        "user": request.user.id,
        "name": request.user.username,
    })
    
    # ========================================= role based routes  ============================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):

    if request.user.role != "admin":
        return Response({
            "error": "Only admins allowed"
        }, status=403)
    # post=Post.objects.filter(id=post_id).first()
    # if not post:
    #     return Response({
    #         "error": "Post not found"
    #     }, status=404)
    # post.delete()
    return Response({
        "success": True,
        "message": "Post deleted successfully"
    })

# ========================================= redirection to the google auth  ============================
def google_login(request):

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        "&response_type=code"
        "&scope=openid email profile"
        "&redirect_uri=http://localhost:8000/auth/google/callback/"
    )

    return redirect(google_auth_url)
 # ========================================= Google OAuth callback  ============================
    
# def google_callback(request):

#     code = request.GET.get("code")

#     # return JsonResponse({
#     #     "code": code
#     # })
    
#     token_url = "https://oauth2.googleapis.com/token"
#     data = {
#         "code": code,
#         "client_id": settings.GOOGLE_CLIENT_ID,
#         "client_secret": settings.GOOGLE_CLIENT_SECRET,
#         "redirect_uri": "http://localhost:8000/auth/google/callback/",
#         "grant_type": "authorization_code",
#     }
#     response = requests.post(token_url, data=data)
#     token_response = response.json()
#     access_token = token_response.get("access_token")
#      # ================= GOOGLE USER INFO =================
     
#     userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     userinfo_response = requests.get(userinfo_url, headers=headers)
#     userinfo = userinfo_response.json()
#     email = userinfo.get("email")   
#     name = userinfo.get("name")
    
#      # ================= CREATE USER =================
#     user, created = User.objects.get_or_create(
#      username=email,
#      defaults={"first_name": name, "email": email}
     
#     )
    
#     # ================= CREATE JWT TOKENS =================
    
#     refresh = RefreshToken.for_user(user)
#     return JsonResponse({
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#         "user": {
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "name": user.first_name
#         }
#     })
     
     
     
def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "No code provided from Google"}, status=400)

    # 1. Exchange Code for Access Token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": "http://localhost:8000/auth/google/callback/", # MUST match your console
        "grant_type": "authorization_code",
    }
    
    token_response = requests.post(token_url, data=data).json()
    access_token = token_response.get("access_token")

    # GATE 1: Did we actually get a token?
    if not access_token:
        return JsonResponse({
            "error": "Failed to get access token",
            "details": token_response  # This helps you debug!
        }, status=400)

    # 2. Get Google User Profile
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo = requests.get(userinfo_url, headers=headers).json()
    
    email = userinfo.get("email")
    name = userinfo.get("name", "")

    # GATE 2: Did Google give us an email?
    if not email:
        return JsonResponse({"error": "Google did not return an email address"}, status=400)

    # 3. Save User to Database
    # We use 'email' as the 'username' because emails are unique
    user, created = User.objects.get_or_create(
        username=email, 
        defaults={
            "email": email,
            "first_name": name
        }
    )

    # 4. Generate JWT for your Backend
    refresh = RefreshToken.for_user(user)
    
    return JsonResponse({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username
        }
    })
     
      # ================= forget password  =================
      
@api_view(['POST'])
def forgot_password(request):
    email = request.data.get("email")
    user = User.objects.filter(username=email).first()
    if not user:
        return Response({"error": "User with this email does not exist"}, status=404)
    token = PasswordResetTokenGenerator().make_token(user)
    reset_link = f"http://localhost:8000/reset-password/{user.id}/{token}/"
    # send_mail(
    #     "Password Reset Request",
    #     f"Click the link to reset your password: {reset_link}",
    #     "from@example.com",
    #     [email],
    #     fail_silently=False,
    # )
    send_mail(
        subject="Reset Your Password",
        message=f"Click here: {reset_link}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )
    return Response({"message": "Password reset link sent to your email"})

# ================= to set  password  =================

@api_view(['POST'])
def reset_password(request):
    user_id = request.data.get("user_id")
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=404)
    
    valid=PasswordResetTokenGenerator().check_token(user, token)
    if not valid:
        return Response({"error": "Invalid or expired token"}, status=400)
    user.set_password(new_password)
    user.save()
    return Response({"message": "Password reset successful"})
    
    
    # ================= testing endpoint just json   =================
@api_view(['GET'])
def test_endpoint(request):
    return Response({"message": "Hello, World! mango ginga lala"})


# ================= now fro the cache by using the redis   =================

# @api_view(['GET'])
# def get_all_users_cache(request):
#     cached_users = cache.get('all_users')
#     if cached_users is not None:
#         return Response({
#             "success": True,
#             "redis_cache": True,
#             "count": len(cached_users),
#             "users": cached_users
#         })
#     # data=services.get_all_users()
#     data=User.objects.all()
#     users=list(data.values())
#     cache.set('all_users', users, timeout=30)  # Cache for 60 seconds
#     return Response({"count":len(users),"users":users , "realdb": True})


@api_view(['GET'])
def get_all_users_cache(request):
    cache_key = 'all_users_list'
    
    # 1. Try to get data from Redis
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response({
            "success": True,
            "source": "cache",
            "data": cached_data
        })

    # 2. Cache MISS: Hit the DB
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    
    # 3. Save the serialized data to Redis (30 seconds)
    cache.set(cache_key, serializer.data, timeout=60)
    
    return Response({
        "success": True,
        "source": "database",
        "data": serializer.data
    })



# ==================================celery jobs

@csrf_exempt
def trigger_calculation_api(request):
    """Endpoint 1: Launches the job and hands back a tracking ticket ID"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
        
    num1 = data.get("num1")
    num2 = data.get("num2")
    
    if not num1 or not num2:
        return JsonResponse({"error": "Please provide num1 and num2"}, status=400)

    # Launch the task instantly in the background
    task = process_heavy_calculation.delay(num1, num2)

    # Instantly return the tracking ticket ID to Postman
    return JsonResponse({
        "success": True,
        "message": "Calculation processing started in backend memory stack.",
        "task_id": task.id # This is the unique UUID string token
    })


def check_task_status_api(request, task_id):
    """Endpoint 2: User passes the task_id here to look inside Redis for the answer"""
    # Look into your Redis container using the task UUID
    task_result = AsyncResult(task_id)
    
    response_data = {
        "task_id": task_id,
        "status": task_result.status, # Returns PENDING, STARTED, SUCCESS, or FAILURE
        "result": None
    }
    
    if task_result.status == "SUCCESS":
        response_data["result"] = task_result.result # Captures the returned math value!
        
    return JsonResponse(response_data)



@csrf_exempt
def schedule_user_alarm_api(request):
    """Endpoint: User provides a message and a countdown delay in seconds"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
        
    user_id = data.get("user_id")
    message = data.get("message")
    delay_seconds = data.get("delay_seconds") # How many seconds to wait (e.g., 30)

    if not user_id or not message or not delay_seconds:
        return JsonResponse({"error": "Missing user_id, message, or delay_seconds"}, status=400)

    # MAGIC KEYWORD: countdown tells Celery how many seconds to wait before executing
    send_future_alert_task.apply_async(
        args=[user_id, message],
        countdown=int(delay_seconds) 
    )

    return JsonResponse({
        "success": True,
        "message": f"Alarm successfully scheduled! The system will execute it in exactly {delay_seconds} seconds."
    })

    # import requests

# def google_callback(request):
#     code = request.GET.get("code")
    
#     # The Backend Swap: Exchange code for the real tokens
#     token_url = "https://oauth2.googleapis.com/token"
#     data = {
#         "code": code,
#         "client_id": settings.GOOGLE_CLIENT_ID,
#         "client_secret": settings.GOOGLE_CLIENT_SECRET,
#         "redirect_uri": "http://127.0.0.1:8000/auth/google/callback/",
#         "grant_type": "authorization_code",
#     }
    
#     response = requests.post(token_url, data=data)
#     return JsonResponse(response.json()) # This will show your Access Token!
    



    #             "title": post.title,
    #             "content": post.content,
    #         }
    #     ]
     
     
    # user=services.update_user()

# from django.http import HttpResponse
# def home(request):
#     return HttpResponse("Hello Django 🚀")
