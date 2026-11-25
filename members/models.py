from django.db import models
from django.urls import reverse

from  .validators import mobile_validator, number_validator, indian_vehicle_reg_validator




# Create your models here.
class Flat (models.Model):
        flat_number     = models.CharField(max_length=3, 
                        verbose_name='Flat Number', 
                        validators = [number_validator],
                        )
        wing            = models.CharField(max_length=1)
        slug            = models.SlugField(unique = True, blank=True)

        def has_vehicle(self):
                if self.vehicle_set.count()>0:
                        return True
                else:
                        return False
        
        def vehicle_count(self):
                return self.vehicle_set.count()
        
        def save(self, *args, **kwargs):
                self.slug = (self.flat_number + self.wing)
                super (Flat, self).save(*args, **kwargs)

        class Meta:
                unique_together = ("flat_number", "wing")
        
        def get_absolute_url(self):
                return reverse('flat_detail', args=[(self.slug)])

        def __str__(self):
                return "{} {}".format( self.flat_number, self.wing)

class Guest (models.Model):
        flat_number     = models.OneToOneField(Flat, on_delete=models.CASCADE)
        first_name      = models.CharField(max_length = 200)
        last_name       = models.CharField(max_length = 200)
        mobile          = models.CharField(max_length = 10, 
                validators = [mobile_validator]
                )

        def __str__(self):
                return "{} {}".format(self.first_name, self.last_name)

        def full_name(self):
                return "{} {}".format(self.first_name, self.last_name)


class RentalStatus(models.Model):
        flat_number     = models.OneToOneField(Flat, on_delete=models.CASCADE)
        is_rented       = models.BooleanField(default =False)

        def __str__(self):
                if self.is_rented:
                        return "Rented"
                else:
                        return "Not Rented"


class Renter(models.Model):
        flat_number     = models.OneToOneField(Flat, on_delete=models.CASCADE)
        first_name      = models.CharField(max_length = 200)
        last_name       = models.CharField(max_length = 200)
        mobile          = models.CharField(max_length = 10, 
                validators = [mobile_validator]
                )
        
        def __str__(self):
                return "{} {}".format(self.first_name, self.last_name)

        def full_name(self):
                return "{} {}".format(self.first_name, self.last_name)

class Vehicle(models.Model):
        TYPE = (
                ("TWST", "Two Wheeler Stilt"),
                ("FWST", "Four Wheeler Stilt"),
                ("TWOU", "Two Wheeler Outside"),
                ("FWOU", "Four Wheeler Outside"),
        )
        vehicle         = models.CharField(max_length=4, choices=TYPE)
        flat            =models.ForeignKey(Flat, on_delete=models.CASCADE)
        registration_number = models.CharField(
                max_length=15,
                blank=True,
                default="",
                verbose_name="Registration Number",
                help_text="e.g. MH 02 AB 1234 or 22 BH 1234 AB",
                validators=[indian_vehicle_reg_validator],
        )
        make = models.CharField(max_length=50, blank=True, default="", verbose_name="Make")
        model = models.CharField(max_length=50, blank=True, default="", verbose_name="Model")

        def save(self, *args, **kwargs):
                if self.registration_number:
                        self.registration_number = " ".join(self.registration_number.strip().upper().split())
                if self.make:
                        self.make = self.make.strip()
                if self.model:
                        self.model = self.model.strip()
                super().save(*args, **kwargs)
        
        def __str__(self):
                parts = [str(self.flat), self.get_vehicle_display()]
                make_model = " ".join(p for p in (self.make, self.model) if p)
                if make_model:
                        parts.append("- " + make_model)
                if self.registration_number:
                        parts.append("({})".format(self.registration_number))
                return " ".join(parts)