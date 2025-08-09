"""
User settings schemas for the Quran Learning API
"""
from marshmallow import Schema, fields, validate


class UserSettingsSchema(Schema):
    """User settings schema for responses."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    language = fields.Str(validate=validate.OneOf(["ar", "en", "ur"]))
    theme = fields.Str(validate=validate.OneOf(["light", "dark", "auto"]))
    notifications_enabled = fields.Bool()
    auto_play = fields.Bool()
    download_quality = fields.Str(validate=validate.OneOf(["low", "medium", "high"]))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserSettingsUpdateSchema(Schema):
    """User settings update schema for requests."""
    language = fields.Str(validate=validate.OneOf(["ar", "en", "ur"]), required=False)
    theme = fields.Str(validate=validate.OneOf(["light", "dark", "auto"]), required=False)
    notifications_enabled = fields.Bool(required=False)
    auto_play = fields.Bool(required=False)
    download_quality = fields.Str(validate=validate.OneOf(["low", "medium", "high"]), required=False) 