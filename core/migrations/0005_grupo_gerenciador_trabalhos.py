from django.db import migrations


GROUP_NAME = 'Gerenciador de trabalhos'


def create_work_manager_group(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    content_type, _ = ContentType.objects.using(alias).get_or_create(
        app_label='core',
        model='trabalhorealizado',
    )

    permissions = []
    for action in ('view', 'add'):
        codename = f'{action}_trabalhorealizado'
        permission, _ = Permission.objects.using(alias).get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={
                'name': f'Can {action} trabalho realizado',
            },
        )
        permissions.append(permission)

    group, _ = Group.objects.using(alias).get_or_create(name=GROUP_NAME)
    group.permissions.add(*permissions)


def remove_work_manager_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.using(schema_editor.connection.alias).filter(
        name=GROUP_NAME
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0004_alter_trabalhorealizado_arquivo_antes_and_more'),
    ]

    operations = [
        migrations.RunPython(
            create_work_manager_group,
            remove_work_manager_group,
        ),
    ]
