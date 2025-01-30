from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Q

from blog.models import Post, Category, User, Comment
from .forms import PostForm, ProfileEditForm, CommentForm


def get_posts_from_db(object):
    return object.filter(
        Q(is_published=True)
        & Q(pub_date__lte=now())
        & Q(category__is_published=True)
    ).annotate(comment_count=Count('comments'))


def paginator(request, data):
    paginator = Paginator(data, 10)
    num_pages = request.GET.get('page')

    return paginator.get_page(num_pages)


def index(request):
    template = 'blog/index.html'

    post_list = get_posts_from_db(Post.objects).order_by('-pub_date')
    page_obj = paginator(request, post_list)

    content = {'page_obj': page_obj}

    return render(request, template, content)


def post_detail(request, pk):
    template = 'blog/detail.html'

    post = get_object_or_404(
        Post,
        pk=pk,
    )

    if request.user != post.author:
        post = get_object_or_404(get_posts_from_db(Post.objects), id=pk)

    comments = post.comments.order_by('created_at')
    form = CommentForm()

    content = {'post': post, 'form': form, 'comments': comments}

    return render(request, template, content)


def category_posts(request, category_slug):
    template = 'blog/category.html'

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)

    post_list = Post.objects.filter(
        Q(is_published=True)
        & Q(category=category)
        & Q(pub_date__lte=now())
    ).order_by('-pub_date')

    page_obj = paginator(request, post_list)

    content = {
        'category': category,
        'page_obj': page_obj
    }

    return render(request, template, content)


def profile(request, username):
    profile = get_object_or_404(User, username=username)

    posts = Post.objects.select_related(
        'category', 'location', 'author'
    ).annotate(comment_count=Count('comments')
               ).filter(author=profile).order_by('-pub_date')

    if request.user != profile:
        posts = get_posts_from_db(posts)

    page_obj = paginator(request, posts)

    content = {
        'profile': profile,
        'page_obj': page_obj
    }

    return render(request, 'blog/profile.html', content)


@login_required
def edit_profile(request):
    template = 'blog/user.html'

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', request.user)
    else:
        form = ProfileEditForm(instance=request.user)

    content = {'form': form}

    return render(request, template, content)


@login_required
def create_post(request):
    template = 'blog/create.html'

    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', request.user)
    else:
        form = PostForm()

    content = {'form': form}

    return render(request, template, content)


@login_required
def edit_post(request, pk):
    template = 'blog/create.html'

    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        return redirect('blog:post_detail', pk)
    if request.method == "POST":
        form = PostForm(
            request.POST, files=request.FILES or None, instance=post)
        if form.is_valid():
            post.save()
            return redirect('blog:post_detail', pk)
    else:
        form = PostForm(instance=post)

    content = {'form': form}

    return render(request, template, content)


@login_required
def delete_post(request, pk):
    template = 'blog/create.html'

    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        return redirect('blog:post_detail', pk)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        post.delete()
        return redirect('blog:index')
    else:
        form = PostForm(instance=post)

    content = {'form': form}

    return render(request, template, content)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('blog:post_detail', pk)


@login_required
def edit_comment(request, pk, comment_pk):
    template = 'blog/comment.html'

    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.user != comment.author:
        return redirect('blog:post_detail', pk)

    if request.method == "POST":
        form = CommentForm(request.POST or None, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk)
    else:
        form = CommentForm(instance=comment)

    content = {'form': form, 'comment': comment}

    return render(request, template, content)


@login_required
def delete_comment(request, pk, comment_pk):
    template = 'blog/comment.html'

    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.user != comment.author:
        return redirect('blog:post_detail', pk)

    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', pk)

    content = {'comment': comment}

    return render(request, template, content)
