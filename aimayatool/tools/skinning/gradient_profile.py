from __future__ import absolute_import


def inverse_distance_ratios(distances):
    """Map distances to normalized inverse ratios: nearest=1, farthest=0."""
    values = [float(value) for value in (distances or [])]
    if not values:
        return []
    if any(value < 0.0 for value in values):
        raise ValueError("Distances must be non-negative")
    minimum = min(values)
    maximum = max(values)
    span = maximum - minimum
    if abs(span) <= 1e-8:
        return [1.0 for _ in values]
    result = []
    for value in values:
        ratio = (value - minimum) / span
        ratio = max(0.0, min(1.0, ratio))
        result.append(1.0 - ratio)
    return result


def sample_distance_profile(distances, sampler=None):
    """Sample inverse-distance ratios through a normalized 0..1 profile sampler."""
    ratios = inverse_distance_ratios(distances)
    if sampler is None:
        from .weight_profile import sample_profile
        sampler = sample_profile
    values = [float(sampler(ratio)) for ratio in ratios]
    for value in values:
        if value < -1e-8 or value > 1.0 + 1e-8:
            raise ValueError("Profile sampler must return normalized values")
    return values
