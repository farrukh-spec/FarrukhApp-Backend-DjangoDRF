from rest_framework import serializers
from .models import User, Post, Tag, Profile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields=['id','username','age','role','password']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields= '__all__'
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields= '__all__'
        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields= '__all__'
        
class UserwithPostsSerializer(serializers.ModelSerializer):  # the serializer which used recursively or reuse the posts 
    posts = PostSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        # fields = ['id', 'name',  'posts']
        fields = ['id', 'username',  'posts']
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'age', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        user.age = validated_data.get("age")
        user.role = validated_data.get("role", "user")
        user.save()
        return user