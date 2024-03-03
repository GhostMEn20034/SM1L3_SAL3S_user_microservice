from services.verification.verificaton_service import VerificationService

def get_verification_service(user_queryset):
    return VerificationService(user_queryset)
