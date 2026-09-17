# forwardtogroup

Saved Messages'dagi oxirgi xabarni `targets.txt` dagi aniq ro'yxatga bir marta
forward qiladigan skript. Cheksiz sikl yo'q, guruhlarni avtomatik topish yo'q.

## Lokal ishga tushirish

```bash
cp .env.example .env            # TELEGRAM_API_ID / TELEGRAM_API_HASH
cp targets.example.txt targets.txt
pip install -r requirements.txt
python broadcast.py --dry-run   # avval quruq yurgizib ko'ring
python broadcast.py
```

Birinchi ishga tushirishda Telethon telefon raqami va kodni interaktiv so'raydi
va `session.session` faylini yaratadi.

## Serverga deploy (GitHub Actions + SSH)

### 1. Deploy kaliti

Lokal mashinangizda:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/forwardtogroup_deploy -N ''
ssh-copy-id -i ~/.ssh/forwardtogroup_deploy.pub USER@SERVER
ssh-keyscan -p 22 SERVER            # ixtiyoriy: SSH_KNOWN_HOSTS uchun
```

`SSH_KNOWN_HOSTS` ni qo'shmasangiz, workflow har deployda serverning host
kalitini `ssh-keyscan` bilan o'zi oladi. Ishlaydi, lekin birinchi ulanishda
MITM'dan himoya qilmaydi — bu kalitni oldindan bilishning butun ma'nosi edi.
Imkoni bo'lsa secretni qo'shib qo'ying.

Yopiq kalitni (`~/.ssh/forwardtogroup_deploy`) hech qachon repoga qo'ymang.

### 2. GitHub secretlari

Settings → Secrets and variables → Actions → New repository secret:

| Secret | Nima |
| --- | --- |
| `SSH_HOST` | server IP yoki domeni |
| `SSH_USER` | SSH foydalanuvchisi |
| `SSH_PORT` | port (ixtiyoriy, default `22`) |
| `SSH_PRIVATE_KEY` | `~/.ssh/forwardtogroup_deploy` faylining to'liq mazmuni |
| `SSH_KNOWN_HOSTS` | ixtiyoriy. `ssh-keyscan` chiqishi. Bo'lmasa workflow host kalitini deploy paytida o'zi oladi |
| `DEPLOY_PATH` | ixtiyoriy. Ko'rsatilmasa `~/apps/forwardtogroup` ishlatiladi |
| `TELEGRAM_API_ID` | my.telegram.org dan |
| `TELEGRAM_API_HASH` | my.telegram.org dan |

`gh` CLI orqali ham bo'ladi:

```bash
gh secret set SSH_PRIVATE_KEY < ~/.ssh/forwardtogroup_deploy
gh secret set SSH_KNOWN_HOSTS < known_hosts.txt
gh secret set SSH_HOST         # qiymat so'raydi
```

### 3. Deploy

`main` ga push qilinganda yoki Actions → Deploy → Run workflow orqali qo'lda
ishga tushadi. Workflow: fayllarni `rsync` qiladi, secretlardan serverda `.env`
yozadi (`umask 077`), `.venv` ichiga bog'liqliklarni o'rnatadi.

Default papka — SSH foydalanuvchisining uy katalogidagi `apps/forwardtogroup`.
U faqat shu loyihaga tegishli, boshqa papkalarga tegmaydi. Boshqa joy kerak
bo'lsa `DEPLOY_PATH` secretini qo'shing (uy katalogiga nisbatan yo'l yoki
absolyut yo'l).

`rsync --delete` ishlatiladi — shuning uchun papka faqat shu loyiha uchun
bo'lishi muhim. `.env`, `targets.txt`, `.venv` va `*.session` istisno
qilingan, serverdagi nusxalari o'chmaydi.

### 4. Serverda birinchi marta

Workflow skriptni **ishga tushirmaydi** — Telegram sessiyasi interaktiv login
talab qiladi va yuborishni qo'lda boshlagan ma'qul:

```bash
ssh USER@SERVER
cd ~/apps/forwardtogroup
nano targets.txt                 # manzillar ro'yxati (bir marta)
.venv/bin/python broadcast.py    # birinchi safar login so'raydi
```

Keyingi safarlar uchun `session.session` fayli saqlanib qoladi.
