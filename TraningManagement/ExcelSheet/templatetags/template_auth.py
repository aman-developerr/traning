from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter(name='has_group')
def has_group(group, user_id):
    group_user = User.objects.filter(groups__name=group)

    for gr in group_user:
        if gr.pk == user_id:
            return True
    return False



