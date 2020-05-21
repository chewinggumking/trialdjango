from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from .validators import mobile_validator

# Create your models here.

class SiteUserManager(BaseUserManager):
    #Method taken directly from documentation example
    def create_user(self, email, first_name, last_name, password = None):
        if not email:
            raise ValueError("User must enter a valid email address.")
        user = self.model(email = self.normalize_email(email),
                        first_name=first_name,
                        last_name=last_name)
        user.set_password(password)
        user.save(using =self._db)
        return user

    def create_staffuser(self, email, first_name, last_name, password):
        user = self.create_user(email = self.normalize_email(email),
                        first_name=first_name,
                        last_name=last_name,
                        password=password)
        user.staff = True
              
        user.save(using=self._db)
        return user
    

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email = self.normalize_email(email),
                        first_name=first_name,
                        last_name=last_name,
                        password=password)
        user.staff = True
        user.admin = True
        
        user.save(using=self._db)
        return user

    def full_name(self):
        return "{} {}".format(self.first_name, self.first_name)

class SiteUser(AbstractBaseUser):
    email       = models.EmailField(max_length=85, unique=True)
    mobile      = models.CharField(blank=False, max_length=10, validators=[mobile_validator])
    first_name  = models.CharField(blank=False, max_length=50)
    last_name   = models.CharField(blank=False, max_length=50)
    staff       = models.BooleanField(default=False)
    admin       = models.BooleanField(default=False)
    active      = models.BooleanField(default=True)

    objects = SiteUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return "{}    {} {}".format(self.email, self.first_name, self.last_name)

    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)        

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True    
    
    @property
    def is_staff(self):
        return self.staff
    
    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active