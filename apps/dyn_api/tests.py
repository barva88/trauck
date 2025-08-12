# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.test import TestCase
from django.urls import reverse


class DynRoutesTests(TestCase):
    def test_dyn_api_index(self):
        resp = self.client.get(reverse('dynamic_api'))
        self.assertEqual(resp.status_code, 200)
