from .models import User,Post,Tag,Profile
from django.core.paginator import Paginator
from django.db.models import Prefetch
# ================= CREATE =================
def create_user(name,age=None,password=None,role="user"):
    user= User.objects.create(
        name=name,
        age=age,
        password=password,
        role=role
    )
    return user

# ================= GET ALL =================
def get_all_users():
    return User.objects.all()

# ================= GET BY ID =================
def get_user_by_id(user_id):
    return User.objects.filter(id=user_id).first()


# ================= DELETE =================
def delete_user(user_id):
    user=User.objects.filter(id=user_id).first()
    
    if not user:
        return None
    
    user.delete()
    return  True

# ================= UPDATE =================
def update_user(data,user_id):
    user=User.objects.filter(id=user_id).first()
    if not user:
        return None
    user.name=data.get("name",user.name)
    user.age=data.get("age",user.age)
    user.role=data.get("role",user.role)
    
    user.save()
    return user

# ================================================================================= Now for the posts =================
# ================= create post =================
def create_posts(title,content,user_id):
    post= Post.objects.create(
        title=title,
        content=content,
        user_id=user_id
    )
    
    return post

# ================= create post =================
def get_all_posts():
  return Post.objects.all()

# ================================================================================= Now for the tags =================
# ================= create tag =================
def create_tags(name):
    tag= Tag.objects.create(
        name=name,
        
    )
    
    return tag

# ================= get al tags =================
def get_all_tags():
  return Tag.objects.all()

# ====================================================================== FILTERING =================
def filter_users(name=None,age=None):
    query=User.objects.all()
    if name:
        query=query.filter(name__icontains=name)
    if age:
        query=query.filter(age=age)
    return query

# ====================================================================== paginations =================
def paginate_users(page_number=1,limit=10):
    user=User.objects.all()
    paginator=Paginator(user,limit)
    page=paginator.get_page(page_number)
    # return page.object_list
    data=list(page.object_list.values())
    return {
        "total": paginator.count,
        "page": page,
        "pages": paginator.num_pages,
        "count": len(data),
        "data": data
    }
    
    
    
#     try:
#     offset = max(0, int(offset))
# except (TypeError, ValueError):
#     offset = 0

# try:
#     limit = max(min(100, int(limit)), 1)
# except (TypeError, ValueError):
#     limit = 10
    
    # ====================================================================== paginations by queryset =================
    
def paginate_users_by_queryset(offset=0,limit=10):
    queryset=User.objects.all().order_by("-id")
    total=queryset.count()
    offset=max(0,int(offset))
    limit=max(min(100,int(limit)),1)
    paginated_data=queryset[offset:offset+limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "count": len(paginated_data),
        "data": list(paginated_data.values())
    }
    
# ====================================================================== paginations and filters mixed =================
    
def paginate_queryset(queryset, offset=0, limit=10):
    total = queryset.count()

    offset = max(0, int(offset))
    limit = max(min(100, int(limit)), 1)

    paginated_data = queryset[offset:offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "count": len(paginated_data),
        "data": list(paginated_data.values())
    }
    
# ====================================================================== now the joins =================
# ====================================================================== simple left join =================

def get_users_with_posts(id=None):
    user=User.objects.filter(id=id).first()
    return user
    
# ====================================================================== simple right join =================
def get_posts_with_users(id=None):
    post=Post.objects.filter(id=id).first()
    return post


# ========================================================================now the django recomended inner joins ============================

def inner_join_users_with_posts():
    users=User.objects.filter(posts__isnull=False).distinct()
    return users

# ========================================================================now the django recomended left joins ============================
def left_join_users_with_posts():
    users=User.objects.prefetch_related("posts").all()
    return users

# ========================================================================now the django recomended right joins ============================

def right_join_users_with_posts():
    posts= Post.objects.select_related("user").all()
    return posts

# ========================================================================now the django recomended outer joins ============================

def outer_join_users_with_posts():
    users=User.objects.prefetch_related("posts").all()
    posts=Post.objects.select_related("user").all()
    return users,posts

 # ========================================================================now the django recomended cross joins ============================
def cross_join_users_with_posts():
     users=User.objects.all()
     posts=Post.objects.all()
     return users,posts


# ========================================================================now many to many relationships ============================
# ======================================================now assign tags to users ============================
def assign_tags_to_user(user_id,tag_ids):
    user = User.objects.filter(id=user_id).first()
    tag = Tag.objects.filter(id=tag_ids).first()
    
    if not user or not tag:
        return None
    
    user.tags.add(tag)
    return user


# ======================================================now get users with tags  ============================

def get_users_with_tags(user_id):
    user=User.objects.prefetch_related("tags").filter(id=user_id).first()
    return user


# ======================================================now assign users to tags   ============================

def assign_users_to_tags(tag_id, user_ids):
    tag = Tag.objects.filter(id=tag_id).first()
    users = User.objects.filter(id=user_ids).first()
    
    if not tag:
        return None
    
    tag.users.add(users)
    return tag

# ======================================================now get tags with users  ============================

def get_tag_with_users(tag_id):
    tag=Tag.objects.prefetch_related("users").filter(id=tag_id).first()
    return tag

def create_profile(user_id,bio=None,avatar=None):
    user=User.objects.filter(id=user_id).first()
    if not user:
        return None
    profile=Profile.objects.create(
        user=user,
        bio=bio,
        avatar=avatar
    )
    return profile
    
# ======================================================get users with profile  ============================

def get_users_with_profile(user_id):
    user=User.objects.select_related("profile").filter(id=user_id).first()
    return user
    

     # return JsonResponse({
     #     "total_users": users.count(),
     #     "total_posts": posts.count(),