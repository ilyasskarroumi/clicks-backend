# Generated by Django 4.2.6 on 2023-12-12 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0028_alter_page_creator"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="client",
            name="media_buyer",
        ),
        migrations.AddField(
            model_name="product",
            name="media_buyer",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"role": "Media Buyer"},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_media_buyer",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("New", "New"),
                    ("Awaiting Landing Page", "Awaiting Landing Page"),
                    ("Awaiting Creatives", "Awaiting Creatives"),
                    ("Published", "Published"),
                ],
                default="New",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Available", "Available"),
                    ("Busy", "Busy"),
                    ("Not Available", "Not Available"),
                ],
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="AOV",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_client",
                to="api.client",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="selling_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="sourcing_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="test_cpp",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
