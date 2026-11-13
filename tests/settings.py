USE_I18N = False
SECRET_KEY = "test_secret_key"

INSTALLED_APPS = [
    "django_byo_react.apps.DjangoByoReactConfig",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    },
]
