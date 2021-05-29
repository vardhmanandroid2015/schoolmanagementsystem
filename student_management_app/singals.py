from .models import *
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            AdminHOD.objects.create(admin=instance)
        if instance.user_type == 2:
            Staffs.objects.create(admin=instance)
        if instance.user_type == 3:
            Students.objects.create(admin=instance)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        print("Signals - Going to add into admimnhod")
        instance.adminhod.save()
    if instance.user_type == 2:
        instance.staffs.save()
    if instance.user_type == 3:
        instance.students.save()