from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from articles.models import Article
from .models import Comment
from .forms import CommentForm


@login_required
def add_comment(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            messages.success(request, 'Yorumunuz eklendi!')

    return redirect('articles:detail', pk=pk)
