from django.conf import settings
from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    UserProfile = apps.get_model("accounts", "UserProfile")

    existing_user_ids = set(UserProfile.objects.values_list("user_id", flat=True))
    profiles_to_create = []
    for user in User.objects.all():
        if user.id not in existing_user_ids:
            profiles_to_create.append(UserProfile(user=user))
    UserProfile.objects.bulk_create(profiles_to_create)


def remove_extra_profiles(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")
    UserProfile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, remove_extra_profiles),
    ]

