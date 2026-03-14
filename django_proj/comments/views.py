from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Post, Comment, PostLike, CommentLike
from .serializers import (
    UserSerializer, UserCreateSerializer, UserLoginSerializer,
    PostSerializer, CommentSerializer,
    PostLikeSerializer, CommentLikeSerializer
)
from .permissions import IsAuthorOrAdminOrReadOnly, IsAdminOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'register':
            return [AllowAny()]
        elif self.action == 'login':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve']:
            return [IsAdminOrReadOnly()]
        else:
            return [IsAdminOrReadOnly()]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Неверные учетные данные'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def activity(self, request, pk=None):
        user = self.get_object()
        data = {
            'user_id': user.id,
            'username': user.username,
            'posts_count': user.posts.count(),
            'comments_count': user.comments.count(),
            'post_likes_given': user.post_likes.count(),
            'comment_likes_given': user.comment_likes.count(),
            'joined': user.date_joined,
        }
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def top_active(self, request):
        users = User.objects.annotate(
            posts_count=Count('posts'),
            comments_count=Count('comments'),
            total_activity=Count('posts') + Count('comments')
        ).order_by('-total_activity')[:5]

        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'posts': user.posts_count,
                'comments': user.comments_count,
                'total': user.total_activity,
            })
        return Response(data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthorOrAdminOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(
            post=post,
            user=request.user
        )

        if not created:
            like.delete()
            return Response({'status': 'like removed', 'likes_count': post.total_likes})

        return Response({'status': 'like added', 'likes_count': post.total_likes})

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def popular(self, request):
        posts = self.get_queryset().annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).order_by('-likes_count', '-comments_count')[:5]

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def recent(self, request):
        week_ago = datetime.now() - timedelta(days=7)
        posts = self.get_queryset().filter(created_at__gte=week_ago)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def activity(self, request, pk=None):
        post = self.get_object()
        data = {
            'post_id': post.id,
            'title': post.title,
            'total_likes': post.total_likes,
            'total_comments': post.total_comments,
            'likes_by_day': post.likes.filter(
                created_at__gte=datetime.now() - timedelta(days=7)
            ).count(),
            'comments_by_day': post.comments.filter(
                created_at__gte=datetime.now() - timedelta(days=7)
            ).count(),
        }
        return Response(data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthorOrAdminOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user
        )

        if not created:
            like.delete()
            return Response({'status': 'like removed', 'likes_count': comment.total_likes})

        return Response({'status': 'like added', 'likes_count': comment.total_likes})

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def by_post(self, request):
        post_id = request.query_params.get('post_id')
        if not post_id:
            return Response(
                {'error': 'post_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comments = self.get_queryset().filter(post_id=post_id, parent__isnull=True)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def stats(self, request):
        total = self.get_queryset().count()
        with_parent = self.get_queryset().filter(parent__isnull=False).count()

        data = {
            'total_comments': total,
            'reply_comments': with_parent,
            'top_level_comments': total - with_parent,
        }
        return Response(data)


class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all().order_by('-created_at')
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all().order_by('-created_at')
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)