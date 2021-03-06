from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
import bcrypt, json
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import model_to_dict


#User functions#
def index(request):
    if 'user_id' in request.session:
        request.session.clear()
    return redirect('/login/')


# Create User
def create_user(request):
    if request.method == "GET":
        if 'user_id' in request.session:
            request.session.clear()
        return render(request, "register.html")
    else:
        request.session.clear()
        request.session.clear()
        request.session['first_name'] = request.POST['first_name']
        request.session['last_name'] = request.POST['last_name']
        request.session['email'] = request.POST['email']
        
        errors = User.objects.registration_validation(request.POST)	
        if len(errors)>0:													
            for value in errors.values():											
                messages.error(request, value)											
            return redirect('/register/')

        new_user = User.objects.registration(request.POST)
        request.session.clear()
        request.session['user_id'] = new_user.id
        return redirect('/dashboard/')


# Login
def login(request):
    if request.method == "GET":
        if 'user_id' in request.session:
            request.session.clear()
        return render(request, "login.html")
    else:
        result = User.objects.authenticate(request.POST['email'],request.POST['password']) # Checking login
        if result == False:
            messages.error(request, "Email or password do not match.")
            return redirect('/login/')
        else:
            request.session.clear()
            user = User.objects.get(email = request.POST['email'])
            request.session['user_id'] = user.id
            return redirect('/dashboard/')


# Logout
def logout(request):
    request.session.clear()
    return redirect("/login/")    


# Profile Page
def user_profile(request, user_id):
    needed_user = User.objects.get(id=user_id)
    user_posts = needed_user.poster.all().order_by('-created_at')
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'user':needed_user,
        'user_posts':user_posts,
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'profile.html', context)


# Update Profile Page
def update_profile(request, user_id):
    if request.method == "GET":
        cur_user=User.objects.get(id = user_id)
        cur_user.birth_date=str(cur_user.birth_date)
        context = {
            'cur_user': cur_user,
            'all_available_posts': Post.objects.all(),
            'all_users': User.objects.all(),
            'all_videos': Video_item.objects.all()
        }
        return render(request, 'update_profile.html', context)
    else:
        errors = User.objects.update_profile_validation(request.POST, user_id)	
        if len(errors)>0:													
            for value in errors.values():											
                messages.error(request, value)											
            return redirect(f'/update_profile/{user_id}/')

        updated_user = User.objects.update_profile(user_id, request.POST, request.FILES)
        return redirect(f'/user/{user_id}/profile/')


# Dashboard Page
def dashboard(request):
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'posts': Post.objects.all().order_by('-created_at'),
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'dashboard.html', context)


# All Users Page
def all_friends(request):
    context = {
        'all_users': User.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id']),
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'all_users.html', context)


# Posts
def create_post(request, post_type):
    poster = User.objects.get(id = request.session['user_id'])
    if post_type=='text':
        Post.objects.create(content = request.POST['editor1'], poster = poster)
    elif post_type=='image':
        Post.objects.create_image_post(request.POST, request.FILES, poster)
    elif post_type=='video':
        new_post=Post.objects.create(content = request.POST['content'], poster = poster)
        Video_item.objects.create(video = request.POST['video_item'], post = new_post, video_poster = poster )
    elif post_type=='music':
        new_post = Post.objects.create_music_post(request.POST, request.FILES, poster)
    return redirect(f'/user/{poster.id}/profile/')


# Post add comment
def add_comment(request, post_id):
    needed_post = Post.objects.get(id = post_id)
    comment_poster = User.objects.get(id = request.session['user_id'])
    Comment.objects.create(comment=request.POST['comment'], poster = comment_poster, post = needed_post)
    return redirect('/dashboard/')


# Post comment with Ajax
def post_comment_with_ajax(request):
    needed_post = Post.objects.get(id = request.POST['post_id'])
    comment_poster = User.objects.get(id = request.session['user_id'])
    Comment.objects.create(comment=request.POST['comment'], poster = comment_poster, post = needed_post)
    all_posts_comments = needed_post.comments.all()
    context = {
        'current_post_comments':all_posts_comments,
        'cur_user': User.objects.get(id = request.session['user_id']),
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all(),
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'comments_partial.html', context)


