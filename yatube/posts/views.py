from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import pagination


def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_profile_list = Post.objects.filter(author=author)
    page_obj = pagination(request, posts_profile_list)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(id=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, template, {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.user == post.author:
        if request.method == 'POST':
            form.save()
            return redirect('posts:post_detail', post_id)
        context = {
            'form': form,
            'is_edit': True,
            'post': post,
        }
    return render(request, template, context)
