from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse

from config.views import server_error
from .models import Avaliacao, TrabalhoRealizado


class ServerErrorPageTest(TestCase):
    def test_server_error_returns_standalone_500_page(self):
        response = server_error(RequestFactory().get('/'))

        self.assertEqual(response.status_code, 500)
        self.assertContains(
            response,
            'Estamos com uma instabilidade',
            status_code=500,
        )
        self.assertContains(response, 'Voltar para o início', status_code=500)


class HomeTrabalhosTest(TestCase):
    def test_exibe_videos_e_imagens_dos_trabalhos_publicados(self):
        TrabalhoRealizado.objects.create(
            titulo='Desentupimento de pia',
            arquivo_antes='trabalhos/antes/antes.mp4',
            arquivo_depois='trabalhos/depois/depois.jpg',
        )

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<source src="/media/trabalhos/antes/antes.mp4">',
        )
        self.assertRegex(
            response.content.decode(),
            r'<img\s+src="/media/trabalhos/depois/depois\.jpg"',
        )

    def test_home_only_displays_published_reviews(self):
        Avaliacao.objects.create(
            nome_cliente='Cliente publicado',
            nota=5,
            comentario='Atendimento excelente.',
            publicado=True,
        )
        Avaliacao.objects.create(
            nome_cliente='Cliente pendente',
            nota=4,
            comentario='Ainda em análise.',
        )

        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cliente publicado')
        self.assertContains(response, 'Atendimento excelente.')
        self.assertNotContains(response, 'Cliente pendente')
        self.assertContains(response, 'Deixe sua avaliação')


