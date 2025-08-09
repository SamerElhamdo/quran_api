from marshmallow import Schema, fields, validate, validates
from marshmallow.exceptions import ValidationError


class PaginationSchema(Schema):
    """Schema for pagination parameters."""
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=20)


class PaginationResponseSchema(Schema):
    """Schema for pagination response."""
    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int()
    total_pages = fields.Int()


class ErrorSchema(Schema):
    """Schema for error responses."""
    error = fields.Str(required=True)
    details = fields.Dict(missing=None)
    request_id = fields.Str(missing=None)


class SuccessSchema(Schema):
    """Schema for success responses."""
    message = fields.Str(required=True)
    data = fields.Dict(missing=None)


class DateRangeSchema(Schema):
    """Schema for date range parameters."""
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    
    @validates("end_date")
    def validate_date_range(self, value, data):
        """Ensure end_date is after start_date."""
        if "start_date" in data and value <= data["start_date"]:
            raise ValidationError("End date must be after start date")


class SearchSchema(Schema):
    """Schema for search parameters."""
    query = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=20)
    filters = fields.Dict(missing={})
    sort_by = fields.Str(missing="created_at")
    sort_order = fields.Str(validate=validate.OneOf(["asc", "desc"]), missing="desc") 