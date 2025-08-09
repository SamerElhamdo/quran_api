"""
Playlist schemas for the Quran Learning API
"""
from marshmallow import Schema, fields, validate


class PlaylistItemSchema(Schema):
    """Playlist item schema for responses."""
    id = fields.Int(dump_only=True)
    playlist_id = fields.Int(dump_only=True)
    ayah_id = fields.Int()
    order = fields.Int()
    created_at = fields.DateTime(dump_only=True)


class PlaylistSchema(Schema):
    """Playlist schema for responses."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    is_public = fields.Bool()
    items = fields.Nested(PlaylistItemSchema, many=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PlaylistCreateSchema(Schema):
    """Playlist creation schema for requests."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500), required=False)
    is_public = fields.Bool(required=False, default=False)


class PlaylistUpdateSchema(Schema):
    """Playlist update schema for requests."""
    name = fields.Str(validate=validate.Length(min=1, max=100), required=False)
    description = fields.Str(validate=validate.Length(max=500), required=False)
    is_public = fields.Bool(required=False) 