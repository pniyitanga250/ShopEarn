from django.test import TestCase, Client
from django.urls import reverse
from shop_accounts.models import ContactMessage
from django.core import mail


class ContactFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.contact_url = reverse('shop_accounts:contact')
        self.contact_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }

    def test_contact_form_saves_to_database(self):
        """Test that submitting the contact form saves the message to the database"""
        response = self.client.post(self.contact_url, self.contact_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the message was saved to the database
        self.assertEqual(ContactMessage.objects.count(), 1)
        contact_message = ContactMessage.objects.first()
        self.assertEqual(contact_message.name, 'Test User')
        self.assertEqual(contact_message.email, 'test@example.com')
        self.assertEqual(contact_message.subject, 'Test Subject')
        self.assertEqual(contact_message.message, 'This is a test message.')
        
    def test_contact_form_sends_emails(self):
        """Test that submitting the contact form sends emails"""
        # This test will only work if EMAIL_BACKEND is set to the console or memory backend
        with self.settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            DEFAULT_FROM_EMAIL='noreply@shopearn.com',
            CONTACT_EMAIL='peacemakerproofficial@gmail.com'
        ):
            response = self.client.post(self.contact_url, self.contact_data, follow=True)
            self.assertEqual(response.status_code, 200)
            
            # Check that two emails were sent (one to admin, one to user)
            self.assertEqual(len(mail.outbox), 2)
            
            # Check admin email
            admin_email = mail.outbox[0]
            self.assertEqual(admin_email.subject, 'ShopEarn Contact Form: Test Subject')
            self.assertEqual(admin_email.to, ['peacemakerproofficial@gmail.com'])
            
            # Check user confirmation email
            user_email = mail.outbox[1]
            self.assertEqual(user_email.subject, 'Thank you for contacting ShopEarn')
            self.assertEqual(user_email.to, ['test@example.com'])