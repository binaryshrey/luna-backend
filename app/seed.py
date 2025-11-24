# app/seed.py

import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.session import engine, SessionLocal, Base
from app.models.user import User
from app.models.venue import Venue
from app.models.interactions import UserVenueInteraction
from app.models.social import UserSocialEdge
from app.models.plan import Plan, PlanParticipant


# -------------------------
# Helper: create all tables
# -------------------------
def init_db():
    Base.metadata.create_all(bind=engine)


def seed(db: Session):
    # Avoid double seeding
    if db.query(User).first():
        print("Seed data already exists, skipping.")
        return

    # -------------------------
    # Users (24 users)
    # -------------------------
    base_lat, base_lng = 40.73061, -73.935242

    user_specs = [
        ("alice", "Alice Chen", 25),
        ("bob", "Bob Singh", 27),
        ("carol", "Carol Martinez", 24),
        ("dave", "Dave Johnson", 29),
        ("eva", "Eva Rossi", 23),
        ("frank", "Frank Müller", 31),
        ("grace", "Grace Lee", 26),
        ("henry", "Henry Patel", 28),
        ("irene", "Irene Kim", 22),
        ("jack", "Jack Thompson", 30),
        ("kira", "Kira Nakamura", 24),
        ("liam", "Liam O'Connor", 27),
        ("mia", "Mia Fernandez", 25),
        ("noah", "Noah Williams", 29),
        ("olivia", "Olivia Brown", 26),
        ("peter", "Peter Novak", 32),
        ("quinn", "Quinn Zhang", 23),
        ("ryan", "Ryan Carter", 28),
        ("sofia", "Sofia Alvarez", 24),
        ("tom", "Tom Anders", 27),
        ("uma", "Uma Desai", 22),
        ("victor", "Victor Costa", 29),
        ("wendy", "Wendy Park", 25),
        ("yuri", "Yuri Petrov", 30),
    ]

    users: list[User] = []
    for handle, name, age in user_specs:
        jitter_lat = base_lat + random.uniform(-0.02, 0.02)
        jitter_lng = base_lng + random.uniform(-0.02, 0.02)
        users.append(
            User(
                handle=handle,
                name=name,
                home_lat=jitter_lat,
                home_lng=jitter_lng,
                age=age,
            )
        )

    db.add_all(users)
    db.commit()
    for u in users:
        db.refresh(u)

    # convenient references
    alice = users[0]
    bob = users[1]
    carol = users[2]
    dave = users[3]
    eva = users[4]

    # -------------------------
    # Venues (20 venues)
    # -------------------------
    venues_data = [
        (
            "Sunset Rooftop Bar",
            "Rooftop cocktails with skyline view.",
            "bar",
            40.7325,
            -73.99,
            3,
            4.7,
        ),
        (
            "Midnight Coffee Lab",
            "Late-night coffee and board games.",
            "cafe",
            40.729,
            -73.94,
            2,
            4.5,
        ),
        (
            "Riverside Jazz Club",
            "Live jazz every weekend.",
            "music",
            40.738,
            -73.96,
            3,
            4.8,
        ),
        (
            "Neighborhood Pizza Spot",
            "Casual pizza with outdoor seating.",
            "restaurant",
            40.731,
            -73.937,
            1,
            4.3,
        ),
        (
            "Brooklyn Street Tacos",
            "Street-style tacos and margaritas.",
            "restaurant",
            40.7295,
            -73.99,
            2,
            4.6,
        ),
        (
            "Greenpoint Game Night",
            "Board games bar with craft beers.",
            "bar",
            40.735,
            -73.95,
            2,
            4.4,
        ),
        (
            "Lo-Fi Listening Lounge",
            "Chill lo-fi music and low lighting.",
            "music",
            40.736,
            -73.97,
            3,
            4.7,
        ),
        (
            "Hudson River Walk Café",
            "Coffee by the water with outdoor seating.",
            "cafe",
            40.739,
            -73.99,
            2,
            4.2,
        ),
        (
            "Indie Film Microcinema",
            "Small cinema showing indie films.",
            "cinema",
            40.728,
            -73.932,
            3,
            4.5,
        ),
        (
            "Underground Comedy Cellar",
            "Stand-up comedy nights in the basement.",
            "comedy",
            40.733,
            -73.938,
            2,
            4.8,
        ),
        (
            "Karaoke Nights Studio",
            "Private karaoke rooms until late.",
            "karaoke",
            40.727,
            -73.936,
            3,
            4.4,
        ),
        (
            "Vegan Bowl Corner",
            "Healthy bowls and smoothies.",
            "restaurant",
            40.734,
            -73.941,
            2,
            4.1,
        ),
        (
            "Vintage Arcade Bar",
            "Retro arcade machines and craft beer.",
            "bar",
            40.737,
            -73.943,
            2,
            4.5,
        ),
        (
            "Chelsea Art Loft",
            "Gallery with rotating exhibitions and wine nights.",
            "art",
            40.746,
            -74.002,
            3,
            4.6,
        ),
        (
            "Rooftop Yoga Studio",
            "Morning yoga with a skyline view.",
            "wellness",
            40.741,
            -73.989,
            2,
            4.7,
        ),
        (
            "Harbor Sunset Cruise",
            "Boat cruise with music and drinks.",
            "experience",
            40.703,
            -74.013,
            4,
            4.9,
        ),
        (
            "Speakeasy Cocktail Den",
            "Hidden speakeasy with classic cocktails.",
            "bar",
            40.724,
            -73.995,
            3,
            4.8,
        ),
        (
            "Open Mic Poetry Night",
            "Spoken word and poetry open mic.",
            "music",
            40.72,
            -73.99,
            1,
            4.3,
        ),
        (
            "Tech Meetup Hub",
            "Coworking space hosting evening meetups.",
            "cowork",
            40.742,
            -73.98,
            2,
            4.4,
        ),
        (
            "Climbing Gym Hangout",
            "Indoor bouldering with a café corner.",
            "sports",
            40.748,
            -73.993,
            3,
            4.6,
        ),
    ]

    venues: list[Venue] = []
    for name, desc, cat, lat, lng, price, rating in venues_data:
        venues.append(
            Venue(
                name=name,
                description=desc,
                category=cat,
                lat=lat,
                lng=lng,
                price_level=price,
                rating=rating,
            )
        )

    db.add_all(venues)
    db.commit()
    for v in venues:
        db.refresh(v)

    # -------------------------
    # Interactions (lots)
    # -------------------------
    def add_interaction(user: User, venue: Venue, itype: str, dwell: int):
        iv = UserVenueInteraction(
            user_id=user.id,
            venue_id=venue.id,
            interaction_type=itype,
            dwell_time_seconds=dwell,
        )
        db.add(iv)

    interaction_types = ["view", "view", "like", "interest", "view", "like"]

    # Some hand-crafted patterns for a few users
    # Alice: rooftops, coffee, art
    add_interaction(alice, venues[0], "like", 260)
    add_interaction(alice, venues[1], "interest", 200)
    add_interaction(alice, venues[13], "like", 220)

    # Bob: jazz, comedy, bar
    add_interaction(bob, venues[2], "like", 300)
    add_interaction(bob, venues[9], "interest", 180)
    add_interaction(bob, venues[5], "like", 210)

    # Carol: coffee, vegan, yoga
    add_interaction(carol, venues[1], "like", 240)
    add_interaction(carol, venues[11], "like", 230)
    add_interaction(carol, venues[14], "interest", 190)

    # Dave: rooftop, speakeasy, tacos
    add_interaction(dave, venues[0], "interest", 180)
    add_interaction(dave, venues[4], "like", 220)
    add_interaction(dave, venues[16], "like", 250)

    # Eva: film, poetry, art
    add_interaction(eva, venues[8], "like", 260)
    add_interaction(eva, venues[17], "like", 240)
    add_interaction(eva, venues[13], "interest", 200)

    # Now randomized interactions for all users across venues
    for user in users:
        # Each user interacts with 8–12 venues
        k = random.randint(8, min(12, len(venues)))
        sampled_venues = random.sample(venues, k=k)
        for v in sampled_venues:
            itype = random.choice(interaction_types)
            base = 30 if itype == "view" else 120
            dwell = base + random.randint(0, 240)
            add_interaction(user, v, itype, dwell)

    db.commit()

    # -------------------------
    # Social graph (dense between all 24 users)
    # -------------------------
    edges: list[UserSocialEdge] = []

    for i, u1 in enumerate(users):
        for j, u2 in enumerate(users):
            if i == j:
                continue

            # Stronger curated edges for a few pairs
            handles = {u1.handle, u2.handle}
            if handles == {"alice", "bob"}:
                strength = 0.95
                rel = "friend"
            elif handles == {"alice", "carol"}:
                strength = 0.8
                rel = "mutual"
            elif handles == {"bob", "dave"}:
                strength = 0.85
                rel = "friend"
            elif handles == {"eva", "mia"}:
                strength = 0.8
                rel = "friend"
            else:
                strength = round(random.uniform(0.3, 0.9), 2)
                rel = random.choice(["friend", "mutual", "suggested"])

            edges.append(
                UserSocialEdge(
                    user_id=u1.id,
                    other_user_id=u2.id,
                    relationship_type=rel,
                    strength=strength,
                )
            )

    db.add_all(edges)
    db.commit()

    # -------------------------
    # Example plans (5 plans, multiple participants)
    # -------------------------
    plans: list[Plan] = []

    # Plan 1: Alice organizing rooftop night tomorrow
    plans.append(
        Plan(
            organizer_id=alice.id,
            venue_id=venues[0].id,
            start_time=datetime.utcnow() + timedelta(days=1),
            status="pending",
        )
    )
    # Plan 2: Bob organizing jazz + bar night in 2 days
    plans.append(
        Plan(
            organizer_id=bob.id,
            venue_id=venues[2].id,
            start_time=datetime.utcnow() + timedelta(days=2),
            status="pending",
        )
    )
    # Plan 3: Carol organizing coffee meetup next week
    plans.append(
        Plan(
            organizer_id=carol.id,
            venue_id=venues[1].id,
            start_time=datetime.utcnow() + timedelta(days=7),
            status="pending",
        )
    )
    # Plan 4: Tech meetup at cowork hub
    plans.append(
        Plan(
            organizer_id=dave.id,
            venue_id=venues[18].id,
            start_time=datetime.utcnow() + timedelta(days=3),
            status="pending",
        )
    )
    # Plan 5: Climbing gym hangout
    plans.append(
        Plan(
            organizer_id=eva.id,
            venue_id=venues[19].id,
            start_time=datetime.utcnow() + timedelta(days=5),
            status="pending",
        )
    )

    db.add_all(plans)
    db.commit()
    for p in plans:
        db.refresh(p)

    participants: list[PlanParticipant] = []

    # Plan 1: rooftop – Alice, Bob, Grace, Henry, Olivia
    for u, status in [
        (alice, "accepted"),
        (bob, "accepted"),
        (users[6], "invited"),   # Grace
        (users[7], "invited"),   # Henry
        (users[14], "invited"),  # Olivia
    ]:
        participants.append(
            PlanParticipant(plan_id=plans[0].id, user_id=u.id, status=status)
        )

    # Plan 2: jazz – Bob, Frank, Jack, Ryan, Victor
    for u, status in [
        (bob, "accepted"),
        (users[5], "invited"),   # Frank
        (users[9], "invited"),   # Jack
        (users[17], "invited"),  # Ryan
        (users[21], "invited"),  # Victor
    ]:
        participants.append(
            PlanParticipant(plan_id=plans[1].id, user_id=u.id, status=status)
        )

    # Plan 3: coffee – Carol, Eva, Irene, Quinn, Sofia
    for u, status in [
        (carol, "accepted"),
        (eva, "accepted"),
        (users[8], "invited"),   # Irene
        (users[16], "invited"),  # Quinn
        (users[18], "invited"),  # Sofia
    ]:
        participants.append(
            PlanParticipant(plan_id=plans[2].id, user_id=u.id, status=status)
        )

    # Plan 4: tech meetup – Dave, Liam, Noah, Peter, Tom
    for u, status in [
        (dave, "accepted"),
        (users[11], "invited"),  # Liam
        (users[13], "invited"),  # Noah
        (users[15], "invited"),  # Peter
        (users[19], "invited"),  # Tom
    ]:
        participants.append(
            PlanParticipant(plan_id=plans[3].id, user_id=u.id, status=status)
        )

    # Plan 5: climbing – Eva, Mia, Uma, Wendy, Yuri
    for u, status in [
        (eva, "accepted"),
        (users[12], "invited"),  # Mia
        (users[20], "invited"),  # Uma
        (users[22], "invited"),  # Wendy
        (users[23], "invited"),  # Yuri
    ]:
        participants.append(
            PlanParticipant(plan_id=plans[4].id, user_id=u.id, status=status)
        )

    db.add_all(participants)
    db.commit()

    print(
        f"Seed data inserted: {len(users)} users, {len(venues)} venues, "
        f"{db.query(UserVenueInteraction).count()} interactions, "
        f"{db.query(UserSocialEdge).count()} social edges, "
        f"{db.query(Plan).count()} plans."
    )


if __name__ == "__main__":
    print("Initializing DB...")
    init_db()
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
