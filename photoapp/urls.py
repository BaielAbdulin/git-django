from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import AddCommentView
from .views import DeleteCommentView
from .views import (
    PhotoListView,
    PhotoTagListView,
    PhotoDetailView,
    PhotoCreateView,
    PhotoUpdateView,
    PhotoDeleteView,
    DownloadPhotoView
)

app_name = 'photo'

urlpatterns = [
    path('', PhotoListView.as_view(), name='list'),
    path('tag/<slug:tag>/', PhotoTagListView.as_view(), name='tag'),
    path('photo/<int:pk>/', PhotoDetailView.as_view(), name='detail'),
    path('photo/create/', PhotoCreateView.as_view(), name='create'),
    path('photo/<int:pk>/update/', PhotoUpdateView.as_view(), name='update'),
    path('photo/<int:pk>/delete/', PhotoDeleteView.as_view(), name='delete'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('photo/<int:photo_id>/download/', DownloadPhotoView.as_view(), name='download_photo'),
    path('photo/<int:photo_id>/add_comment/', AddCommentView.as_view(), name='add_comment'),
    path('<int:photo_id>/delete_comment/<int:comment_id>/', DeleteCommentView.as_view(), name='delete_comment'),
]
