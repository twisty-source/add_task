from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import BlogPost
from .forms import BlogPostForm


def index(request):
    """Главная страница со списком всех публикаций блога."""
    posts = BlogPost.objects.order_by('-date_added')
    context = {'posts': posts}
    return render(request, 'blogs/index.html', context)


def post_detail(request, post_id):
    """Отдельная страница публикации."""
    post = get_object_or_404(BlogPost, id=post_id)
    context = {'post': post}
    return render(request, 'blogs/post_detail.html', context)


@login_required
def new_post(request):
    """Создание новой публикации (только для авторизованных авторов)."""
    if request.method != 'POST':
        form = BlogPostForm()
    else:
        form = BlogPostForm(data=request.POST)
        if form.is_valid():
            new_post_obj = form.save(commit=False)
            new_post_obj.owner = request.user
            new_post_obj.save()
            return redirect('blogs:index')

    context = {'form': form}
    return render(request, 'blogs/new_post.html', context)


@login_required
def edit_post(request, post_id):
    """Редактирование публикации (только автором)."""
    post = get_object_or_404(BlogPost, id=post_id, owner=request.user)

    if request.method != 'POST':
        form = BlogPostForm(instance=post)
    else:
        form = BlogPostForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blogs:post_detail', post_id=post.id)

    context = {'post': post, 'form': form}
    return render(request, 'blogs/edit_post.html', context)


@login_required
def delete_post(request, post_id):
    """Удаление публикации автором с подтверждением (только POST)."""
    post = get_object_or_404(BlogPost, id=post_id, owner=request.user)

    if request.method == 'POST':
        post.delete()
        return redirect('blogs:index')

    context = {'post': post}
    return render(request, 'blogs/delete_confirm.html', context)
