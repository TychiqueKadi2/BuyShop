# Generated by Django 5.0.2 on 2025-04-23 17:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0003_remove_abstractcustomuser_is_verified_and_more"),
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="buyer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="product_bought",
                to="authentication.buyer",
            ),
        ),
    ]
