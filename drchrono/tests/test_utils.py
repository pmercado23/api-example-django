import unittest
from drchrono import utils
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth



class Test(unittest.TestCase):
    # Testing Sanity, if this fails, all hope is lost.
    def test_sanity(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
        self.assertEqual(True, True, "Should be True")

    def test_ssn_format(self):
        correct_ssn = "123-44-1233"
        result = utils.check_ssn_format(correct_ssn)
        self.assertEqual(result, True, "Should be True, correct ssn was entered")
        bad_ssn = "12-44-1233"
        result_bad_ssn = utils.check_ssn_format(bad_ssn)
        self.assertEqual(result_bad_ssn, False, "Should be False, bad format was entered")

    def test_get_token(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='user1', email='user@example.com')
        self.access_token = "secret"
        self.usa = UserSocialAuth.objects.create(
            user=self.user, provider='drchrono',
            uid='1234',
            extra_data={
                "access_token": self.access_token,
                "expires_in": 172800,
                "refresh_token": "wWdSgnBSwLZs1XEwxxG0CE8JRFNAjm",
                "auth_time": 1575496917})


        token = utils.get_token()
        self.assertEqual(token, "secret")

        # make sure oauth_provider.extra_data['access_token'] is what it returns
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        self.assertEqual(token, oauth_provider.extra_data['access_token'])

