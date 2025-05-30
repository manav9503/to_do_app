# vercel_app.py
import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.urls import path
from django.shortcuts import render, redirect
from django.db import models
from django import forms
from django.http import HttpResponse

# Configure Django settings
settings.configure(
    DEBUG=False,
    SECRET_KEY='django-insecure-+j!p%*^!7#qy$5z@3r9v8b2m(xs5e&0k)l6o#n1i!d4h7g9f*',
    ROOT_URLCONF=__name__,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',  # Using /tmp for Vercel's writable storage
        }
    },
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(os.path.dirname(__file__), 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    STATIC_URL='/static/',
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
)

# Create models
class TodoItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'todo'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# Create forms
class TodoForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = ['title', 'description', 'completed']

# Create views
def todo_list(request):
    todos = TodoItem.objects.all()
    return render(request, 'todo_list.html', {'todos': todos})

def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
    else:
        form = TodoForm()
    return render(request, 'todo_form.html', {'form': form, 'title': 'Create Todo'})

def todo_update(request, pk):
    todo = TodoItem.objects.get(pk=pk)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo_form.html', {'form': form, 'title': 'Update Todo'})

def todo_delete(request, pk):
    todo = TodoItem.objects.get(pk=pk)
    if request.method == 'POST':
        todo.delete()
        return redirect('todo_list')
    return render(request, 'todo_confirm_delete.html', {'todo': todo})

# Configure URLs
urlpatterns = [
    path('', todo_list, name='todo_list'),
    path('create/', todo_create, name='todo_create'),
    path('update/<int:pk>/', todo_update, name='todo_update'),
    path('delete/<int:pk>/', todo_delete, name='todo_delete'),
]

# WSGI application
app = get_wsgi_application()

# Vercel serverless function handler
def handler(request):
    from io import BytesIO
    from django.core.handlers.wsgi import WSGIRequest
    from django.core.handlers.wsgi import WSGIHandler
    
    # Convert Vercel request to Django WSGI request
    environ = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string,
        'wsgi.input': BytesIO(request.body),
        'wsgi.url_scheme': request.headers.get('x-forwarded-proto', 'http'),
        'SERVER_NAME': request.headers.get('host', 'localhost'),
        'SERVER_PORT': request.headers.get('x-forwarded-port', '80'),
    }
    
    # Add headers
    for key, value in request.headers.items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Create WSGI request
    wsgi_request = WSGIRequest(environ)
    
    # Process request
    response = WSGIHandler()(wsgi_request)
    
    # Convert Django response to Vercel response
    return {
        'statusCode': response.status_code,
        'headers': dict(response.items()),
        'body': response.content.decode('utf-8'),
    }

# For local development
if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver'])
