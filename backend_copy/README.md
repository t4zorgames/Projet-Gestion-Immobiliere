Copie du projet `backend` pour modifications sûres.

Instructions rapides:

1. Créez et activez un virtualenv.
2. Installez les dépendances:

```bash
pip install -r requirements.txt
```

3. Créez un `.env` basé sur `.env.example` et remplacez `DJANGO_SECRET_KEY`.
4. Lancez le serveur:

```bash
set DJANGO_SECRET_KEY=yourkey
set DEBUG=True
python manage.py migrate
python manage.py runserver
```

5. (Optionnel) Configuration SMTP

 - Le projet utilise par défaut le backend console pour le développement (`EMAIL_BACKEND`).
 - Pour envoyer de vrais e‑mails, définissez les variables d'environnement suivantes dans votre `.env`:

```bash
set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
set EMAIL_HOST=smtp.example.com
set EMAIL_PORT=587
set EMAIL_HOST_USER=your_smtp_user
set EMAIL_HOST_PASSWORD=your_smtp_password
set EMAIL_USE_TLS=True
set DEFAULT_FROM_EMAIL=you@example.com
```

Redémarrez le serveur après avoir défini ces variables.