class AvaliacaoPublicaTest(TestCase):
    def test_customer_can_submit_review_without_account_and_it_stays_pending(self):
        response = self.client.get(reverse('core:nova_avaliacao'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Conte como foi sua experiência')
        self.assertContains(response, 'star-rating')
        self.assertContains(response, 'type="radio"')
        self.assertNotContains(response, '<select')
        self.assertContains(response, 'Selecione de 1 a 5 estrelas')
        self.assertNotContains(response, 'checked="checked"')

        response = self.client.post(
            reverse('core:nova_avaliacao'),
            {
                'nome_cliente': '  Maria Cliente  ',
                'nota': '5',
                'comentario': '  Serviço rápido e bem feito.  ',
            },
        )

        self.assertRedirects(
            response,
            reverse('core:agradecimento_avaliacao'),
        )
        avaliacao = Avaliacao.objects.get()
        self.assertEqual(avaliacao.nome_cliente, 'Maria Cliente')
        self.assertEqual(avaliacao.nota, 5)
        self.assertEqual(avaliacao.comentario, 'Serviço rápido e bem feito.')
        self.assertFalse(avaliacao.publicado)
        thanks_page = self.client.get(response.url)
        self.assertContains(
            thanks_page,
            'Obrigado por compartilhar sua experiência!',
        )
        self.assertContains(thanks_page, 'Recebemos sua avaliação ou reclamação')
        self.assertContains(thanks_page, 'Voltar para o início')

    def test_customer_cannot_set_review_as_published_in_submission(self):
        response = self.client.post(
            reverse('core:nova_avaliacao'),
            {
                'nome_cliente': 'Cliente',
                'nota': '5',
                'comentario': 'Minha avaliação.',
                'publicado': 'on',
            },
        )

        self.assertRedirects(
            response,
            reverse('core:agradecimento_avaliacao'),
        )
        self.assertFalse(Avaliacao.objects.get().publicado)

    def test_invalid_rating_and_overlong_review_are_rejected(self):
        response = self.client.post(
            reverse('core:nova_avaliacao'),
            {
                'nome_cliente': 'Cliente',
                'nota': '6',
                'comentario': 'x' * 2001,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Avaliacao.objects.exists())


class AvaliacaoModerationTest(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='admin_cliente',
            password='Senha-segura-123!',
        )
        self.admin.groups.add(
            Group.objects.get(name='Gerenciador de trabalhos')
        )
        self.avaliacao = Avaliacao.objects.create(
            nome_cliente='Maria',
            nota=5,
            comentario='Excelente serviço.',
        )

    def test_work_manager_can_publish_and_hide_reviews(self):
        self.client.force_login(self.admin)
        review_url = reverse(
            'core:alterar_publicacao_avaliacao',
            args=[self.avaliacao.pk],
        )

        response = self.client.get(reverse('core:gerenciar_avaliacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria')
        self.assertContains(response, 'Publicar')
        self.assertContains(
            self.client.get(reverse('core:dashboard')),
            'Analisar avaliações',
        )

        response = self.client.post(review_url, {'action': 'publish'})
        self.assertRedirects(
            response,
            reverse('core:gerenciar_avaliacoes'),
        )
        self.avaliacao.refresh_from_db()
        self.assertTrue(self.avaliacao.publicado)

        self.assertContains(
            self.client.get(reverse('core:home')),
            'Excelente serviço.',
        )

        response = self.client.post(review_url, {'action': 'hide'})
        self.assertRedirects(
            response,
            reverse('core:gerenciar_avaliacoes'),
        )
        self.avaliacao.refresh_from_db()
        self.assertFalse(self.avaliacao.publicado)
        self.assertNotContains(
            self.client.get(reverse('core:home')),
            'Excelente serviço.',
        )

    def test_regular_user_cannot_open_or_moderate_reviews(self):
        regular_user = get_user_model().objects.create_user(
            username='usuario_comum',
            password='Senha-segura-123!',
        )
        self.client.force_login(regular_user)

        response = self.client.get(reverse('core:gerenciar_avaliacoes'))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse(
                'core:alterar_publicacao_avaliacao',
                args=[self.avaliacao.pk],
            ),
            {'action': 'publish'},
        )
        self.assertEqual(response.status_code, 403)
        self.avaliacao.refresh_from_db()
        self.assertFalse(self.avaliacao.publicado)

    def test_moderation_action_requires_post(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse(
                'core:alterar_publicacao_avaliacao',
                args=[self.avaliacao.pk],
            )
        )
        self.assertEqual(response.status_code, 405)

    def test_work_manager_can_permanently_delete_review(self):
        self.client.force_login(self.admin)
        delete_url = reverse(
            'core:excluir_avaliacao',
            args=[self.avaliacao.pk],
        )

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(delete_url)

        self.assertRedirects(
            response,
            reverse('core:gerenciar_avaliacoes'),
        )
        self.assertFalse(
            Avaliacao.objects.filter(pk=self.avaliacao.pk).exists()
        )
    def test_superuser_can_permanently_delete_review(self):
        superuser = get_user_model().objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='Senha-segura-123!',
        )
        self.client.force_login(superuser)

        response = self.client.post(
            reverse(
                'core:excluir_avaliacao',
                args=[self.avaliacao.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse('core:gerenciar_avaliacoes'),
        )
        self.assertFalse(
            Avaliacao.objects.filter(pk=self.avaliacao.pk).exists()
        )

    def test_regular_user_cannot_delete_review(self):
        regular_user = get_user_model().objects.create_user(
            username='usuario_sem_permissao',
            password='Senha-segura-123!',
        )
        self.client.force_login(regular_user)

        response = self.client.post(
            reverse(
                'core:excluir_avaliacao',
                args=[self.avaliacao.pk],
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Avaliacao.objects.filter(pk=self.avaliacao.pk).exists()
        )


class DashboardPermissionsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='cliente',
            password='Senha-segura-123!',
        )
        self.client.force_login(self.user)

    def test_authenticated_user_without_group_is_denied_dashboard(self):
        for route_name in (
            'core:dashboard',
            'core:trabalhos',
            'core:novo_trabalho',
        ):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 403)

    def test_work_manager_can_manage_work_without_staff_or_superuser_access(self):
        group = Group.objects.get(name='Gerenciador de trabalhos')
        self.user.groups.add(group)

        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertEqual(
            self.client.get(reverse('core:dashboard')).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('core:trabalhos')).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('core:novo_trabalho')).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('admin:index')).status_code,
            302,
        )

        response = self.client.post(
            reverse('core:novo_trabalho'),
            {'titulo': 'Desentupimento de pia'},
        )

        self.assertRedirects(response, reverse('core:trabalhos'))
        self.assertTrue(
            TrabalhoRealizado.objects.filter(
                titulo='Desentupimento de pia'
            ).exists()
        )

    def test_superuser_can_access_dashboard_without_group(self):
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()

        self.assertEqual(
            self.client.get(reverse('core:dashboard')).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('core:novo_trabalho')).status_code,
            200,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse('core:dashboard'))

        self.assertRedirects(
            response,
            f'{reverse("core:dashboard_login")}?next={reverse("core:dashboard")}',
        )

    def test_logout_requires_post_and_ends_the_session(self):
        self.assertEqual(
            self.client.get(reverse('core:dashboard_logout')).status_code,
            405,
        )

        response = self.client.post(reverse('core:dashboard_logout'))

        self.assertRedirects(response, reverse('core:dashboard_login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_public_registration_creates_inactive_user_without_access(self):
        self.client.logout()
        response = self.client.post(
            reverse('core:cadastro_usuario'),
            {
                'username': 'novo_cliente',
                'email': 'novo@example.com',
                'password1': 'N0va-senha-segura-2026!',
                'password2': 'N0va-senha-segura-2026!',
            },
        )

        self.assertRedirects(
            response,
            reverse('core:aguardando_liberacao'),
        )
        user = get_user_model().objects.get(username='novo_cliente')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(
            Group.objects.get(name='Gerenciador de trabalhos')
            .user_set.filter(pk=user.pk).exists()
        )
        self.assertFalse(
            self.client.login(
                username='novo_cliente',
                password='N0va-senha-segura-2026!',
            )
        )

        waiting_page = self.client.get(
            reverse('core:aguardando_liberacao')
        )
        self.assertContains(waiting_page, 'Aguarde a liberação')
        self.assertContains(waiting_page, 'Voltar para o login')

    def test_pending_user_with_correct_password_is_sent_to_waiting_page(self):
        self.client.logout()
        self.user.set_password('Senha-segura-123!')
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            reverse('core:dashboard_login'),
            {
                'username': 'cliente',
                'password': 'Senha-segura-123!',
            },
        )

        self.assertRedirects(
            response,
            reverse('core:aguardando_liberacao'),
        )
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_pending_user_with_wrong_password_gets_generic_login_error(self):
        self.client.logout()
        self.user.set_password('Senha-segura-123!')
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            reverse('core:dashboard_login'),
            {
                'username': 'cliente',
                'password': 'senha-incorreta',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuário ou senha inválidos.')

    def test_active_user_without_dashboard_permission_is_sent_to_waiting_page(self):
        self.client.logout()

        response = self.client.post(
            reverse('core:dashboard_login'),
            {
                'username': 'cliente',
                'password': 'Senha-segura-123!',
            },
        )

        self.assertRedirects(
            response,
            reverse('core:aguardando_liberacao'),
        )
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_approved_user_can_log_in_to_dashboard(self):
        self.client.logout()
        self.user.groups.add(
            Group.objects.get(name='Gerenciador de trabalhos')
        )

        response = self.client.post(
            reverse('core:dashboard_login'),
            {
                'username': 'cliente',
                'password': 'Senha-segura-123!',
            },
        )

        self.assertRedirects(response, reverse('core:dashboard'))
        self.assertEqual(
            str(self.client.session['_auth_user_id']),
            str(self.user.pk),
        )

    def test_public_registration_rejects_duplicate_email(self):
        self.client.logout()
        get_user_model().objects.create_user(
            username='existing',
            email='same@example.com',
            password='Senha-segura-123!',
        )

        response = self.client.post(
            reverse('core:cadastro_usuario'),
            {
                'username': 'another',
                'email': 'SAME@example.com',
                'password1': 'N0va-senha-segura-2026!',
                'password2': 'N0va-senha-segura-2026!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(username='another').exists()
        )


class UserManagementTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.superuser = self.user_model.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='Senha-segura-123!',
        )
        self.client.force_login(self.superuser)

    def test_only_superuser_can_open_user_management(self):
        regular_user = self.user_model.objects.create_user(
            username='cliente',
            password='Senha-segura-123!',
        )
        regular_user.groups.add(
            Group.objects.get(name='Gerenciador de trabalhos')
        )
        self.client.force_login(regular_user)

        response = self.client.get(reverse('core:gerenciar_usuarios'))

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_view_users_and_dashboard_shortcut(self):
        self.user_model.objects.create_user(
            username='cliente',
            email='cliente@example.com',
            password='Senha-segura-123!',
        )

        response = self.client.get(reverse('core:gerenciar_usuarios'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cliente')
        self.assertContains(response, 'cliente@example.com')
        self.assertContains(response, 'Abrir cadastro')
        self.assertContains(response, 'Editar')

        dashboard_response = self.client.get(reverse('core:dashboard'))
        self.assertContains(dashboard_response, 'Gerenciar acessos')

    def test_superuser_can_create_pending_account_from_user_management(self):
        signup_url = reverse('core:cadastro_usuario')
        response = self.client.get(signup_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar usuário')

        response = self.client.post(
            signup_url,
            {
                'username': 'novo_cliente',
                'email': 'novo@example.com',
                'password1': 'N0va-senha-segura-2026!',
                'password2': 'N0va-senha-segura-2026!',
            },
        )

        self.assertRedirects(
            response,
            reverse('core:gerenciar_usuarios'),
        )
        user = self.user_model.objects.get(username='novo_cliente')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_can_grant_and_revoke_client_dashboard_access(self):
        regular_user = self.user_model.objects.create_user(
            username='cliente',
            password='Senha-segura-123!',
            is_active=False,
        )
        group = Group.objects.get(name='Gerenciador de trabalhos')
        access_url = reverse(
            'core:alterar_acesso_usuario',
            args=[regular_user.pk],
        )

        response = self.client.post(
            access_url,
            {'action': 'grant'},
        )

        self.assertRedirects(response, reverse('core:gerenciar_usuarios'))
        self.assertTrue(group.user_set.filter(pk=regular_user.pk).exists())
        regular_user.refresh_from_db()
        self.assertTrue(regular_user.is_active)
        self.assertFalse(regular_user.is_staff)
        self.assertFalse(regular_user.is_superuser)

        self.client.logout()
        self.assertTrue(
            self.client.login(
                username='cliente',
                password='Senha-segura-123!',
            )
        )
        self.assertEqual(
            self.client.get(reverse('core:dashboard')).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('core:gerenciar_usuarios')).status_code,
            403,
        )

        self.client.force_login(self.superuser)
        response = self.client.post(access_url, {'action': 'revoke'})
        self.assertRedirects(
            response,
            reverse('core:gerenciar_usuarios'),
        )
        self.assertFalse(group.user_set.filter(pk=regular_user.pk).exists())
        self.client.force_login(regular_user)
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse('core:dashboard_login'))
        )

    def test_superuser_can_approve_inactive_user_but_not_change_superuser(self):
        inactive_user = self.user_model.objects.create_user(
            username='inativo',
            password='Senha-segura-123!',
            is_active=False,
        )
        group = Group.objects.get(name='Gerenciador de trabalhos')
        response = self.client.post(
            reverse(
                'core:alterar_acesso_usuario',
                args=[inactive_user.pk],
            ),
            {'action': 'grant'},
        )

        self.assertRedirects(response, reverse('core:gerenciar_usuarios'))
        inactive_user.refresh_from_db()
        self.assertTrue(inactive_user.is_active)
        self.assertTrue(group.user_set.filter(pk=inactive_user.pk).exists())

        response = self.client.post(
            reverse(
                'core:alterar_acesso_usuario',
                args=[self.superuser.pk],
            ),
            {'action': 'revoke'},
        )
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_permanently_delete_regular_user(self):
        user = self.user_model.objects.create_user(
            username='cliente_para_excluir',
            password='Senha-segura-123!',
        )

        response = self.client.get(
            reverse('core:excluir_usuario', args=[user.pk])
        )
        self.assertEqual(response.status_code, 405)

        response = self.client.post(
            reverse('core:excluir_usuario', args=[user.pk])
        )

        self.assertRedirects(
            response,
            reverse('core:gerenciar_usuarios'),
        )
        self.assertFalse(
            self.user_model.objects.filter(pk=user.pk).exists()
        )

    def test_superuser_cannot_delete_self_or_another_superuser(self):
        other_superuser = self.user_model.objects.create_superuser(
            username='outro_superadmin',
            email='outro@example.com',
            password='Senha-segura-123!',
        )

        for user in (self.superuser, other_superuser):
            with self.subTest(user=user.username):
                response = self.client.post(
                    reverse('core:excluir_usuario', args=[user.pk])
                )
                self.assertEqual(response.status_code, 403)
                self.assertTrue(
                    self.user_model.objects.filter(pk=user.pk).exists()
                )

    def test_superuser_can_edit_client_profile_without_changing_permissions(self):
        regular_user = self.user_model.objects.create_user(
            username='cliente',
            email='cliente@example.com',
            password='Senha-segura-123!',
        )
        edit_url = reverse(
            'core:editar_usuario',
            args=[regular_user.pk],
        )

        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Salvar alterações')

        response = self.client.post(
            edit_url,
            {
                'username': 'cliente-atualizado',
                'first_name': 'Cliente',
                'last_name': 'Exemplo',
                'email': 'novo-cliente@example.com',
            },
        )

        self.assertRedirects(response, reverse('core:gerenciar_usuarios'))
        regular_user.refresh_from_db()
        self.assertEqual(regular_user.username, 'cliente-atualizado')
        self.assertEqual(regular_user.email, 'novo-cliente@example.com')
        self.assertFalse(regular_user.is_staff)
        self.assertFalse(regular_user.is_superuser)
        self.assertFalse(
            Group.objects.get(name='Gerenciador de trabalhos')
            .user_set.filter(pk=regular_user.pk).exists()
        )

    def test_regular_user_cannot_edit_user_profile(self):
        regular_user = self.user_model.objects.create_user(
            username='cliente',
            password='Senha-segura-123!',
        )
        self.client.force_login(regular_user)

        response = self.client.get(
            reverse('core:editar_usuario', args=[regular_user.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_delete_user(self):
        regular_user = self.user_model.objects.create_user(
            username='cliente',
            password='Senha-segura-123!',
        )
        target_user = self.user_model.objects.create_user(
            username='outro_cliente',
            password='Senha-segura-123!',
        )
        self.client.force_login(regular_user)

        response = self.client.post(
            reverse('core:excluir_usuario', args=[target_user.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            self.user_model.objects.filter(pk=target_user.pk).exists()
        )

    def test_user_management_post_requires_superuser(self):
        regular_user = self.user_model.objects.create_user(
            username='cliente',
            password='Senha-segura-123!',
        )
        self.client.force_login(regular_user)

        response = self.client.post(
            reverse(
                'core:alterar_acesso_usuario',
                args=[regular_user.pk],
            ),
            {'action': 'grant'},
        )

        self.assertEqual(response.status_code, 403)
