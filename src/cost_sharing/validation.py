"""Validation utilities for request data."""

from flask import jsonify


def validate_json_body(request):
    """
    Validate that request body contains valid JSON.

    Args:
        request: Flask request object

    Returns:
        tuple: (data: dict|None, error: tuple|None)
        If valid: (parsed_json_dict, None)
        If invalid: (None, (jsonify(...), status_code))
    """
    data = request.get_json(silent=True)
    if data is None:
        error = (jsonify({
            "error": "Validation failed",
            "message": "Invalid JSON"
        }), 400)
        return None, error
    return data, None


def validate_required_string(data, field_name, min_len=1, max_len=None):
    """
    Validate and extract a required string field from request data.

    Args:
        data: Dictionary containing request data
        field_name: Name of the field to validate
        min_len: Minimum length (default: 1)
        max_len: Maximum length (None for no max)

    Returns:
        tuple: (value: str|None, error: tuple|None)
        If valid: (validated_string, None)
        If invalid: (None, (jsonify(...), status_code))
    """
    value = data.get(field_name)
    if value is None:
        error = (jsonify({
            "error": "Validation failed",
            "message": f"{field_name} is required"
        }), 400)
        return None, error

    if not isinstance(value, str) or len(value) < min_len:
        char_text = "character" if min_len == 1 else "characters"
        error = (jsonify({
            "error": "Validation failed",
            "message": f"{field_name} must be at least {min_len} {char_text}"
        }), 400)
        return None, error

    if max_len is not None and len(value) > max_len:
        error = (jsonify({
            "error": "Validation failed",
            "message": f"{field_name} must be at most {max_len} characters"
        }), 400)
        return None, error

    return value, None


def validate_optional_string(data, field_name, max_len=None):
    """
    Validate an optional string field from request data.

    Args:
        data: Dictionary containing request data
        field_name: Name of the field to validate
        max_len: Maximum length (None for no max)

    Returns:
        tuple: (value: str|None, error: tuple|None)
        If field missing: (None, None) - Valid, just not provided
        If field invalid: (None, error) - Invalid value provided
        If field valid: (validated_string, None) - Valid value provided
    """
    value = data.get(field_name)
    if value is None:
        return None, None  # Valid - field is optional

    if not isinstance(value, str):
        error = (jsonify({
            "error": "Validation failed",
            "message": f"{field_name} must be a string"
        }), 400)
        return None, error

    if max_len is not None and len(value) > max_len:
        error = (jsonify({
            "error": "Validation failed",
            "message": f"{field_name} must be at most {max_len} characters"
        }), 400)
        return None, error

    return value, None


def validate_required_query_param(request, param_name):
    """
    Validate a required query parameter.

    Args:
        request: Flask request object
        param_name: Name of the query parameter

    Returns:
        tuple: (value: str|None, error: tuple|None)
        If valid: (parameter_value, None)
        If invalid: (None, (jsonify(...), status_code))
    """
    value = request.args.get(param_name)
    if not value:
        error = (jsonify({
            "error": "Validation failed",
            "message": f"{param_name} parameter is required"
        }), 400)
        return None, error
    return value, None
