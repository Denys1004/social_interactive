from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('register', views.create_user),
    path('dashboard', views.dashboard),
    
    path('create_post/<str:post_type>', views.create_post),

    path('user/<int:user_id>/profile', views.user_profile),
    path('update_profile/<int:user_id>', views.update_profile),

    path('music', views.music),
    path('images', views.images),
    path('video', views.video),

    path('all_friends', views.all_friends),

    path('add_comment/post/<int:post_id>', views.add_comment),

    path('delete/post/<int:post_id>', views.delete_post),
    path('delete/comment/<int:comment_id>', views.delete_comment),
    path('post_comment', views.post_comment_with_ajax),

    #messages
    path('messages', views.display_messages),
    path('send_to/<int:user_id>', views.send_message),

    path('chat/<int:conv_id>/<int:receiver_id>', views.chat),

    path('like/<int:post_id>', views.add_like),
    path('unlike/<int:post_id>', views.remove_like),

    path('logout', views.logout)
]
