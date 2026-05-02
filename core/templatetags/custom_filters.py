from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def split_csv(value):
    """Split a comma-separated string into a list."""
    if not value:
        return []
    return [s.strip() for s in value.split(',') if s.strip()]

@register.filter
def entry_rowspan(entry):
    """Return the number of rows an entry should span (works for TimetableEntry and SavedTimetableEntry)."""
    if entry is None:
        return 1
    return entry.end_time - entry.start_time
