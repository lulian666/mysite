from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from article.models import ArticlePost
import redis
from django.conf import settings

r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


def article_titles(request, username=None):
    if username:
        user = User.objects.get(username=username)
        article_title_list = ArticlePost.objects.filter(author=user)
        try:
            userinfo = user.userinfo
        except:
            userinfo = None
    else:
        article_title_list = ArticlePost.objects.all()

    paginator = Paginator(article_title_list, 10)
    page = request.GET.get('page')
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list

    if username:
        return render(request, 'article/list_author_articles.html',
                      {'articles': articles, 'page': current_page, 'userinfo': userinfo, 'user': user})

    return render(request, 'article/list_article_title.html', {'articles': articles, 'page': current_page})


def article_detail(request, id, slug):
    article = get_object_or_404(ArticlePost, id=id, slug=slug)
    total_views = r.incr('article:{}:views'.format(article.id))

    r.zincrby('article_ranking', 1, article.id)
    article_ranking = r.zrange('article_ranking', 0, -1, desc=True)[:10]

    article_ranking_ids = [int(id) for id in article_ranking]
    most_viewed = list(ArticlePost.objects.filter(id__in=article_ranking_ids))

    most_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))
    return render(request, 'article/list_article_detail.html',
                  {'article': article, 'total_views': total_views, 'most_viewed': most_viewed})


@login_required(login_url='/account/login/')
@csrf_exempt
@require_POST
def like_article(request):
    article_id = request.POST.get('id')
    action = request.POST.get('action')

    if article_id and action:
        try:
            article = ArticlePost.objects.get(id=article_id)
            if action == 'like':
                article.user_like.add(request.user)
                return HttpResponse('1')
            else:
                article.user_like.remove(request.user)
                return HttpResponse('2')
        except:
            return HttpResponse('0')
