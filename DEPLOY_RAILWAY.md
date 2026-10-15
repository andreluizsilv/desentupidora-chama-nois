# Deploy no Railway

O projeto já aceita PostgreSQL pela variável `DATABASE_URL`, coleta os arquivos
estáticos com WhiteNoise e usa um volume persistente para fotos e vídeos
enviados no dashboard.

## Importante sobre o plano gratuito

Segundo a página oficial de preços consultada em 14/10/2026, o plano Free custa
US$ 0/mês e inclui US$ 1/mês em créditos de uso. A conta nova pode receber
US$ 5 de crédito uma única vez, válido por 30 dias. O plano Free permite até
500 MB de armazenamento em volume, um serviço por réplica e não permite domínio
personalizado. O consumo do app, banco, tráfego e volume é medido; portanto não
há garantia de que o site com app e PostgreSQL ligados continuamente caiba nos
créditos gratuitos. Confira **Usage** e **Billing** no painel com frequência.

## Criar o projeto

1. Confirme no painel que sua conta está no plano **Free**. Crie um projeto em
   **New Project** e escolha **Deploy from GitHub repo**. Se o repositório ainda
   não aparecer, conecte a conta GitHub e envie primeiro as alterações deste
   projeto para uma branch do repositório.
2. No serviço criado a partir do repositório, configure:
   - **Build Command:** `python manage.py collectstatic --noinput`
   - **Start Command:** `bash scripts/railway_start.sh`
3. No canvas do projeto, crie um banco em **Create → Database → PostgreSQL**.
   A criação do serviço de PostgreSQL não depende do Blueprint do Render.
4. No serviço web, adicione as variáveis abaixo. Para `DATABASE_URL`, selecione
   a referência `${{Postgres.DATABASE_URL}}`; se o nome que aparece no canvas
   for diferente de `Postgres`, ajuste o nome da referência:

   | Variável | Valor |
   | --- | --- |
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
   | `DJANGO_SECRET_KEY` | Uma chave longa, aleatória e privada |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `localhost` temporariamente |

   Use a opção **Generate** do Railway para criar a chave secreta. O host
   `localhost` permite que o primeiro build rode antes de existir um domínio
   público; depois de gerar o domínio, substitua esse valor pelo hostname
   exibido, sem `https://`. O Django também reconhece automaticamente a
   variável `RAILWAY_PUBLIC_DOMAIN`.
5. Gere um domínio em **Settings → Networking → Generate Domain**. O domínio
   fornecido pelo Railway funciona no Free; domínio personalizado não está
   incluído nesse plano. Se o domínio for criado antes do primeiro deploy,
   configure `DJANGO_ALLOWED_HOSTS` com o hostname já nessa etapa.
6. Para preservar as mídias após reinicializações, adicione um volume ao serviço
   web no caminho `/data`. O Railway define automaticamente
   `RAILWAY_VOLUME_MOUNT_PATH`; o projeto grava os uploads em
   `/data/media`. No Free, o limite de volume é 500 MB.
7. Faça deploy e acompanhe os logs. O script aplica as migrations e inicia o
   servidor. Abra **Shell** no serviço web e crie o primeiro SuperAdmin:

   ```sh
   python manage.py createsuperuser
   ```

8. Teste a home, `/admin/`, login do dashboard, uma avaliação e o envio de uma
   mídia. Verifique que a mídia continua disponível depois de um novo deploy.

## Banco local e segurança

O PostgreSQL novo fica vazio: as migrations criam as tabelas, mas não importam
automaticamente usuários, avaliações ou trabalhos do SQLite local. As mídias
que estão versionadas no repositório são copiadas para o volume na primeira
inicialização. Crie um novo SuperAdmin no Railway. Não envie credenciais nem a
chave secreta ao GitHub; a antiga chave fixa no código não deve ser reutilizada.

Para produção de um negócio, confirme os custos e a disponibilidade antes de
usar o plano gratuito. Se o crédito mensal não cobrir app + banco, será preciso
aceitar o custo do plano Hobby ou escolher outra hospedagem que se encaixe no
orçamento. O volume gratuito também não substitui um backup externo.
