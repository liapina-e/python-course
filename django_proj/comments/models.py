from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return f"{self.title} (автор: {self.author.username})"

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_comments(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор"
    )
    content = models.TextField(verbose_name="Содержание комментария")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Родительский комментарий"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий от {self.author.username} к посту '{self.post.title}'"

    def clean(self):
        if self.parent and self.parent.post != self.post:
            raise ValidationError("Родительский комментарий должен относиться к тому же посту")

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def is_reply(self):
        return self.parent is not None


class PostLike(models.Model):
    """
    Лайки для постов
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Пост"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post_likes',
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        unique_together = ['post', 'user']
        verbose_name = "Лайк поста"
        verbose_name_plural = "Лайки постов"

    def __str__(self):
        return f"{self.user.username} лайкнул(а) '{self.post.title}'"


class CommentLike(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Комментарий"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_likes',
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        unique_together = ['comment', 'user']
        verbose_name = "Лайк комментария"
        verbose_name_plural = "Лайки комментариев"

    def __str__(self):
        return f"{self.user.username} лайкнул(а) комментарий от {self.comment.author.username}"