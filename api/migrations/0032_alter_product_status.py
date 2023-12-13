# Generated by Django 4.2.6 on 2023-12-13 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0031_alter_product_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("New", "New"),
                    ("Not Approved", "Not Approved"),
                    ("Approved", "Approved"),
                    ("Awaiting Landing Page", "Awaiting Landing Page"),
                    ("Awaiting Creatives", "Awaiting Creatives"),
                    ("Published", "Published"),
                ],
                default="New",
                max_length=30,
                null=True,
            ),
        ),
    ]
