# Generated by Django 4.2.6 on 2023-11-20 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_alter_creative_status_alter_page_status_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="voiceover",
            old_name="voice_over",
            new_name="creator",
        ),
        migrations.AlterField(
            model_name="creative",
            name="voice_over",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="creative_voice_over",
                to="api.voiceover",
            ),
        ),
    ]
