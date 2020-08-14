from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt
from datetime import datetime
from django.core.paginator import Paginator

from django.forms.models import model_to_dict

#User functions_____________________________________________________________________________________________________________________#
def index(request):
    return redirect('/login')

def create_user(request):
    if request.method == "GET":
        return render(request, "register.html")
    else:
        request.session.clear()
        request.session['first_name'] = request.POST['first_name']
        request.session['last_name'] = request.POST['last_name']
        request.session['email'] = request.POST['email']
        
        errors = User.objects.registration_validation(request.POST)	
        if len(errors)>0:													
            for value in errors.values():											
                messages.error(request, value)											
            return redirect('/register')

        new_user = User.objects.registration(request.POST)
        request.session.clear()
        request.session['user_id'] = new_user.id
        request.session['initials'] = new_user.first_name[0] + new_user.last_name[0]
        return redirect('/dashboard')

def login(request):
    if request.method == "GET":
        request.session.clear()
        return render(request, "login.html")
    else:
        result = User.objects.authenticate(request.POST['email'],request.POST['password']) # Checking login
        if result == False:
            messages.error(request, "Email or password do not match.")
            return redirect('/login')
        else:
            request.session.clear()
            user = User.objects.get(email = request.POST['email'])
            request.session['user_id'] = user.id
            request.session['initials'] = user.first_name[0] + user.last_name[0]
            return redirect('/dashboard')

def logout(request):
    request.session.clear()
    return redirect("/login")    

def user_profile(request, user_id):
    needed_user = User.objects.get(id=user_id)
    user_posts = needed_user.poster.all().order_by('-created_at')
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'user':needed_user,
        'user_posts':user_posts
    }
    return render(request, 'profile.html', context)

def update_profile(request, user_id):
    if request.method == "GET":
        cur_user=User.objects.get(id = user_id)
        cur_user.birth_date=str(cur_user.birth_date)
        context = {
            'cur_user': cur_user
        }
        return render(request, 'update_profile.html', context)
    else:
        errors = User.objects.update_profile_validation(request.POST, user_id)	
        if len(errors)>0:													
            for value in errors.values():											
                messages.error(request, value)											
            return redirect(f'/update_profile/{user_id}')

        updated_user = User.objects.update(user_id, request.POST, request.FILES)
        return redirect(f'/user/{user_id}/profile')

#Independent Pages__________________________________________________________________________________________________________________#
def dashboard(request):
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all()
    }
    return render(request, 'dashboard.html', context)

def all_friends(request):
    context = {
        'all_users': User.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id'])
    }
    return render(request, 'all_users.html', context)

#Posts______________________________________________________________________________________________________________________________#
def create_new_image_post(request):
    if request.method == "GET":
        context = {
            'videos': Video_item.objects.all(),
            'cur_user': User.objects.get(id = request.session['user_id']),
        }
        return redirect('/dashboard')
    else:
        poster = User.objects.get(id = request.session['user_id'])
        new_post = Post.objects.create_image_post(request.POST, request.FILES, poster)
        return redirect('/dashboard')

def create_new_video_post(request):
    if request.method == "GET":
        context = {
            'videos': Video_item.objects.all(),
            'cur_user': User.objects.get(id = request.session['user_id']),
        }
        return redirect('/dashboard')
    else:
        poster = User.objects.get(id = request.session['user_id'])
        new_post = Post.objects.create(content = request.POST['content'], poster = poster)
        new_video = Video_item.objects.create(video = request.POST['video_item'], post = new_post, video_poster = poster )
        return redirect('/dashboard')

def create_new_text_post(request):
    if request.method == "GET":
        context = {
            'videos': Video_item.objects.all(),
            'cur_user': User.objects.get(id = request.session['user_id']),
        }
        return redirect('/dashboard')
    else:
        poster = User.objects.get(id = request.session['user_id'])
        new_post = Post.objects.create(content = request.POST['editor1'], poster = poster)
        return redirect(f'/user/{poster.id}/profile')

# LIKES_____________________________________________________________________________________________________________________________#
def add_like(request, post_id):
    user_liking = User.objects.get(id = request.session['user_id'])
    post_liked = Post.objects.get(id = post_id)
    if post_liked.videos.all():
        video_liked = Video_item.objects.get(post = post_liked)
        context = {
            'video_liked':video_liked,
            'posts': Post.objects.all().order_by('-created_at'),
            'videos': Video_item.objects.all(),
            'cur_user': User.objects.get(id = request.session['user_id'])
        }
    post_liked.likes.add(user_liking)
    context = {
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id'])
    }
    return redirect('/dashboard')

def remove_like(request, post_id):
    user_liking = User.objects.get(id = request.session['user_id'])
    post_liked = Post.objects.get(id = post_id)
    if post_liked.videos.all():
        video_liked = Video_item.objects.get(post = post_liked)
        context = {
            'video_liked':video_liked,
            'posts': Post.objects.all().order_by('-created_at'),
            'videos': Video_item.objects.all(),
            'cur_user': User.objects.get(id = request.session['user_id'])
        }
    post_liked.likes.remove(user_liking)
    context = {
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id'])
    }
    return redirect('/dashboard')


def add_comment(request, post_id):
    needed_post = Post.objects.get(id = post_id)
    comment_poster = User.objects.get(id = request.session['user_id'])
    Comment.objects.create(comment=request.POST['comment'], poster = comment_poster, post = needed_post)
    return redirect('/dashboard')

def post_comment_with_ajax(request):
    needed_post = Post.objects.get(id = request.POST['post_id'])
    comment_poster = User.objects.get(id = request.session['user_id'])
    Comment.objects.create(comment=request.POST['comment'], poster = comment_poster, post = needed_post)
    all_posts_comments = needed_post.comments.all()
    context = {
        'current_post_comments':all_posts_comments,
        'cur_user': User.objects.get(id = request.session['user_id']),
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all()
    }
    return render(request, 'comments_partial.html', context)

#Conversation functions_____________________________________________________________________________________________________________#
def send_message(request, user_id):
    receiver = User.objects.get(id = user_id)
    sender = User.objects.get(id = request.session['user_id'])
    if request.method == "GET":
        context = {
            'cur_user': User.objects.get(id = request.session['user_id']),
            'receiver': receiver,
            'sender': sender
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
        
        #tells receiver they have a message
        receiver.has_message+=1
        receiver.save()

        #create new message
        new_message = Message.objects.create(content = request.POST['content'],poster = sender, conversation=needed_conversation)
        new_message.receivers.add(receiver)
        needed_conversation.title = new_message.content
        needed_conversation.save()

        return redirect(f'/chat/{needed_conversation.id}/{receiver.id}')

def display_messages(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    conversations = cur_user.conversations.all().order_by('-updated_at')
    context = {
        'cur_user': cur_user,
        'conversations': conversations
    }
    return render(request, 'display_conversations.html', context)

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
            'receiver': receiver
        }
        return render(request, 'chat.html', context)
    else:
        #create new message
        new_message = Message.objects.create(content = request.POST['content'],poster = cur_user, conversation=conversation)
        new_message.receivers.add(receiver)
        conversation.title = new_message.content
        conversation.save()

        #tells receiver they have a message
        receiver.has_message+=1
        receiver.save()

        context = {
            'cur_user': cur_user,
            'conversation': conversation,
            'receiver': receiver
        }
        return render(request, 'chat.html', context)