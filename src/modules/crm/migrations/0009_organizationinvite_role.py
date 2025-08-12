from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0008_alter_organization_id_alter_organization_members_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationinvite',
            name='role',
            field=models.CharField(
                choices=[('owner','owner'),('admin','admin'),('member','member'),('viewer','viewer')],
                default='member',
                max_length=20,
                verbose_name='\u0420\u043e\u043b\u044c',
            ),
        ),
    ]
