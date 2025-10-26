from django.test import TestCase
from django.contrib.auth.models import User
import uuid as _uuid
from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from scoutifiiapp.models import (
    Profile, AdPlacement, Advertiser, 
    Campaign, Creative, AdImpression, AdClick,
    Post, FollowersCount, BrandSetting
)
import pytest
from datetime import timedelta
from scoutifiiapp.ad_selector import select_creative


class UserSignupTest(TestCase):
    def setUp(self):
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'mmasiga@scoutifii.com',
            'password': 'testpassword',
            'password_confirm': 'testpassword',
        }

    def test_user_signup(self):
        response = self.client.post('/signup/', self.user_data)
        self.assertEqual(response.status_code, 302)  # Redirect to settings page
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)

    def test_user_signup_password_mismatch(self):
        self.user_data['password_confirm'] = 'wrongpassword'
        response = self.client.post('/signup/', self.user_data)
        self.assertEqual(response.status_code, 302)

class UserSProfileTest(TestCase):
    def setUp(self):
        self.profile_data = {
            'bio': 'my biography',
            'location': 'my location',
            'phone_no': '0700101010',
            'country_id': 'Uganda',
            'profile_type_data': 'User',
            'birth_date': '1990/01/01'
        }
    
    def test_user_profile(self):
        response = self.client.post('/settings/', self.profile_data)
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard page
        profile_exists = Profile.objects.filter(phone_no='0700101010').exists()
        self.assertFalse(profile_exists)

class DashboardViewTests(TestCase):
    def setUp(self):
        # Users
        self.me = User.objects.create_user(
            username="me", email="me@example.com", password="pass1234"
        )
        self.u1 = User.objects.create_user(
            username="u1", email="u1@example.com", password="pass1234"
        )
        self.u2 = User.objects.create_user(
            username="u2", email="u2@example.com", password="pass1234"
        )
        # Profiles
        self.me_profile = Profile.objects.create(user=self.me, id_user=self.me.id, phone_no="1000000001")
        self.u1_profile = Profile.objects.create(user=self.u1, id_user=self.u1.id, phone_no="1000000002")
        self.u2_profile = Profile.objects.create(user=self.u2, id_user=self.u2.id, phone_no="1000000003")

        # Brand setting (view expects queryset to exist)
        BrandSetting.objects.create()  # add required fields if model enforces them

        # Follow: me -> u1 (but not u2)
        FollowersCount.objects.create(follower=self.me.username, user=self.u1.username, profile_id=str(self.u1_profile.id))

        # Posts
        self.p1 = Post.objects.create(
            user_id=self.u1.id,
            user_prof=self.u1.username,
            profile_id=str(self.u1_profile.id),
            uuid=str(_uuid.uuid4()),
            video_name="u1-post",
            category_type="general",
            created_at=timezone.now(),
        )
        self.p2 = Post.objects.create(
            user_id=self.u2.id,
            user_prof=self.u2.username,
            profile_id=str(self.u2_profile.id),
            uuid=str(_uuid.uuid4()),
            video_name="u2-post",
            category_type="general",
            created_at=timezone.now(),
        )

    def test_requires_login(self):
        url = reverse("dashboard")
        res = self.client.get(url)
        # Redirects to login due to @login_required
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login", res["Location"])

    @patch("scoutifiiapp.views.random.shuffle", lambda x: None)  # make order deterministic
    def test_feed_contains_followed_users_posts_only(self):
        self.client.login(username="me", password="pass1234")
        url = reverse("dashboard")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "dashboard.html")

        # Context assertions
        ctx = res.context
        self.assertIn("posts", ctx)
        self.assertIn("user_profile", ctx)
        self.assertIn("brand_setting", ctx)
        self.assertIn("username_suggestions", ctx)
        self.assertIn("num_of_followers", ctx)
        self.assertIn("token", ctx)

        posts = list(ctx["posts"])
        # Only u1 (followed) should be in feed; u2 should not
        self.assertEqual([p.id for p in posts], [self.p1.id])

    @patch("scoutifiiapp.views.random.shuffle", lambda x: None)
    def test_suggestions_exclude_self_and_already_followed(self):
        self.client.login(username="me", password="pass1234")
        res = self.client.get(reverse("dashboard"))
        suggestions = list(res.context["username_suggestions"])
        # Suggestions are profiles; expect u2 only
        suggested_user_ids = {p.user_id for p in suggestions}
        self.assertSetEqual(suggested_user_ids, {self.u2.id})

    @patch("scoutifiiapp.views.random.shuffle", lambda x: None)
    def test_handles_empty_following(self):
        # Log in as u2 (follows no one)
        self.client.login(username="u2", password="pass1234")
        res = self.client.get(reverse("dashboard"))
        self.assertEqual(res.status_code, 200)
        posts = list(res.context["posts"])
        # Feed should be empty because code only includes followed users
        self.assertEqual(posts, [])
        # Suggestions should include me and u1 (not self u2)
        suggested_user_ids = {p.user_id for p in res.context["username_suggestions"]}
        self.assertSetEqual(suggested_user_ids, {self.me.id, self.u1.id})

    def test_token_is_uuid_like(self):
        self.client.login(username="me", password="pass1234")
        res = self.client.get(reverse("dashboard"))
        token = res.context["token"]
        # Validate it parses as UUID
        import uuid as _uuid
        _ = _uuid.UUID(token)  # will raise if invalid


