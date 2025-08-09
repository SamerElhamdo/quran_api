"""
Download schemas for the Quran Learning API
"""
from marshmallow import Schema, fields, validate


class DownloadSchema(Schema):
    """Download schema for responses."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    ayah_id = fields.Int()
    reciter_id = fields.Int()
    file_path = fields.Str()
    file_size = fields.Int()
    status = fields.Str(validate=validate.OneOf(["pending", "downloading", "completed", "failed"]))
    progress = fields.Float(validate=validate.Range(min=0, max=100))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class DownloadCreateSchema(Schema):
    """Download creation schema for requests."""
    ayah_id = fields.Int(required=True)
    reciter_id = fields.Int(required=True) 