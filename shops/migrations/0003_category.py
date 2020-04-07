# Generated by Django 3.0.3 on 2020-03-03 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0002_shop_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('left_key', models.IntegerField()),
                ('right_key', models.IntegerField()),
                ('title', models.CharField(max_length=200)),
                ('depth', models.IntegerField()),
            ],
        ),
    ]