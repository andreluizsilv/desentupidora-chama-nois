from django.db import migrations


GROUP_NAME = 'Gerenciador de trabalhos'
PERMISSION_CODENAMES = ('view_avaliacao', 'change_avaliacao')


def add_review_permissions(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    content_type, _ = ContentType.objects.using(alias).get_or_create(
        app_label='core',
        model='avaliacao',
    )
    permissions = []
    for codename, name in (
        ('view_avaliacao', 'Can view avaliação'),
        ('change_avaliacao', 'Can change avaliação'),
    ):
        permission, _ = Permission.objects.using(alias).get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={'name': name},
        )
        permissions.append(permission)

    group, _ = Group.objects.using(alias).get_or_create(name=GROUP_NAME)
    group.permissions.add(*permissions)


def remove_review_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    alias = schema_editor.connection.alias
    group = Group.objects.using(alias).filter(name=GROUP_NAME).first()
    if group is not None:
        group.permissions.remove(
            *Permission.objects.using(alias).filter(
                content_type__app_label='core',
                content_type__model='avaliacao',
                codename__in=PERMISSION_CODENAMES,
            )
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_grupo_gerenciador_trabalhos'),
    ]

    operations = [
        migrations.RunPython(
            add_review_permissions,
            remove_review_permissions,
        ),
    ]
