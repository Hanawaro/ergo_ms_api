from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='slug',
            field=models.SlugField(blank=True, unique=True, verbose_name='Слаг'),
        ),
        migrations.AddField(
            model_name='organization',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AddField(
            model_name='organization',
            name='logo_url',
            field=models.URLField(blank=True, verbose_name='Логотип'),
        ),
        migrations.AddField(
            model_name='organization',
            name='industry',
            field=models.CharField(blank=True, max_length=255, verbose_name='Отрасль'),
        ),
        migrations.AddField(
            model_name='organization',
            name='website',
            field=models.URLField(blank=True, verbose_name='Сайт'),
        ),
        migrations.AddField(
            model_name='organization',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='organization',
            name='phone',
            field=models.CharField(blank=True, max_length=50, verbose_name='Телефон'),
        ),
        migrations.AddField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, max_length=100, verbose_name='Страна'),
        ),
        migrations.AddField(
            model_name='organization',
            name='timezone',
            field=models.CharField(blank=True, max_length=50, verbose_name='Часовой пояс'),
        ),
        migrations.AddField(
            model_name='organization',
            name='address',
            field=models.CharField(blank=True, max_length=255, verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='organization',
            name='billing_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Плательщик'),
        ),
        migrations.AddField(
            model_name='organization',
            name='billing_vat',
            field=models.CharField(blank=True, max_length=50, verbose_name='НДС'),
        ),
        migrations.AddField(
            model_name='organization',
            name='billing_address',
            field=models.CharField(blank=True, max_length=255, verbose_name='Адрес для счетов'),
        ),
        migrations.AddField(
            model_name='organization',
            name='visibility',
            field=models.CharField(choices=[('private', 'private'), ('by_invite', 'by_invite')], default='by_invite', max_length=20, verbose_name='Видимость'),
        ),
        migrations.AddField(
            model_name='organization',
            name='default_role',
            field=models.CharField(choices=[('member', 'member'), ('viewer', 'viewer')], default='member', max_length=20, verbose_name='Роль по умолчанию'),
        ),
        migrations.AddField(
            model_name='organization',
            name='status',
            field=models.CharField(choices=[('active', 'active'), ('archived', 'archived')], default='active', max_length=20, verbose_name='Статус'),
        ),
        migrations.RemoveField(
            model_name='organizationmember',
            name='is_accepted',
        ),
        migrations.RemoveField(
            model_name='organizationmember',
            name='joined_at',
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='role',
            field=models.CharField(choices=[('owner','owner'),('admin','admin'),('member','member'),('viewer','viewer')], default='member', max_length=20, verbose_name='Роль'),
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='status',
            field=models.CharField(choices=[('pending','pending'),('accepted','accepted'),('declined','declined'),('revoked','revoked')], default='pending', max_length=20, verbose_name='Статус'),
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='invited_by',
            field=models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, related_name='sent_org_invites', to=settings.AUTH_USER_MODEL, verbose_name='Кем приглашен'),
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='responded_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата ответа'),
        ),
        migrations.CreateModel(
            name='OrganizationInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('token', models.CharField(max_length=64, unique=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Истекает')),
                ('status', models.CharField(choices=[('pending','pending'),('accepted','accepted'),('declined','declined'),('expired','expired')], default='pending', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('responded_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата ответа')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='crm.organization')),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_invites', to=settings.AUTH_USER_MODEL, verbose_name='Пригласивший')),
            ],
            options={
                'verbose_name': 'Приглашение в организацию',
                'verbose_name_plural': 'Приглашения в организации',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='crm.organization', verbose_name='Организация'),
        ),
    ]
