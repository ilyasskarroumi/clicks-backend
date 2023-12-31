# Generated by Django 4.2.6 on 2023-12-05 17:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0023_rename_payment_type_payment_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="user",
            field=models.OneToOneField(
                limit_choices_to={"role": "Client"},
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
