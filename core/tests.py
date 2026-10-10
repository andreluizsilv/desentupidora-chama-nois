from django.test import TestCase

from .models import TrabalhoRealizado


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
