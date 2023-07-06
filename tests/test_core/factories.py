import factory.django


class LoginRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')


class SignUpRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    password_repeat = factory.LazyAttribute(lambda o: o.password)
    # password = 'ffyyRwS!21QWE2!'
    # password_repeat = 'ffyyRwS!21QWE2!'
