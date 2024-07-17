"""
URL configuration for asoka_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from user.views import *
from llm.views  import *
from product.views  import *
from shop.views  import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', login.as_view()),
    path('get_user_info', get_user_info.as_view()),
    path('update_user_info', update_user_info.as_view()),
        path('save_phone', save_phone.as_view()),
   
    path('save_eval_content', save_eval_content.as_view()),
    path('get_eval_content', get_eval_content.as_view()),
    path('save_message', save_message.as_view()),
    path('get_chat_history', get_chat_history.as_view()),
    path('clear_chat_history', clear_chat_history.as_view()),
    path('save_eval_report', save_eval_report.as_view()),
    path('get_all_eval_report', get_all_eval_report.as_view()),
    path('get_certain_eval_report', get_certain_eval_report.as_view()),

    path('get_all_gem', get_all_gem.as_view()),
    path('get_certain_gem', get_certain_gem.as_view()),
    path('get_all_bracelet', get_all_bracelet.as_view()),
    path('get_certain_bracelet', get_certain_bracelet.as_view()),
    path('get_all_gift', get_all_gift.as_view()),
    path('get_gift_by_type', get_gift_by_type.as_view()),
    path('get_certain_gift', get_certain_gift.as_view()),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)