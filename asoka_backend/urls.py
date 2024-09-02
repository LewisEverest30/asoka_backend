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
    # path('save_message', save_message.as_view()),
    path('get_chat_history', get_chat_history.as_view()),
    path('start_chat', start_chat.as_view()),
    path('continue_chat', continue_chat.as_view()),
    path('clear_chat_history', clear_chat_history.as_view()),
    path('generate_eval_report', generate_eval_report.as_view()),
    path('get_all_eval_report', get_all_eval_report.as_view()),
    path('get_certain_eval_report', get_certain_eval_report.as_view()),

    path('get_all_gem', get_all_gem.as_view()),
    path('get_certain_gem', get_certain_gem.as_view()),
    path('get_certain_gem_byname', get_certain_gem_byname.as_view()),
    path('get_all_bracelet', get_all_bracelet.as_view()),
    path('get_certain_bracelet', get_certain_bracelet.as_view()),
    path('get_all_gift', get_all_gift.as_view()),
    path('get_gift_by_symbol', get_gift_by_symbol.as_view()),
    path('get_certain_gift', get_certain_gift.as_view()),
    path('get_all_stamp', get_all_stamp.as_view()),
    path('get_certain_stamp', get_certain_stamp.as_view()),
    path('get_recommended_product', get_recommended_product.as_view()),

    path('get_all_scheme', get_all_scheme_template.as_view()),
    path('get_advice', get_advice.as_view()),
    path('get_advice_for_scheme', get_advice_for_scheme.as_view()),

    # path('create_cart', create_cart.as_view()),
    path('create_cart_from_parts', create_cart_from_parts.as_view()),
    path('create_cart_from_gift', create_cart_from_gift.as_view()),
    path('create_cart_from_scheme', create_cart_from_scheme.as_view()),
    path('get_all_cart', get_all_cart.as_view()),
    path('update_cart_quantity', update_cart_quantity.as_view()),
    path('delete_cart', delete_cart.as_view()),
    path('clear_cart', clear_cart.as_view()),

    path('create_address', create_address.as_view()),
    path('get_all_address', get_all_address.as_view()),
    path('update_address', update_address.as_view()),
    path('delete_address', delete_address.as_view()),

    path('get_all_order', get_all_order.as_view()),
    path('get_certain_order', get_certain_order.as_view()),
    path('create_order_from_cart', create_order_from_cart.as_view()),
    path('create_order_from_product', create_order_from_product.as_view()),
    path('set_order_paid', set_order_paid.as_view()),
    path('cancel_order', cancel_order.as_view()),
    path('refund_order', refund_order.as_view()),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)