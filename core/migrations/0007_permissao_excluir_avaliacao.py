from django.db import migrations


GROUP_NAME = 'Gerenciador de trabalhos'


def add_delete_review_permission(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    content_type, _ = ContentType.objects.using(alias).get_or_create(
        app_label='core',
        model='avaliacao',
    )
    permission, _ = Permission.objects.using(alias).get_or_create(
        content_type=content_type,
        codename='delete_avaliacao',
        defaults={'name': 'Can delete avaliação'},
    )
    group, _ = Group.objects.using(alias).get_or_create(name=GROUP_NAME)
    group.permissions.add(permission)


def remove_delete_review_permission(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    alias = schema_editor.connection.alias
    group = Group.objects.using(alias).filter(name=GROUP_NAME).first()
    if group is None:
        return

    permission = Permission.objects.using(alias).filter(
        content_type__app_label='core',
        content_type__model='avaliacao',
        codename='delete_avaliacao',
    )
    group.permissions.remove(*permission)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_permissoes_moderacao_avaliacoes'),
    ]

    operations = [
        migrations.RunPython(
            add_delete_review_permission,
            remove_delete_review_permission,
        ),
    ]
