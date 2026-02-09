from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'post-likes', views.PostLikeViewSet)
router.register(r'comment-likes', views.CommentLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]