# LIKES
def add_like(request, post_id):
    user_liking = User.objects.get(id = request.session['user_id'])
    post_liked = Post.objects.get(id = post_id)
    if post_liked.videos.all():
        video_liked = Video_item.objects.get(post = post_liked)
        context = {
            'video_liked':video_liked,
            'posts': Post.objects.all().order_by('-created_at'),
            'videos': Video_item.objects.all(),
            'cur_user': User.objects.get(id = request.session['user_id']),
            'all_available_posts': Post.objects.all(),
            'all_users': User.objects.all(),
            'all_videos': Video_item.objects.all()
        }
    post_liked.likes.add(user_liking)
    context = {
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id']),
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return HttpResponse(json.dumps(post_liked.likes.count()), content_type = 'application/json')


# Delete like
def remove_like(request, post_id):
    user_liking = User.objects.get(id = request.session['user_id'])
    post_liked = Post.objects.get(id = post_id)
    if post_liked.videos.all():
        video_liked = Video_item.objects.get(post = post_liked)
        context = {
            'video_liked':video_liked,
            'posts': Post.objects.all().order_by('-created_at'),
            'videos': Video_item.objects.all(),
            'cur_user': User.objects.get(id = request.session['user_id']),
            'all_available_posts': Post.objects.all(),
            'all_users': User.objects.all(),
            'all_videos': Video_item.objects.all()
        }
    post_liked.likes.remove(user_liking)
    context = {
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id']),
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return HttpResponse(json.dumps(post_liked.likes.count()), content_type = 'application/json')


# Conversation Page
def send_message(request, user_id):
    receiver = User.objects.get(id = user_id)
    sender = User.objects.get(id = request.session['user_id'])
    if request.method == "GET":
        context = {
            'cur_user': User.objects.get(id = request.session['user_id']),
            'receiver': receiver,
            'sender': sender,
            'all_available_posts': Post.objects.all(),
            'all_users': User.objects.all(),
            'all_videos': Video_item.objects.all()
        }
        return render(request, 'send_message.html', context)
    else:
        conversation_exists = False  #flag
        for conversation in sender.conversations.all():
            if receiver in conversation.users.all():
                conversation_exists = conversation  #flag will no longer be false

        if conversation_exists == False:
            #create new conversation
            needed_conversation = Conversation.objects.create(title =request.POST['content'][:50] )
            needed_conversation.users.add(receiver, sender)
        else:
            needed_conversation = conversation_exists
        
        #tells receiver they have a message
        receiver.has_message+=1
        receiver.save()

        #create new message
        new_message = Message.objects.create(content = request.POST['content'],poster = sender, conversation=needed_conversation)
        new_message.receivers.add(receiver)
        needed_conversation.title = new_message.content
        needed_conversation.save()

        return redirect(f'/chat/{needed_conversation.id}/{receiver.id}/')


# Display New Message
def display_messages(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    conversations = cur_user.conversations.all().order_by('-updated_at')
    context = {
        'cur_user': cur_user,
        'conversations': conversations,
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'display_conversations.html', context)


# Chat
def chat(request, conv_id, receiver_id):
    cur_user = User.objects.get(id = request.session['user_id'])
    conversation = Conversation.objects.get(id = conv_id)
    receiver = User.objects.get(id = receiver_id)

    if request.method == "GET":
        #receiver has read conversation remove all messages in this conversation from has_message count
        if(cur_user.has_message>0):
            new_messages=cur_user.inbox.all().filter(conversation=conversation) #filter all messages in users inbox by conversation that was clicked
            cur_user.has_message-=len(new_messages) #reduce has_message count by number of new messages found
            cur_user.save()
            for message in new_messages:        #remove all new messages from inbox
                cur_user.inbox.remove(message)
        context = {
            'cur_user': cur_user,
            'conversation': conversation,
            'receiver': receiver,
            'all_available_posts': Post.objects.all(),
            'all_users': User.objects.all(),
            'all_videos': Video_item.objects.all()
        }
        return render(request, 'chat.html', context)
    else:
        #create new message
        if len(request.POST['content']) < 1:
            return redirect(f'/chat/{conv_id}/{receiver_id}/')
        new_message = Message.objects.create(content = request.POST['content'],poster = cur_user, conversation=conversation)
        new_message.receivers.add(receiver)
        conversation.title = new_message.content
        conversation.save()

        #tells receiver they have a message
        receiver.has_message+=1
        receiver.save()
        response={
            'name':f'{new_message.poster.first_name} {new_message.poster.last_name}',
            'avatar':str(new_message.poster.avatar),
            'message':new_message.content,
            'time':new_message.created_at.strftime('%b %d, %I:%M%p'),
            'poster_id': f'{new_message.poster.id}'
        }

        return HttpResponse(json.dumps(response))


# Display Music Page
def music(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    all_posts = Post.objects.exclude(poster = cur_user )
    context = {
        'cur_user':cur_user,
        'all_posts':all_posts,
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'music.html', context)


# Display Images Page
def images(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    all_posts = Post.objects.exclude(poster = cur_user )
    context = {
        'cur_user':cur_user,
        'all_posts':all_posts,
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'images.html', context)


# Display Video Page
def video(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    all_videos = Video_item.objects.exclude(video_poster = cur_user)
    context = {
        'cur_user':cur_user,
        'all_users_videos':all_videos,
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'video.html', context)


# Delete Post
def delete_post(request, post_id):
    to_delete = Post.objects.get(id = post_id)
    to_delete.delete()
    return redirect('/dashboard/')


# Delete Comment
def delete_comment(request, comment_id):
    comment = Comment.objects.get(id = comment_id)
    needed_post = comment.post
    comment.delete()
    all_posts_comments = needed_post.comments.all()
    context = {
        'current_post_comments':all_posts_comments,
        'cur_user': User.objects.get(id = request.session['user_id']),
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all(),
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'comments_partial.html', context)


# search bar in All Users
def zapros(request):
    zapros = request.GET['zapros']
    result = Post.objects.filter(Q(first_name__icontains=zapros,) | Q(last_name__icontains = zapros))
    context = {
        'zapros':zapros,
        'cur_user': User.objects.get(id = request.session['user_id']),
        'result': result,
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'zapros.html', context)

def main_search_bar(request):
    results = request.GET['results']
    result = Post.objects.filter(Q(content__icontains=results))
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'post_results': result,
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'search_result.html', context)

# Check for new messages
def check_mess(request, mess_id):
    mess = Message.objects.get(id = mess_id)
    conversation = mess.conversation
    all_messages = conversation.messages.all()
    all_new_mess = all_messages.filter(id__gt = int(mess_id))
    if len(all_new_mess)  == 0:
        return HttpResponse(json.dumps([]), content_type = 'application/json')
    else:
        response = []
        for new_mess in all_new_mess:
            message = {}
            message['name'] = f'{new_mess.poster.first_name} {new_mess.poster.last_name}',
            message['avatar'] = str(new_mess.poster.avatar),
            message['message'] = new_mess.content,
            message['time'] = new_mess.created_at.strftime('%b %d, %I:%M%p'),
            message['poster_id'] = f'{new_mess.poster.id}',
            message['mess_id'] = new_mess.id

            response.append(message)
       
        return HttpResponse(json.dumps(response))  