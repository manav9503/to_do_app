# todo_app.py
import os
import sys
from django.conf import settings
from django.core.management import execute_from_command_line
from django.urls import path
from django.shortcuts import render, redirect
from django.db import models
from django import forms

# Configure Django settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='django-insecure-+j!p%*^!7#qy$5z@3r9v8b2m(xs5e&0k)l6o#n1i!d4h7g9f*',
    ROOT_URLCONF=__name__,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
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

# Create templates directory and files
if not os.path.exists('templates'):
    os.makedirs('templates')

# Base template
with open('templates/base.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Django To-Do App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        {% block content %}
        {% endblock %}
    </div>
</body>
</html>
''')

# Todo list template
with open('templates/todo_list.html', 'w') as f:
    f.write('''{% extends 'base.html' %}

{% block content %}
    <h1 class="mb-4">To-Do List</h1>
    <a href="{% url 'todo_create' %}" class="btn btn-primary mb-3">Add New Todo</a>
    
    <div class="list-group">
        {% for todo in todos %}
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="mb-1 {% if todo.completed %}text-decoration-line-through{% endif %}">
                        {{ todo.title }}
                    </h5>
                    <p class="mb-1">{{ todo.description }}</p>
                    <small>Created: {{ todo.created_at|date:"M d, Y H:i" }}</small>
                </div>
                <div>
                    <a href="{% url 'todo_update' todo.pk %}" class="btn btn-sm btn-outline-secondary">Edit</a>
                    <a href="{% url 'todo_delete' todo.pk %}" class="btn btn-sm btn-outline-danger">Delete</a>
                </div>
            </div>
        {% empty %}
            <div class="alert alert-info">No todos yet. Add one!</div>
        {% endfor %}
    </div>
{% endblock %}
''')

# Todo form template
with open('templates/todo_form.html', 'w') as f:
    f.write('''{% extends 'base.html' %}

{% block content %}
    <h1 class="mb-4">{{ title }}</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Save</button>
        <a href="{% url 'todo_list' %}" class="btn btn-secondary">Cancel</a>
    </form>
{% endblock %}
''')

# Delete confirmation template
with open('templates/todo_confirm_delete.html', 'w') as f:
    f.write('''{% extends 'base.html' %}

{% block content %}
    <h1 class="mb-4">Confirm Delete</h1>
    <p>Are you sure you want to delete "{{ todo.title }}"?</p>
    <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Delete</button>
        <a href="{% url 'todo_list' %}" class="btn btn-secondary">Cancel</a>
    </form>
{% endblock %}
''')

# Initialize the database
if __name__ == '__main__':
    # Create database tables
    from django.db.utils import OperationalError
    try:
        TodoItem.objects.all().exists()
    except OperationalError:
        from django.core.management.commands.migrate import Command as MigrateCommand
        migrate = MigrateCommand()
        migrate.run_from_argv(['manage.py', 'migrate'])
        
        # Create a custom migration for our model
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        executor = MigrationExecutor(connection)
        if not executor.migration_plan(executor.loader.graph.leaf_nodes()):
            from django.db.migrations.state import ProjectState
            from django.db.migrations import Migration
            from django.db.migrations.operations.models import CreateModel
            
            class CustomMigration(Migration):
                operations = [
                    CreateModel(
                        name='TodoItem',
                        fields=[
                            ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                            ('title', models.CharField(max_length=200)),
                            ('description', models.TextField(blank=True)),
                            ('completed', models.BooleanField(default=False)),
                            ('created_at', models.DateTimeField(auto_now_add=True)),
                            ('updated_at', models.DateTimeField(auto_now=True)),
                        ],
                    ),
                ]
            
            migration = CustomMigration('custom', 'todo')
            executor.apply_migration(ProjectState(), migration)
    
    # Run the development server
    execute_from_command_line(sys.argv)
