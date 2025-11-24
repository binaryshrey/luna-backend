from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from math import exp, radians, sin, cos, atan2, sqrt

from app.models.user import User
from app.models.venue import Venue
from app.models.interactions import UserVenueInteraction
from app.models.social import UserSocialEdge
from app.schemas.reco import VenueReco, UserReco

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute distance between two lat/lng points using the Haversine formula."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def recommend_venues_for_user(
    db: Session,
    user_id: UUID,
    limit: int = 10,
) -> List[VenueReco]:
    """
    Recommend venues for a user, blending:
    - spatial proximity
    - user-specific preferences (likes + dwell time)
    - global popularity
    """

    user = db.query(User).get(user_id)
    if not user or user.home_lat is None or user.home_lng is None:
        return []

    venues = db.query(Venue).all()
    if not venues:
        return []

    # Global popularity: how many users liked/interested in each venue
    popularity_counts: dict[UUID, int] = {}
    for v in venues:
        count = (
            db.query(UserVenueInteraction)
            .filter(
                UserVenueInteraction.venue_id == v.id,
                UserVenueInteraction.interaction_type.in_(["like", "interest"]),
            )
            .count()
        )
        popularity_counts[v.id] = count

    max_pop = max(popularity_counts.values(), default=1)

    recos: list[VenueReco] = []

    for v in venues:
        dist_km = haversine_km(user.home_lat, user.home_lng, v.lat, v.lng)

        # User-specific preferences from past interactions
        interactions = (
            db.query(UserVenueInteraction)
            .filter(
                UserVenueInteraction.user_id == user_id,
                UserVenueInteraction.venue_id == v.id,
            )
            .all()
        )

        like_count = sum(
            1 for i in interactions if i.interaction_type in ("like", "interest")
        )
        view_time = sum(i.dwell_time_seconds for i in interactions)

        # crude normalization: 1 like ~0.5, 300s view ~1.0
        preference_score = min(1.0, like_count * 0.5 + view_time / 300.0)
        spatial_score = exp(-0.3 * dist_km)
        popularity_score = popularity_counts[v.id] / max_pop if max_pop else 0.0

        # blended score
        venue_score = (
            0.4 * spatial_score
            + 0.4 * preference_score
            + 0.2 * popularity_score
        )

        recos.append(
            VenueReco(
                venue_id=v.id,
                score=float(venue_score),
                distance_km=float(dist_km),
            )
        )

    recos.sort(key=lambda r: r.score, reverse=True)
    return recos[:limit]


def recommend_people_for_user(
    db: Session,
    user_id: UUID,
    venue_id: UUID | None,
    limit: int = 10,
) -> List[UserReco]:
    """
    Recommend people to go with `user_id`.

    Logic:
    - Always start from the existing social graph (UserSocialEdge).
    - If `venue_id` is provided:
        - Boost users who have interacted positively with that venue.
        - Boost users who like venues in the same category.
    """

    # Start from social edges (friends/mutuals)
    edges = (
        db.query(UserSocialEdge)
        .filter(UserSocialEdge.user_id == user_id)
        .all()
    )

    if not edges:
        return []

    target_venue: Venue | None = None
    same_category_venue_ids: set[UUID] = set()

    if venue_id is not None:
        # The specific venue user is looking at
        target_venue = db.query(Venue).get(venue_id)
        if target_venue is not None and target_venue.category:
            # All venues in the same category
            same_category_venue_ids = {
                row.id
                for row in db.query(Venue.id)
                .filter(Venue.category == target_venue.category)
                .all()
            }

    recos: list[UserReco] = []

    for edge in edges:
        base_strength = float(edge.strength or 0.0)

        direct_pref = 0.0
        category_pref = 0.0

        if venue_id is not None and target_venue is not None:
            # ----- Direct preference for this specific venue -----
            direct_interactions = (
                db.query(UserVenueInteraction)
                .filter(
                    UserVenueInteraction.user_id == edge.other_user_id,
                    UserVenueInteraction.venue_id == venue_id,
                )
                .all()
            )

            direct_like_count = sum(
                1
                for i in direct_interactions
                if i.interaction_type in ("like", "interest")
            )
            direct_view_time = sum(i.dwell_time_seconds for i in direct_interactions)

            # 1 like ~ 0.5, 300s ~ 1.0
            direct_pref = min(1.0, direct_like_count * 0.5 + direct_view_time / 300.0)

            # ----- Category-level preference (same category as target venue) -----
            if same_category_venue_ids:
                cat_interactions = (
                    db.query(UserVenueInteraction)
                    .filter(
                        UserVenueInteraction.user_id == edge.other_user_id,
                        UserVenueInteraction.venue_id.in_(same_category_venue_ids),
                    )
                    .all()
                )

                cat_like_count = sum(
                    1
                    for i in cat_interactions
                    if i.interaction_type in ("like", "interest")
                )
                cat_view_time = sum(i.dwell_time_seconds for i in cat_interactions)

                # Softer normalization; we don't want category to dominate
                category_pref = min(
                    1.0,
                    cat_like_count * 0.3 + cat_view_time / 600.0,
                )

        # Final score:
        # - social edge strength is still primary
        # - direct venue preference is next
        # - category-level affinity is a smaller bump
        score = (
            0.6 * base_strength +
            0.25 * direct_pref +
            0.15 * category_pref
        )

        recos.append(
            UserReco(
                user_id=edge.other_user_id,
                score=float(score),
            )
        )

    recos.sort(key=lambda r: r.score, reverse=True)
    return recos[:limit]
