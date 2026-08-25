from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Order


class TrackOrderPermissionTests(TestCase):
    """Regression tests for the IDOR in track_order.

    Before the fix, track_order looked orders up by primary key alone, with no
    login requirement and no ownership check, so any visitor could enumerate
    sequential order IDs and read other users' order data.

    These assert on the view's context rather than the rendered HTML, because
    track.html only displays a subset of the order's fields.
    """

    def setUp(self):
        self.owner = User.objects.create_user("owner@example.com", password="pw-Str0ng-1")
        self.other = User.objects.create_user("other@example.com", password="pw-Str0ng-2")
        self.order = Order.objects.create(
            user=self.owner,
            product_link="https://example.com/gift",
            delivery_date="2027-01-01",
            delivery_time="10:00",
            address="12 Private Road, Gurugram",
        )

    def test_anonymous_visitor_is_redirected_to_login(self):
        response = self.client.post(reverse("track"), {"order_id": self.order.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_other_user_cannot_load_the_order(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse("track"), {"order_id": self.order.id})
        self.assertIsNone(response.context["order"])
        self.assertEqual(response.context["error"], "Order not found. Please check your Order ID.")

    def test_owner_can_load_their_own_order(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("track"), {"order_id": self.order.id})
        self.assertEqual(response.context["order"], self.order)

    def test_non_numeric_order_id_does_not_raise(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("track"), {"order_id": "abc"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["order"])


class SignupValidationTests(TestCase):
    def test_weak_password_is_rejected(self):
        self.client.post(
            reverse("signup"),
            {"email": "new@example.com", "password1": "1", "password2": "1"},
        )
        self.assertFalse(User.objects.filter(username="new@example.com").exists())

    def test_invalid_email_is_rejected(self):
        self.client.post(
            reverse("signup"),
            {"email": "notanemail", "password1": "pw-Str0ng-9", "password2": "pw-Str0ng-9"},
        )
        self.assertFalse(User.objects.filter(username="notanemail").exists())

    def test_valid_signup_creates_the_account(self):
        self.client.post(
            reverse("signup"),
            {"email": "good@example.com", "password1": "pw-Str0ng-9", "password2": "pw-Str0ng-9"},
        )
        self.assertTrue(User.objects.filter(username="good@example.com").exists())


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class RoutingTests(TestCase):
    """The '' path was registered twice - once for home, once for landing.

    Django matched home first, so landing was unreachable, and it rendered
    landing.html, which does not exist in the repo. logout_view redirected to
    the landing name, which reversed to '/' and served home by accident.
    """

    def test_home_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_posting_to_home_does_not_crash(self):
        # The old POST branch raised IntegrityError, then NameError.
        response = self.client.post(reverse("home"), {"product_link": "x"})
        self.assertEqual(response.status_code, 200)

    def test_landing_route_is_gone(self):
        from django.urls import NoReverseMatch

        with self.assertRaises(NoReverseMatch):
            reverse("landing")

    def test_logout_redirects_home(self):
        User.objects.create_user("bye@example.com", password="pw-Str0ng-3")
        self.client.login(username="bye@example.com", password="pw-Str0ng-3")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("home"))


class TrackTemplateTests(TestCase):
    """track.html had no form to submit an order ID, never rendered {{ error }},
    and drew the progress timeline even when no order had been found.
    """

    def setUp(self):
        self.user = User.objects.create_user("t@example.com", password="pw-Str0ng-4")
        self.client.force_login(self.user)

    def test_page_offers_a_lookup_form(self):
        response = self.client.get(reverse("track"))
        self.assertContains(response, 'name="order_id"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_error_message_is_displayed(self):
        response = self.client.post(reverse("track"), {"order_id": "9999"})
        self.assertContains(response, "Order not found")

    def test_timeline_hidden_when_no_order(self):
        response = self.client.post(reverse("track"), {"order_id": "9999"})
        self.assertNotContains(response, "Order Received")

    def test_timeline_shown_for_a_real_order(self):
        order = Order.objects.create(
            user=self.user,
            product_link="https://example.com/gift",
            delivery_date="2027-03-04",
            delivery_time="09:30",
            address="5 Example Street",
        )
        response = self.client.post(reverse("track"), {"order_id": order.id})
        self.assertContains(response, "Order Received")
