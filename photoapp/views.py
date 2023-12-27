from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Photo
from django.views import View
from PIL import Image
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from .models import Photo, Comment
from .forms import CommentForm
from django.contrib import messages
from taggit.managers import TaggableManager
from django.urls import reverse
from django.db.models import Count
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import os

class DeleteCommentView(LoginRequiredMixin, View):
    login_url = 'user:login'

    def post(self, request, photo_id, comment_id, *args, **kwargs):
        photo = get_object_or_404(Photo, id=photo_id)
        comment = get_object_or_404(Comment, id=comment_id)

        # Проверка, что пользователь удаляет свой собственный комментарий
        if request.user == comment.author:
            comment.delete()

        return redirect('photo:detail', pk=photo_id)    
    
class AddCommentView(View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        comment_text = request.POST.get('comment')
        
        if comment_text:
            Comment.objects.create(author=request.user, photo=photo, text=comment_text)
            messages.success(request, 'Комментарий успешно добавлен.')
        else:
            messages.error(request, 'Пустой комментарий не может быть добавлен.')

        return redirect('photo:detail', pk=photo_id)

class DownloadPhotoView(View):
    def get(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        size = request.GET.get('size', 'original')

        if size == 'original':
            image_path = photo.image.path
        else:
            # Измените размер изображения с использованием библиотеки PIL
            image = Image.open(photo.image.path)
            if size == 'small':
                image.thumbnail((100, 100))
            elif size == 'medium':
                image.thumbnail((300, 300))
            elif size == 'large':
                image.thumbnail((800, 800))
            else:
                image.thumbnail((300, 300))  # Размер по умолчанию

            # Создаем каталог для временных файлов, если его нет
            temp_directory = os.path.join(settings.MEDIA_ROOT, 'temp_medium_photos')
            os.makedirs(temp_directory, exist_ok=True)

            # Сохраняем измененное изображение во временный файл
            temp_path = os.path.join(temp_directory, f"{photo.title}_{size}.jpg")
            image.save(temp_path)
            image_path = temp_path

        with open(image_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/jpeg')
            response['Content-Disposition'] = f'attachment; filename="{photo.title}_{size}.jpg"'
        return response

class PhotoListView(ListView):
    model = Photo     
    template_name = 'photoapp/list.html'
    context_object_name = 'photos'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(like_count=Count('likes'))
        return queryset

class PhotoTagListView(PhotoListView):
    template_name = 'photoapp/taglist.html'

    def get_tag(self):
        return self.kwargs.get('tag')
    
    def get_queryset(self):
        return self.model.objects.filter(tags__slug=self.get_tag())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.get_tag()
        return context

class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'photoapp/detail.html'
    context_object_name = 'photo'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        photo = self.get_object()

        if action == 'like':
            return self.handle_like(photo)
        elif action == 'favorite':
            return self.handle_favorite(photo)

        # Возвращаем ошибку, если не указано поддерживаемое действие
        return JsonResponse({'error': 'Invalid action'}, status=400)

    def handle_like(self, photo):
        user = self.request.user

        if user.is_authenticated:
            if photo.likes.filter(pk=user.pk).exists():
                photo.likes.remove(user)
                liked = False
            else:
                photo.likes.add(user)
                liked = True

            return JsonResponse({'liked': liked, 'likes_count': photo.likes.count()})

        # Возвращаем ошибку, если пользователь не аутентифицирован
        return JsonResponse({'error': 'Authentication required'}, status=401)

    def handle_favorite(self, photo):
        user = self.request.user

        if user.is_authenticated:
            if photo.favorites.filter(pk=user.pk).exists():
                photo.favorites.remove(user)
                favorited = False
            else:
                photo.favorites.add(user)
                favorited = True

            return JsonResponse({'favorited': favorited, 'favorites_count': photo.favorites.count()})

        # Возвращаем ошибку, если пользователь не аутентифицирован
        return JsonResponse({'error': 'Authentication required'}, status=401)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = self.get_object()
        user = self.request.user
        
        context['is_liked'] = user.is_authenticated and photo.likes.filter(pk=user.pk).exists()

        return context

class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    fields = ['title', 'description', 'image', 'tags']
    template_name = 'photoapp/create.html'
    success_url = reverse_lazy('photo:list')

    def form_valid(self, form):
        form.instance.submitter = self.request.user
        return super().form_valid(form)

class UserIsSubmitter(UserPassesTestMixin):

    def get_photo(self):
        return get_object_or_404(Photo, pk=self.kwargs.get('pk'))

    def test_func(self):

        if self.request.user.is_authenticated:
            return self.request.user == self.get_photo().submitter
        else:
            raise PermissionDenied('Sorry you are not allowed here')

class PhotoUpdateView(UserIsSubmitter, UpdateView):
    template_name = 'photoapp/update.html'
    model = Photo
    fields = ['title', 'description', 'tags']
    success_url = reverse_lazy('photo:list')

class PhotoDeleteView(UserIsSubmitter, DeleteView):
    template_name = 'photoapp/delete.html'
    model = Photo
    success_url = reverse_lazy('photo:list')

