from django.shortcuts import render
from .models import News, Help
from utils import render_to_response_json

# Create your views here.

def newslist(request):
    '''新闻列表视图函数'''
    objs = News.objects.filter().order_by('-top', '-time')
    news_list = []
    for obj in objs:
        news_list.append({
            'id' : obj.id,
            'title' : obj.title,
            'content' : obj.content,
            'time' : obj.time,
            'top' : obj.top,
        })
    return render(request, 'newslist.html', {'data': news_list})

def help(request):
    '''我的预约统计视图函数'''
    obj = Help.objects.all()[0]
    data = obj.content
    return render_to_response_json({'content': data})
