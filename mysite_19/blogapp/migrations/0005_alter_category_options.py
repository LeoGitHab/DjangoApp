# Generated by Django 4.2.1 on 2023-10-06 04:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blogapp", "0004_alter_article_pub_date_alter_article_tags"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"verbose_name": "Category", "verbose_name_plural": "Categories"},
        ),
    ]
