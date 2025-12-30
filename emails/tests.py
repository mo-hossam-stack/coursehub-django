from django.test import TestCase
from emails.models import Email, EmailVerificationEvent
from emails import services

class OTPVerificationTest(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.email_obj, _ = Email.objects.get_or_create(email=self.email)
        
    def test_otp_generation(self):
        obj, sent = services.start_verification_event(self.email)
        self.assertIsNotNone(obj.otp)
        self.assertEqual(len(obj.otp), 6)
        self.assertTrue(obj.otp.isdigit())

    def test_verify_otp_success(self):
        obj, sent = services.start_verification_event(self.email)
        success, msg, email_obj = services.verify_otp(self.email, obj.otp)
        self.assertTrue(success)
        self.assertEqual(email_obj, self.email_obj)
        
        # Check if expired
        obj.refresh_from_db()
        self.assertTrue(obj.expired)

    def test_verify_otp_failure_invalid_code(self):
        obj, sent = services.start_verification_event(self.email)
        success, msg, email_obj = services.verify_otp(self.email, "000000") # Assuming random code isn't 000000
        self.assertFalse(success)
        self.assertEqual(msg, "Invalid code")
        
        obj.refresh_from_db()
        self.assertEqual(obj.attempts, 1) # incremented

    def test_verify_otp_max_attempts(self):
        obj, sent = services.start_verification_event(self.email)
        max_attempts = 3
        
        for _ in range(max_attempts):
            services.verify_otp(self.email, "000000", max_attempts=max_attempts)
            
        obj.refresh_from_db()
        self.assertEqual(obj.attempts, 3)
        self.assertTrue(obj.expired) # Last attempt should expire it
        
        # Verify next attempt fails with max attempts
        success, msg, email_obj = services.verify_otp(self.email, "000000", max_attempts=max_attempts)
        self.assertFalse(success)
        self.assertEqual(msg, "Code expired")

    def test_rate_limiting(self):
        # Create 4 more events (total 5 including default sent in logic if any, but start_verification_event creates one)
        # Note: setUp does NOT create an event, just an email_obj.
        
        for _ in range(5):
             obj, sent = services.start_verification_event(self.email)
             self.assertIsNotNone(obj)
        
        # 6th attempt should fail
        obj, sent = services.start_verification_event(self.email)
        self.assertIsNone(obj)
        self.assertFalse(sent)

    def test_multiple_valid_otps(self):
        obj1, _ = services.start_verification_event(self.email)
        obj2, _ = services.start_verification_event(self.email) # This might fail if rate limit is tight, but we assume limit > 2
        
        success, msg, email_obj = services.verify_otp(self.email, obj1.otp)
        self.assertTrue(success)
        
        obj1.refresh_from_db()
        obj2.refresh_from_db()
        self.assertTrue(obj1.expired)
        self.assertTrue(obj2.expired)
