from marshmallow import Schema, fields, validate, validates, ValidationError
import re


class LoginSchema(Schema):
    """Schema for user login."""
    email_or_phone = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=255))


class RegisterSchema(Schema):
    """Schema for user registration."""
    email_or_phone = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=255))
    display_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    locale = fields.Str(validate=validate.OneOf(["ar", "en", "tr", "ur"]))
    
    @validates("email_or_phone")
    def validate_email_or_phone(self, value):
        """Validate email or phone format."""
        # Check if it's an email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        # Check if it's a phone number (international format)
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        
        if not (re.match(email_pattern, value) or re.match(phone_pattern, value)):
            raise ValidationError("Must be a valid email or phone number")
    
    @validates("password")
    def validate_password(self, value):
        """Validate password strength."""
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Check for at least one letter and one number
        if not re.search(r'[a-zA-Z]', value) or not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one letter and one number")


class UserSchema(Schema):
    """Schema for user data."""
    id = fields.Str(dump_only=True)
    email_or_phone = fields.Str(dump_only=True)
    display_name = fields.Str(required=True)
    role = fields.Str(dump_only=True)
    locale = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TokenSchema(Schema):
    """Schema for JWT tokens."""
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    token_type = fields.Str(dump_only=True, default="bearer")


class PasswordChangeSchema(Schema):
    """Schema for password change."""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=255))
    
    @validates("new_password")
    def validate_new_password(self, value):
        """Validate new password strength."""
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Check for at least one letter and one number
        if not re.search(r'[a-zA-Z]', value) or not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one letter and one number")


class ProfileUpdateSchema(Schema):
    """Schema for profile updates."""
    display_name = fields.Str(validate=validate.Length(min=1, max=255))
    locale = fields.Str(validate=validate.OneOf(["ar", "en", "tr", "ur"])) 