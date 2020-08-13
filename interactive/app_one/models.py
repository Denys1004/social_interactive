from django.db import models
import re													
from datetime import datetime
import bcrypt
from embed_video.fields import EmbedVideoField
import uuid

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')							
							
class UserManager(models.Manager):
    def register(self, postData, filedata):
        pw_hash = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt()).decode() # create the hash 

        # manage name of the file to prevent conflict
        # file_name = filedata['avatar'].name   #saving filename .name is like .png
        # new_name = f"{file_name.split('.')[0]}-{uuid.uuid4().hex}.{file_name.split('.')[-1]}" # adding random string to the name
        # filedata['avatar'].name = new_name    # reassigning the existing name to new name

        return self.create(
            first_name=postData['first_name'], 
            last_name=postData['last_name'], 
            # birth_date=postData['birth_date'], 
            email=postData['email'],
            # avatar = filedata['avatar'], 
            password=pw_hash
        )
    # Checking login 
    def authenticate(self, email, password):
        user_with_email = self.filter(email = email)
        if not user_with_email: # we quering for all users with this email, and if its empty list:
            return False
        user = user_with_email[0] # if we do have user with that email in our system:
        return bcrypt.checkpw(password.encode(), user.password.encode()) # checkpw returns True of False

    def validator(self, postData, user_id=None):												
        errors = {}																										
        # NAME VALIDATION 	
        if len(postData['first_name']) < 2:											
            errors['first_name'] = 'First name should be atleast 2 characters long.'	
        if not postData['first_name'].isalpha() and postData['first_name'] != '':
            errors['first_name'] = 'First name must containt only letters.'
        if len(postData['last_name']) < 2:										
            errors['last_name'] = 'Last name should be atleast 2 characters long'
        if not postData['last_name'].isalpha() and postData['first_name'] != '':
            errors['last_name'] = 'Last name must containt only letters.'
        # DATE VALIDATION
        if 'birth_date' in postData:
            if len(postData['birth_date']) < 1:	                							
                errors['birth_date'] = 'Birth date required.'
            else: 
                current_date = datetime.now()                                              
                date_from_form = postData['birth_date']
                converted_date_from_form = datetime.strptime(date_from_form, "%Y-%m-%d")
                duration = current_date - converted_date_from_form
                age = duration.days / 365.25
                if age < 13:										
                    errors['birth_date'] = 'User must be older then 13 years.'	
                if datetime.strptime(postData['birth_date'], '%Y-%m-%d') > datetime.now():
                    errors['birth_date'] = 'Date of birth should be in the past.'  
        # EMAIL VALIDATION
        if len(postData['email']) < 1:
            errors['email'] = "Email cannot be blank."
        if not EMAIL_REGEX.match(postData['email']): 
            errors['email'] = "Email is not valid"
        result =  self.filter(email = postData['email'])
        if len(result) > 0:
            if(user_id):   #if user_id is passed in, we're updating
                print('were updating')
                if(user_id !=result[0].id):
                    errors['email'] = "Email is already registered."
            else:
                errors['email'] = "Email is already registered."
        # PASSWORD VALIDATION
        if 'password' in postData:
            if len(postData['password']) < 3:
                errors['password'] = 'Password required, should be atleast 8 characters long.'
            if postData['password'] != postData['confirm_password']:
                errors['password'] = "Confirmation didn't match the password"
        return errors
    def update(self, user_id, postData, fileData):
        user=User.objects.get(id=user_id)
        # manage name of the file to prevent conflict
        file_name = fileData['avatar'].name   #saving filename .name is like .png
        new_name = f"{file_name.split('.')[0]}-{uuid.uuid4().hex}.{file_name.split('.')[-1]}" # adding random string to the name
        fileData['avatar'].name = new_name    # reassigning the existing name to new name

        user.first_name=postData['first_name']
        user.last_name=postData['last_name']
        user.birth_date=postData['birth_date']
        user.email=postData['email']
        user.avatar = fileData['avatar']
        user.phone_num=postData['phone_num']
        user.about=postData['about']
        user.save()
        return user

class User(models.Model):
    first_name = models.CharField(max_length = 255)										
    last_name = models.CharField(max_length = 255)	
    initials = 	models.CharField(max_length = 10, blank=True, null = True)						
    birth_date = models.DateField(null=True)	
    avatar = models.ImageField(upload_to='avatars', default='avatars/no_avatar.png')							
    email = models.TextField()
    phone_num = models.CharField(default='', max_length = 255)
    about = models.TextField(default='')
    password = models.TextField()	
    location = models.CharField(max_length = 255, blank=True, null = True)	
    has_message=models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add = True)  								
    updated_at = models.DateTimeField(auto_now = True)									
    objects = UserManager()
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class PostManager(models.Manager):
    def create_image_post(self, postData, fileData, poster_obj):
        # manage name of the file to prevent conflict
        file_name = fileData['files'].name   #saving filename .name is like .png
        new_name = f"{file_name.split('.')[0]}-{uuid.uuid4().hex}.{file_name.split('.')[-1]}" # adding random string to the name
        fileData['files'].name = new_name    # reassigning the existing name to new name
        return self.create(
            content = postData['content'],
            poster = poster_obj,
            post_image = fileData['files']
        )

class Post(models.Model):
    content = models.TextField()
    post_image = models.ImageField(upload_to='post_images', default=None, blank=True, null = True)
    poster = models.ForeignKey(User, related_name = 'poster', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)  								
    updated_at = models.DateTimeField(auto_now = True)	
    objects = PostManager()
    def __str__(self):
        return self.title if self.title else  'no-title, post of:  ' + self.poster.first_name + ' ' + self.poster.last_name

class Category(models.Model):
    name = models.CharField(max_length = 255)
    post = models.ManyToManyField(Post, related_name = 'categories')
    created_at = models.DateTimeField(auto_now_add = True)  								
    updated_at = models.DateTimeField(auto_now = True)
    def __str__(self):
        return self.name

class Comment(models.Model):
    comment = models.TextField(default = 'Hello')
    poster = models.ForeignKey(User, related_name = 'comments', on_delete=models.CASCADE) # Comments has a poster, User has comments
    post = models.ForeignKey(Post, related_name = 'comments', on_delete=models.CASCADE) # message where comment was posted on. Message has comments, but comment belongs to one message 
    created_at = models.DateTimeField(auto_now_add = True)  								
    updated_at = models.DateTimeField(auto_now = True)	
    def __str__(self):
        return f"{self.poster.first_name} {self.poster.last_name}: {self.comment}"

class Video_item(models.Model):
    video = EmbedVideoField()  # same like models.URLField()
    video_poster = models.ForeignKey(User, related_name = 'video_poster', on_delete=models.CASCADE, blank=True, null = True)
    post = models.ForeignKey(Post, related_name = 'videos', on_delete=models.CASCADE, blank=True, null = True) 
    created_at = models.DateTimeField(auto_now_add = True)  								
    updated_at = models.DateTimeField(auto_now = True)

class Conversation(models.Model):
    title = models.CharField(max_length=255, default="title")
    users = models.ManyToManyField(User, related_name = 'conversations')
    created_at = models.DateTimeField(auto_now_add = True)  								
    updated_at = models.DateTimeField(auto_now = True)

class Message(models.Model):
    content = models.TextField(default = 'Hello')
    poster = models.ForeignKey(User, related_name = 'messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name = 'messages', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)  								
    updated_at = models.DateTimeField(auto_now = True)