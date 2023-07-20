from django.contrib.auth import get_user_model

Account = get_user_model()

def change_email(user_id, new_email):
    user = Account.objects.get(id=user_id)
    user.email = new_email
    user.save(update_fields=['email'])
    return True
