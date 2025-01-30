from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'blog'

posts_url = [
    path('create/', views.create_post, name='create_post'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path(
        '<int:pk>/edit_comment/<int:comment_pk>/',
        views.edit_comment,
        name='edit_comment',
    ),
    path(
        '<int:pk>/delete_comment/<int:comment_pk>/',
        views.delete_comment,
        name='delete_comment',
    ),
]

profile_url = [
    path('edit/', views.edit_profile, name='edit_profile'),
    path('<str:username>/', views.profile, name='profile'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', include(posts_url)),
    path('category/<slug:category_slug>/',
         views.category_posts, name='category_posts'),
    path('profile/', include(profile_url)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
