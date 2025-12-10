from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import FieldDoesNotExist, ValidationError
from .tenant import get_current_organization


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, organization, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")
        if not organization:
            raise ValueError("Organization ID is required")
        
        if hasattr(organization, "id"):
            org = organization
        else:
            try:
                org = Organization.objects.get(id=organization)
            except Organization.DoesNotExist:
                raise ValueError(f"Organization with id {organization} does not exist")
        
        user = self.model(username=username, organization=org, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password, organization=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if organization is None:
            org, _ = Organization.objects.get_or_create(name="Default Organization")
            organization = org
            
        return self.create_user(username, password, organization, **extra_fields)

class TenantQuerySet(models.QuerySet):
    def for_current_organization(self):
        org = get_current_organization()
        
        if org is None:
            return self
        
        try:
            self.model._meta.get_field("organization")
        except FieldDoesNotExist:
            return self
        
        return self.filter(organization=org)


class TenantManager(models.Manager):    
    def get_queryset(self):
        qs = TenantQuerySet(model=self.model, using=self._db)
        
        return qs.for_current_organization()

class TenantUserManager(CustomUserManager):    
    def get_queryset(self):
        qs = TenantQuerySet(model=self.model, using=self._db)
        return qs.for_current_organization()
    
    def all_tenants(self):
        return super().get_queryset()


class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    objects = TenantUserManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = [['username', 'organization']]

    def __str__(self):
        return f"{self.username} ({self.organization.name})"


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline_datetime_with_tz = models.DateTimeField()
    priority = models.IntegerField()

    objects = TenantManager()
    all_objects = models.Manager()
    
    class Meta:
        indexes = [
            models.Index(
                fields=['organization', 'deadline_datetime_with_tz', 'priority'], 
                name='task_tenant_order_idx'
            ),
        ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.organization_id:
            org = get_current_organization()
            if org:
                self.organization = org
        
        if self.assigned_to and self.assigned_to.organization_id != self.organization_id:
            raise ValueError("Cannot assign task to user from different organization")
        
        super().save(*args, **kwargs)