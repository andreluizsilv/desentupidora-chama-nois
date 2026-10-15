# Deploy no Render

O projeto está preparado para usar PostgreSQL, arquivos estáticos servidos pelo
WhiteNoise e mídias enviadas pelo dashboard em um disco persistente do Render.
O disco mantém os uploads entre reinicializações e deploys; por isso, o serviço
web deve permanecer com uma instância e um plano que aceite disco persistente.
As mídias públicas são entregues pelo próprio Django; isso atende ao volume
inicial do site, mas para tráfego alto ou múltiplas instâncias será melhor
migrá-las para um armazenamento de objetos/CDN.

## Criar os serviços

1. Envie este repositório para o GitHub e, no Render, crie um **Blueprint** a
   partir do repositório. O Render lerá o `render.yaml` para criar o serviço web,
   o PostgreSQL e o disco de mídia na mesma região.
2. Revise os custos e planos antes de confirmar. O Blueprint usa o plano Starter
   para o serviço web e o plano Basic para o PostgreSQL; discos persistentes
   exigem um serviço pago.
3. Aguarde o primeiro deploy. O comando de inicialização aplica as migrations e
   copia os arquivos de mídia versionados para o disco somente quando ainda não
   existem nele.
4. No serviço web, abra **Shell** e crie o primeiro SuperAdmin:

   ```sh
   python manage.py createsuperuser
   ```

5. Acesse `/admin/` para validar o usuário e depois use o dashboard do site.

O Render gera `DJANGO_SECRET_KEY` e conecta `DATABASE_URL` ao PostgreSQL. Não
publique segredos no repositório. A chave que estava anteriormente no código
deve ser considerada comprometida e não deve ser reutilizada.

## Domínio próprio

Quando o domínio estiver disponível, adicione-o ao serviço no Render e configure
os registros DNS indicados pelo painel. Inclua o domínio em
`DJANGO_ALLOWED_HOSTS` (somente nomes de host, separados por vírgula) e em
`DJANGO_CSRF_TRUSTED_ORIGINS` (origens completas com `https://`). O host
`.onrender.com` continua sendo aceito.

## Dados locais

O PostgreSQL criado pelo Blueprint começa vazio: as migrations criam as tabelas,
mas não copiam automaticamente usuários, avaliações ou trabalhos do SQLite
local. Os arquivos de mídia já versionados no repositório são inicializados no
disco; se houver conteúdo de banco que precise ser preservado, planeje uma
exportação/importação separada antes de abrir o site ao público. Crie um novo
SuperAdmin no Render em vez de copiar a conta de desenvolvimento.

## Verificações após o deploy

- Confirme que o deploy terminou sem erro e que `/` e `/admin/` respondem em
  HTTPS.
- Teste login do SuperAdmin, cadastro e aprovação de um usuário, moderação de
  avaliação e envio de um arquivo de mídia.
- Faça outro deploy e confirme que a mídia continua acessível.
- Configure backups do PostgreSQL e monitore o uso do disco persistente.
