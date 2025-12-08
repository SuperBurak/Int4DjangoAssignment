from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from ninja.security import django_auth
from ninja.pagination import paginate
from . import models, schemas
import datetime

api = NinjaAPI()

@api.post("/api/v1/auth/login")
def login_user(request, payload: schemas.LoginSchema):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is not None:
        login(request, user)
        return {"success": True}
    else:
        return {"error": "Invalid credentials"}

@api.get("/api/v1/tasks/", auth=django_auth, response=list[models.Task])
@paginate
@login_required
def list_tasks(request):
    return models.Task.objects.filter(organization=request.user.organization).order_by(models.Task.deadline_datetime_with_tz, models.Task.priority)


@api.post("/api/v1/tasks/", auth=django_auth)
@login_required
def create_task(request, payload: schemas.TaskCreateSchema):
    if request.user.organization != payload.assigned_to.organization:
        return 401, {"error": "User does not belong to your organization"}
    
    try:
        task = models.Task.objects.create(
            title = payload.title,
            description = payload.description,
            completed = payload.completed,
            deadline_datetime_with_tz = payload.deadline_datetime_with_tz,
            priority = payload.priority,
            assigned_to = payload.user,
            organization = request.user.organization,
            created_at = datetime.datetime.now())
        
        task.save()
        return {"success": True}
    except Exception as e:
        return {"error": e}
    
@api.put("/api/v1/tasks/{task_id}", auth=django_auth)
@login_required
def update_task(request, task_id: int, payload: schemas.TaskUpdateSchema):
    if request.user.organization != payload.assigned_to.organization:
        return 401, {"error": "User does not belong to your organization"}
    
    task = get_object_or_404(models.Task, id=task_id)
    
    task.title = payload.title
    task.description = payload.description
    task.completed = payload.completed
    task.deadline_datetime_with_tz = payload.deadline_datetime_with_tz
    task.priority = payload.priority
    task.assigned_to = payload.assigned_to
    
    task.save()

    return {"success": True, "task_id": task.id}
    
@api.delete("/api/v1/tasks/{task_id}", auth=django_auth)
@login_required
def delete_task(request, task_id: int):
    if request.user.organization != payload.assigned_to.organization:
        return 401, {"error": "User does not belong to your organization"}
    
    task = get_object_or_404(models.Task, id=task_id)
    
    task.delete()
    
    return {"success": True, "task_id": task.id}

@api.get("api/v1/users/", auth=django_auth, response=list[schemas.UserSchema])
@login_required
def get_users(request):
    return models.User.objects.filter(organization=request.user.organization)
        
@api.post("/api/v1/users/", auth=django_auth)
@login_required
def register_user(request, payload: schemas.RegistrationSchema):
    if models.User.objects.filter(username=payload.username).exists():
        return {"error": "Username already exists"}
    if models.Organization.objects.get(id=payload.organization_id) is None:
        return {"error": "No such organization"}
    
    user = models.User.objects.create_user(username=payload.username, password=payload.password, organization=request.user.organization)
    
    user.save()
    
    return {"success": True}
