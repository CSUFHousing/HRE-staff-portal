# Generated by Django 2.0.7 on 2018-12-26 04:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_auto_20170827_0117'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ['user__last_name']},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['sent_date', 'to__user__last_name']},
        ),
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['-published_date']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-published_date']},
        ),
        migrations.AlterField(
            model_name='employee',
            name='supervisor',
            field=models.ForeignKey(blank=True, limit_choices_to={'user__is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portal.Employee'),
        ),
        migrations.AlterField(
            model_name='post',
            name='last_published_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'user__is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portal.Employee'),
        ),
    ]
