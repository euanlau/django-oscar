from django.test import TestCase
from django_dynamic_fixture import G

from oscar.core.compat import get_user_model
from oscar.apps.catalogue.reviews import forms, models
from oscar.test.factories import create_product

User = get_user_model()


class TestReviewForm(TestCase):

    def setUp(self):
        self.product = create_product()
        self.reviewer = G(User)
        self.data = {
            'title': '  This product is lovely',
            'body': 'I really like this cheese',
            'score': 0,
            'name': 'JR Hartley',
            'email': 'hartley@example.com'
        }

    def test_cleans_title(self):
        instance = self.product.reviews.model(
            product=self.product)
        form = forms.ProductReviewForm(data=self.data, instance=instance)
        self.assertTrue(form.is_valid())
        review = form.save()
        self.assertEquals("This product is lovely", review.title)


class TestVoteForm(TestCase):

    def setUp(self):
        self.product = create_product()
        self.reviewer = G(User)
        self.voter = G(User)
        self.review = self.product.reviews.create(
            title='This is nice',
            score=3,
            body="This is the body",
            user=self.reviewer)

    def test_allows_real_users_to_vote(self):
        instance = models.Vote(review=self.review, user=self.voter)
        form = forms.VoteForm(data={}, instance=instance)
        self.assertTrue(form.is_valid())

    def test_prevents_users_from_voting_more_than_once(self):
        self.review.vote_up(self.voter)
        instance = models.Vote(review=self.review, user=self.voter)
        form = forms.VoteForm({}, instance=instance)
        self.assertFalse(form.is_valid())

    def test_prevents_users_voting_on_their_own_reviews(self):
        instance = models.Vote(review=self.review, user=self.reviewer)
        form = forms.VoteForm({}, instance=instance)
        self.assertFalse(form.is_valid())