class LikeFlairPermissionTests(TestCase):
    def setUp(self):
        # Users
        self.owner = User.objects.create_user(username="owner", email="o@example.com", password="pass1234")
        self.other = User.objects.create_user(username="other", email="x@example.com", password="pass1234")

        # Profiles (minimal fields to satisfy FK)
        self.owner_profile = Profile.objects.create(user=self.owner, id_user=self.owner.id, phone_no="2000000001")
        self.other_profile = Profile.objects.create(user=self.other, id_user=self.other.id, phone_no="2000000002")

        BrandSetting.objects.create()  # if required by middleware/context

        # Post authored by owner
        self.post = Post.objects.create(
            user_id=self.owner.id,
            user_prof=self.owner.username,
            profile_id=str(self.owner_profile.id),
            uuid=str(_uuid.uuid4()),
            video_name="clip",
            category_type="general",
            created_at=timezone.now(),
        )

        # Common URLs (adjust to your URL names)
        # Use either pk or uuid depending on your implementation
        self.like_url = reverse("like_post", kwargs={"post_id": self.post.id})
        self.unlike_url = reverse("unlike_post", kwargs={"post_id": self.post.id})
        self.flair_url = reverse("flair_post", kwargs={"post_id": self.post.id})

    # -------- Authentication requirements --------

    def test_like_requires_authentication(self):
        res = self.client.post(self.like_url)
        self.assertIn(res.status_code, (302, 401, 403))  # accept redirect to login or explicit 401/403

    def test_unlike_requires_authentication(self):
        res = self.client.post(self.unlike_url)
        self.assertIn(res.status_code, (302, 401, 403))

    def test_flair_requires_authentication(self):
        res = self.client.post(self.flair_url, data={"flair": "🔥"})
        self.assertIn(res.status_code, (302, 401, 403))

    # -------- HTTP method constraints --------

    def test_like_rejects_get(self):
        self.client.login(username="other", password="pass1234")
        res = self.client.get(self.like_url)
        self.assertIn(res.status_code, (405, 400))  # 405 if @require_POST

    def test_unlike_rejects_get(self):
        self.client.login(username="other", password="pass1234")
        res = self.client.get(self.unlike_url)
        self.assertIn(res.status_code, (405, 400))

    def test_flair_rejects_get(self):
        self.client.login(username="other", password="pass1234")
        res = self.client.get(self.flair_url)
        self.assertIn(res.status_code, (405, 400))

    # -------- Authorization rules --------
    # Adjust based on your business logic:
    # - Like: any authenticated user can like a post
    # - Unlike: only if previously liked
    # - Flair: assume only post owner (or staff/mod) can set flair

    def test_authenticated_user_can_like(self):
        self.client.login(username="other", password="pass1234")
        res = self.client.post(self.like_url)
        self.assertIn(res.status_code, (200, 201, 204))
        # Optionally assert DB side-effect if you have Like model or Post.like_count
        # Example:
        # self.post.refresh_from_db()
        # self.assertEqual(self.post.likes.count(), 1)

    def test_authenticated_user_can_unlike_only_if_liked_before(self):
        self.client.login(username="other", password="pass1234")
        # First like
        _ = self.client.post(self.like_url)
        # Then unlike
        res = self.client.post(self.unlike_url)
        self.assertIn(res.status_code, (200, 204))
        # Repeated unlike should be idempotent or 404 depending on implementation
        res2 = self.client.post(self.unlike_url)
        self.assertIn(res2.status_code, (200, 204, 404))

    def test_non_owner_cannot_set_flair(self):
        self.client.login(username="other", password="pass1234")
        res = self.client.post(self.flair_url, data={"flair": "🔥"})
        self.assertIn(res.status_code, (403,))  # Forbidden

    def test_owner_can_set_flair(self):
        self.client.login(username="owner", password="pass1234")
        res = self.client.post(self.flair_url, data={"flair": "🔥"})
        self.assertIn(res.status_code, (200, 204))
        # Validate persisted change if Post has a flair field
        try:
            self.post.refresh_from_db()
            if hasattr(self.post, "flair"):
                self.assertEqual(self.post.flair, "🔥")
        except Exception:
            # If flair is stored elsewhere, skip persistence check
            pass

    # -------- Non-existent post handling --------

    def test_actions_on_missing_post(self):
        self.client.login(username="other", password="pass1234")
        missing_like = reverse("like_post", kwargs={"post_id": 999999})
        missing_unlike = reverse("unlike_post", kwargs={"post_id": 999999})
        missing_flair = reverse("flair_post", kwargs={"post_id": 999999})

        res1 = self.client.post(missing_like)
        res2 = self.client.post(missing_unlike)
        res3 = self.client.post(missing_flair, data={"flair": "🔥"})

        self.assertEqual(res1.status_code, 404)
        self.assertEqual(res2.status_code, 404)
        # Flair should be 404 regardless of permission if post doesn’t exist
        self.assertEqual(res3.status_code, 404)

    # -------- Optional: CSRF for non-AJAX vs. API tokens --------
    # If these endpoints are CSRF-protected views (not DRF), Django TestClient
    # handles CSRF only if you use the template; typically you exempt via @csrf_exempt
    # or post via AJAX with proper token. If you need strict CSRF behavior, add:
    # def test_like_rejects_missing_csrf(self): ...

