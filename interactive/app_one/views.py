from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
import bcrypt, json
from datetime import datetime
from django.db.models import Q
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
            request.session['user_id'] = User.objects.get(email = request.POST['email']).id
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
        'user_posts':user_posts,
    }
    return render(request, 'profile.html', context)

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
            return redirect(f'/update_profile/{user_id}')

        updated_user = User.objects.update_profile(user_id, request.POST, request.FILES)
        return redirect(f'/user/{user_id}/profile')

#Independent Pages__________________________________________________________________________________________________________________#
def dashboard(request):
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'posts': Post.objects.all().order_by('-created_at'),
        'all_available_posts': Post.objects.all(),
        'all_users': User.objects.all(),
        'all_videos': Video_item.objects.all()
    }
    return render(request, 'dashboard.html', context)

def all_friends(request):
    context = {
        'all_users': User.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id']),
    }
    return render(request, 'all_users.html', context)

#Posts______________________________________________________________________________________________________________________________#
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
    return redirect(f'/user/{poster.id}/profile')

def post_comment_with_ajax(request):
    needed_post = Post.objects.get(id = request.POST['post_id'])
    comment_poster = User.objects.get(id = request.session['user_id'])
    Comment.objects.create(comment=request.POST['comment'], poster = comment_poster, post = needed_post)
    all_posts_comments = needed_post.comments.all()
    context = {
        'current_post_comments':all_posts_comments,
        'cur_user': comment_poster,
    }
    return render(request, 'comments_partial.html', context)

# LIKES_____________________________________________________________________________________________________________________________#
def add_like(request, post_id):
    cur_user = User.objects.get(id = request.session['user_id'])
    post = Post.objects.get(id = post_id)
    post.likes.add(cur_user)

    return HttpResponse(json.dumps(post.likes.count()))

def remove_like(request, post_id):
    cur_user = User.objects.get(id = request.session['user_id'])
    post = Post.objects.get(id = post_id)
    post.likes.remove(cur_user)

    return HttpResponse(json.dumps(post.likes.count()))

#Conversation ______________________________________________________________________________________________________________________#
def display_messages(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    conversations = cur_user.conversations.all().order_by('-updated_at')
    context = {
        'cur_user': cur_user,
        'conversations': conversations,
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
            'receiver': receiver,
        }
        return render(request, 'chat.html', context)
    else:
        #create new message
        if len(request.POST['content']) < 1:
            return redirect(f'/chat/{conv_id}/{receiver_id}')
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
            'poster_id': new_message.poster.id,
            'message_id': new_message.id
        }

        return HttpResponse(json.dumps(response))

def music(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    all_posts = Post.objects.exclude(poster = cur_user )
    context = {
        'cur_user':cur_user,
        'all_posts':all_posts,
    }
    return render(request, 'music.html', context)

def images(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    all_posts = Post.objects.exclude(poster = cur_user )
    context = {
        'cur_user':cur_user,
        'all_posts':all_posts,
    }
    return render(request, 'images.html', context)


def video(request):
    cur_user = User.objects.get(id = request.session['user_id'])
    all_videos = Video_item.objects.exclude(video_poster = cur_user)
    context = {
        'cur_user':cur_user,
        'all_videos':all_videos,
    }
    return render(request, 'video.html', context)


def delete_post(request, post_id):
    post = Post.objects.get(id = post_id).delete()
    return redirect('/dashboard')

def delete_comment(request, comment_id):
    comment = Comment.objects.get(id = comment_id).delete()
    
    post = comment.post
    comments = post.comments.all()
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'current_post_comments':comments,
    }
    return render(request, 'comments_partial.html', context)

def zapros(request):
    zapros = request.GET['zapros']
    result = User.objects.filter(Q(first_name__icontains=zapros,) | Q(last_name__icontains = zapros))
    context = {
        'zapros':zapros,
        'result': result,
    }
    return render(request, 'zapros.html', context)

def check_mess(request, mess_id):
    message = Message.objects.get(id = mess_id)
    conversation = message.conversation
    all_messages = conversation.messages.all()

    new_messages = all_messages.filter(id__gt = int(mess_id))
    if len(new_messages)  == 0:
        return HttpResponse(json.dumps([]), content_type = 'application/json')
    else:
        response = []
        for message in new_messages:
            temp = {}
            temp['name'] = f'{message.poster.first_name} {message.poster.last_name}'
            temp['avatar'] = str(message.poster.avatar)
            temp['message'] = message.content
            temp['time'] = message.created_at.strftime('%b %d, %I:%M%p')
            temp['poster_id'] = message.poster.id
            temp['mess_id'] = message.id

            response.append(temp)
        print('before convert*'*30)
        print(response)
        print('*'*30)

        print('after convert*'*30)
        print(json.dumps(response))
        print('*'*30)
       
        return HttpResponse(json.dumps(response))    