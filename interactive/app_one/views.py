from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt
from datetime import datetime
from django.core.paginator import Paginator

from django.forms.models import model_to_dict # Need for sortation

def index(request):
    return redirect('/login')


def dashboard(request):
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'posts': Post.objects.all().order_by('-created_at'),
        'videos': Video_item.objects.all()
    }
    return render(request, 'dashboard.html', context)

# See profile
def user_profile(request, user_id):
    needed_user = User.objects.get(id=user_id)
    needed_user.birth_date = str(needed_user.birth_date)
    user_posts = needed_user.poster.all().order_by('-created_at')
    context = {
        'cur_user': User.objects.get(id = request.session['user_id']),
        'user':needed_user,
        'user_posts':user_posts
    }
    return render(request, 'profile.html', context)




# Update users profile
def update_profile(request, user_id):
    if request.method == "GET":
        cur_user = User.objects.get(id = user_id)
        cur_user.birth_date = str(cur_user.birth_date)
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

        updated_user = User.objects.update_profile(user_id, request.POST, request.FILES)
        return redirect(f'/user/{user_id}/profile')



# Register new user
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

# Login
def login(request):
    if request.method == "GET":
        if 'user_id' in request.session:
            request.session.clear()
            return render(request, "login.html")
        else:
            return render(request, "login.html")
    else:
        result = User.objects.authenticate(request.POST['email'],request.POST['password']) # Checking login
        if result == False:
            messages.error(request, "Email or passwort do not match.")
            return redirect('/login')
        else:
            request.session.clear()
            user = User.objects.get(email = request.POST['email'])
            request.session['user_id'] = user.id
            return redirect('/dashboard')
        


# CREATE NEW IMAGE POST
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

# CREATE NEW VIDEO POST
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


# CREATE NEW Text POST
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
        needed_conversation = False  #flag
        for conversation in sender.conversations.all():
            if receiver in conversation.users.all():
                needed_conversation = conversation  #flag will no longer be false
        if needed_conversation == False:
            #create new conversation
            needed_conversation = Conversation.objects.create(title =request.POST['content'][:50] )
            needed_conversation.users.add(receiver, sender)

        #create new message
        new_message = Message.objects.create(content = request.POST['content'],poster = sender, conversation=needed_conversation)
        receiver.has_message += 1
        receiver.save()

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
        if cur_user.has_message > 0:
            print("*****************************************")
            print(cur_user.messages.all())
            print("*****************************************")
            for message in cur_user.messages.all():

                if message.conversation == conversation:
                    cur_user.has_message -= 1 
                    if(cur_user.has_message == 0):
                        cur_user.save()
                        break
        context = {
            'cur_user': cur_user,
            'conversation': conversation,
            'receiver': receiver
        }
        return render(request, 'chat.html', context)
    else:
        #create new message
        new_message = Message.objects.create(content = request.POST['content'],poster = cur_user, conversation=conversation)
        receiver.has_message += 1
        receiver.save()
        conversation.title = new_message.content
        conversation.save()
        context = {
            'cur_user': cur_user,
            'conversation': conversation,
            'receiver': receiver
        }
        return render(request, 'chat.html', context)


def all_friends(request):
    context = {
        'all_users': User.objects.all(),
        'cur_user': User.objects.get(id = request.session['user_id'])
    }
    return render(request, 'all_users.html', context)

# LOGOUT
def logout(request):
    request.session.clear()
    return redirect("/login")