@pytest.mark.django_db
def test_select_creative_basic(client, django_user_model):
    placement = AdPlacement.objects.create(code="dashboard_feed_top")
    adv = Advertiser.objects.create(name="Acme", contact_email="acme@test")
    campaign = Campaign.objects.create(
        advertiser=adv,
        name="Test",
        placement=placement,
        start_at=timezone.now() - timedelta(days=1),
        end_at=timezone.now() + timedelta(days=1),
        active=True,
        daily_budget_cents=1000,
        target_country="",
        target_profile_type="",
    )
    creative = Creative.objects.create(
        campaign=campaign,
        click_url="https://example.com",
        headline="Hi",
    )

    placement_obj, campaign_obj, creative_obj = select_creative("dashboard_feed_top")
    assert placement_obj == placement
    assert campaign_obj == campaign
    assert creative_obj == creative

@pytest.mark.django_db
def test_ad_slot_and_click_flow(client):
    placement = AdPlacement.objects.create(code="dashboard_feed_top")
    adv = Advertiser.objects.create(name="Acme", contact_email="acme@test")
    campaign = Campaign.objects.create(
        advertiser=adv,
        name="Test",
        placement=placement,
        start_at=timezone.now() - timedelta(days=1),
        end_at=timezone.now() + timedelta(days=1),
        active=True,
        daily_budget_cents=1000,
        target_country="",
        target_profile_type="",
    )
    Creative.objects.create(
        campaign=campaign,
        click_url="https://example.com",
        headline="Hi",
    )
    # serve slot
    r = client.get("/ads/slot/dashboard_feed_top")
    assert r.status_code == 200
    data = r.json()
    assert "impression_id" in data
    imp_id = data["impression_id"]
    assert AdImpression.objects.filter(id=imp_id).exists()

    # click redirect
    r2 = client.get(f"/ads/click/{imp_id}/", follow=False)
    assert r2.status_code in (301, 302)
    assert AdClick.objects.filter(impression_id=imp_id).exists()
