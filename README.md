# Elastic Framework: to make easy develop your application

Elastic Franmework is a framework 

## Usage
1) pip install https://https://github.com/elastic-coders/elastic_framework/archive/1.0.0

2) Add elastic_framework to your settings INSTALLED_APPS

3) Use elastic_framework utility in your app (see later....)

## Clone the repo
If you want to clone the repo and test it:
1) git clone https://github.com/elastic-coders/elastic_framework.git
2) pip install -r requirements
3) test with python manage.py test

## Use user signup/signin/signout flow

- add elastic_framework url to your application urls:

###
urlpatterns = [
    url(r'^users', include('elastic_framework.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
###

- define your user model as custom Django User Model
An example of User model:

class User(AbstractBaseUser):

    USER_LEVEL_BASE = ''
    USER_LEVEL_ADMIN = 'A'
    USER_LEVEL_STAFF = 'S'

    USER_LEVEL_CHOICES = [
        (USER_LEVEL_BASE, 'base user'),
        (USER_LEVEL_ADMIN, 'admin user'),
        (USER_LEVEL_STAFF, 'staff user'),
    ]

    accessLevel = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=USER_LEVEL_CHOICES,
        default=USER_LEVEL_BASE
    )

    email = models.EmailField(
        max_length=254, blank=False, db_index=True, unique=True
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    surname = models.CharField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    zip_code = models.CharField(max_length=9, blank=True, null=True)


    @property
    def is_admin(self):
        return self.accessLevel == User.USER_LEVEL_ADMIN

    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return (self.accessLevel == User.USER_LEVEL_STAFF or
                self.accessLevel == User.USER_LEVEL_ADMIN)

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def get_full_name(self):
        return '%s %s' % (self.givenName, self.familyName)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    # username field: default is "username". Elastic Framework use this
    # parameter  to know wich input param use to define username
    USERNAME_FIELD = 'email'

    # password field: default is "password". Elastic Framework use this
    # parameter  to know wich input param use to define password
    PASSWORD_FIELD = 'password'

    # user status field: default is "status". Elastic Framework use this
    # parameter  to know wich input param use to define user status
    STATUS_FIELD = 'status'

    FACEBOOK_USER_ID_FIELD = 'facebookUserId'

    objects = UserManager()
