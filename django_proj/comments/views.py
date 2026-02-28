from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Post, Comment, PostLike, CommentLike
from .serializers import (
    UserSerializer, PostSerializer, CommentSerializer,
    PostLikeSerializer, CommentLikeSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
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

    @action(detail=False, methods=['get'])
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
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=False, methods=['get'])
    def popular(self, request):
        posts = self.get_queryset().annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).order_by('-likes_count', '-comments_count')[:5]

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        week_ago = datetime.now() - timedelta(days=7)
        posts = self.get_queryset().filter(created_at__gte=week_ago)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @action(detail=False, methods=['get'])
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

    @action(detail=False, methods=['get'])
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
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer


class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer