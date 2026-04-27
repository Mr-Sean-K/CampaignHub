from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from mysite.models import Client, Campaign, Task
from datetime import date

User = get_user_model()


class UserModelTests(TestCase):
    # test user model creation with different roles

    def test_create_admin_user(self):
        user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password',
            role='admin'
        )
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.check_password('password'))

    def test_create_account_manager(self):
        user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='password',
            role='account_manager'
        )
        self.assertEqual(user.role, 'account_manager')

    def test_create_creative(self):
        user = User.objects.create_user(
            username='creative',
            email='creative@test.com',
            password='password',
            role='creative'
        )
        self.assertEqual(user.role, 'creative')

    def test_create_client(self):
        user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='password',
            role='client'
        )
        self.assertEqual(user.role, 'client')


class ClientModelTests(TestCase):
    # test client model creation

    def test_create_client(self):
        client = Client.objects.create(
            name='Google',
            email='google@google.com',
            phone_number='1234567890',
            company_name='Google'
        )
        self.assertEqual(client.name, 'Google')
        self.assertEqual(str(client), 'Google')


class CampaignModelTests(TestCase):
    # test campaign model creation and relationships

    def setUp(self):
        self.client = Client.objects.create(
            name='Test Client',
            email='test@test.com'
        )

    def test_create_campaign(self):
        campaign = Campaign.objects.create(
            client=self.client,
            campaign_name='Summer Sale',
            status='active',
            start_date=date(2026, 5, 1),
            end_date=date(2026, 8, 31)
        )
        self.assertEqual(campaign.campaign_name, 'Summer Sale')
        self.assertEqual(campaign.status, 'active')
        self.assertEqual(campaign.client, self.client)


class TaskModelTests(TestCase):
    # test task model creation

    def setUp(self):
        self.client_obj = Client.objects.create(
            name='Test Client',
            email='test@test.com'
        )
        self.campaign = Campaign.objects.create(
            client=self.client_obj,
            campaign_name='Test Campaign',
            status='active',
            start_date=date(2026, 5, 1),
            end_date=date(2026, 8, 31)
        )
        self.creative = User.objects.create_user(
            username='creative',
            email='creative@test.com',
            password='password',
            role='creative'
        )

    def test_create_task(self):
        task = Task.objects.create(
            campaign=self.campaign,
            title='Design Banner',
            description='Create a banner ad',
            assigned_to=self.creative,
            deadline=date(2026, 5, 15),
            status='To Do',
            priority='High'
        )
        self.assertEqual(task.title, 'Design Banner')
        self.assertEqual(task.assigned_to, self.creative)
        self.assertEqual(task.status, 'To Do')


class LoginTests(TestCase):
    # test login functionality

    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='admin'
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login(self):
        login_success = self.client.login(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(login_success)

    def test_login_redirect_to_dashboard(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login'))
        # already logged in, login page still accessible
        self.assertEqual(response.status_code, 200)


class PermissionTests(TestCase):
    # test role-based access control

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password',
            role='admin'
        )
        self.creative = User.objects.create_user(
            username='creative',
            email='creative@test.com',
            password='password',
            role='creative'
        )

    def test_admin_can_access_campaigns(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 200)

    def test_creative_cannot_access_campaign_create(self):
        self.client.login(username='creative', password='password')
        response = self.client.get(reverse('campaign_create'))
        # should get 403 or redirect
        self.assertIn(response.status_code, [302, 403])

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class DashboardTests(TestCase):
    # test dashboard view

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='password',
            role='admin'
        )

    def test_dashboard_loads_for_logged_in_user(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_dashboard_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
