from AquaFlo.Utils.default_response_mixin import DefaultResponseMixin
from AquaFlo.Utils.permissions import IsAdminOrReadOnly
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings



# Create your views here.
class RegisterAPI(DefaultResponseMixin, generics.GenericAPIView):
    """
    User Register
    """

    serializer_class = RegisterSerializer
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request):
        serializer = RegisterSerializer(
            data=self.request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            """
            Send a welcome email to the newly registered user.
            """
            subject = "Registration Successful"
            message = f"Hello,\n\nYou have been successfully registered on our platform.\n\nThanks,\nThe Team"
            from_email = (
                settings.EMAIL_HOST_USER
            )  # You can use your default email or configure one in settings

            # Sending the email
            send_mail(subject, message, from_email, [self.request.data.get("email")])
            return self.success_response("Registered successfully", serializer.data)


class LoginAPI(DefaultResponseMixin, generics.GenericAPIView):
    """
    User Register
    """

    serializer_class = LoginSerializer

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if UserModel.objects.filter(
            phone_number=phone_number, is_deleted=True
        ).exists():
            return self.error_response(
                "This user account has been deleted and is no longer active."
            )
        user = authenticate(request, phone_number=phone_number, password=password)
        if user:

            response_data = {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "tokens": user.tokens,
                "addresses": user.addresses,
            }
            return self.success_response("Login successfully", response_data)
        else:
            return self.error_response("The phone number and password do not match. Please try again.")


class AddorRemoveAddressAPI(DefaultResponseMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        addresses = request.data.get("addresses")

        get_address = UserModel.objects.filter(id=user_id).first()

        if not get_address:
            return self.error_response("Address Not Found")

        get_address.addresses = addresses

        get_address.save()
        return self.success_response(
            "Address Update or Delete Successfully", get_address.addresses
        )
