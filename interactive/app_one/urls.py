from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('register', views.create_user),
    path('dashboard', views.dashboard),
    path('user/<int:user_id>/profile', views.user_profile),
    path('update_profile/<int:user_id>', views.update_profile),
    path('music', views.music),
    path('images', views.images),
    path('video', views.video),
    path('all_friends', views.all_friends),

    path('zapros', views.zapros),
    
    path('create_post/<str:post_type>', views.create_post),
    path('delete/post/<int:post_id>', views.delete_post),
    path('like/<int:post_id>', views.add_like),
    path('unlike/<int:post_id>', views.remove_like),

    path('post_comment', views.post_comment_with_ajax),
    path('delete/comment/<int:comment_id>', views.delete_comment),

    #messages
    path('messages', views.display_messages),
    path('chat/<int:conv_id>/<int:receiver_id>', views.chat),
    path('check_mess/<int:mess_id>', views.check_mess),
    
    path('logout', views.logout)
]
