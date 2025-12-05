from django.contrib.auth import authenticate, login
from ninja import NinjaAPI
from ninja.security import django_auth
from ninja.pagination import paginate
from . import models, schemas
import datetime

api = NinjaAPI()

@api.post("/api/v1/auth/register")
def register_user(request, payload: schemas.RegistrationSchema):
    if models.User.objects.filter(username=payload.username).exists():
        return {"error": "Username already exists"}
    if models.Organization.objects.get(id=payload.organization_id) is None:
        return {"error": "No such organization"}
    user = models.User.objects.create_user(username=payload.username, password=payload.password)
    user.save()
    return {"success": True}

@api.post("/api/v1/auth/login")
def login_user(request, payload: schemas.LoginSchema):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is not None:
        login(request, user)
        return {"success": True}
    else:
        return {"error": "Invalid credentials"}

@api.get("/api/v1/tasks/", auth=django_auth, response=list[schemas.TaskSchema])
@paginate
def list_tasks(request):
    user = request.user
    tasks = models.Task.objects.filter(organization=user.organization).order_by(models.Task.deadline_datetime_with_tz, models.Task.priority)
    return tasks

@api.post("/api/v1/tasks/", auth=django_auth)
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
    
@api.put("/api/v1/tasks/", auth=django_auth)
def update_task(request, payload: schemas.TaskCreateSchema):
    task = models.Task.objects.get(id=payload.id)
    
    if task is None:
        return {"error": "Task does not exist"}
