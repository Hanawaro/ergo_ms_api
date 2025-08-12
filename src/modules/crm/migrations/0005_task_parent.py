from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0004_remove_taskstatus_kanban_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='parent',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='subtasks',
                null=True,
                blank=True,
                to='crm.task',
                verbose_name='Родительская задача',
            ),
        ),
    ]
