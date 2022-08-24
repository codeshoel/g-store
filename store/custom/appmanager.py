from django.contrib.auth.models import BaseUserManager


class AppUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, mobile, address, password, *args, **kwargs):
        """
            Creates and saves a User with provided email and password
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email),
            mobile=mobile,
            address=address,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, first_name, last_name, email, mobile, address, password, *args, **kwargs):
        """
            Creates and save superuser with provided email and password
        """
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email, 
            mobile=mobile,
            address=address,
            password=password,
            )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user






