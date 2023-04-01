# Generated by Django 4.1 on 2023-03-29 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="camera_model",
            fields=[
                ("Main_id", models.AutoField(primary_key=True, serialize=False)),
                ("cam_id", models.IntegerField(blank=True, null=True, unique=True)),
                (
                    "ip",
                    models.CharField(
                        blank=True, default="None", max_length=122, null=True
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        blank=True, default="None", max_length=122, null=True
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        blank=True, default="None", max_length=122, null=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="profile_image",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("photo", models.ImageField(default="", upload_to="profile_images")),
                ("roll_num", models.IntegerField(blank=True, unique=True)),
                (
                    "name",
                    models.CharField(
                        blank=True, default="None", max_length=122, null=True
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        blank=True, default="None", max_length=122, null=True
                    ),
                ),
                (
                    "semester",
                    models.CharField(
                        blank=True, default="None", max_length=122, null=True
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True, default="None", max_length=122, null=True
                    ),
                ),
            ],
        ),
    ]
