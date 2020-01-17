import os
from snoop import snoop

@snoop()
def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.fake_django_settings'
    import django

    django.setup()
    from django.contrib.contenttypes.models import ContentType
    queryset = ContentType.objects.all()
    lst = [1, 2, 3]
