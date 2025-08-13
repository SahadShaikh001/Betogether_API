<<<<<<< HEAD
from database import SessionLocal, engine
from models import Base, Category

Base.metadata.create_all(bind=engine)

db = SessionLocal()

default_categories = [
    {"name": "Sports", "image": "/static/icons/sports.png"},
    {"name": "find a ride", "image": "/static/icons/ride.png"},
    {"name": "attend show", "image": "/static/icons/show.png"},
    {"name": "join a event", "image": "/static/icons/event.png"},
    {"name": "explore area", "image": "/static/icons/explore.png"},
    {"name": "keep company", "image": "/static/icons/company.png"},
    {"name": "translator", "image": "/static/icons/translator.png"},
    {"name": "transport", "image": "/static/icons/transport.png"},
    {"name": "cooking", "image": "/static/icons/cooking.png"},
    {"name": "plumber", "image": "/static/icons/plumber.png"},
]

for cat in default_categories:
    existing = db.query(Category).filter_by(name=cat["name"]).first()
    if not existing:
        db.add(Category(name=cat["name"], image=cat["image"]))

db.commit()
db.close()
=======
from database import SessionLocal, engine
from models import Base, Category

Base.metadata.create_all(bind=engine)

db = SessionLocal()

default_categories = [
    {"name": "Sports", "image": "/static/icons/sports.png"},
    {"name": "find a ride", "image": "/static/icons/ride.png"},
    {"name": "attend show", "image": "/static/icons/show.png"},
    {"name": "join a event", "image": "/static/icons/event.png"},
    {"name": "explore area", "image": "/static/icons/explore.png"},
    {"name": "keep company", "image": "/static/icons/company.png"},
    {"name": "translator", "image": "/static/icons/translator.png"},
    {"name": "transport", "image": "/static/icons/transport.png"},
    {"name": "cooking", "image": "/static/icons/cooking.png"},
    {"name": "plumber", "image": "/static/icons/plumber.png"},
]

for cat in default_categories:
    existing = db.query(Category).filter_by(name=cat["name"]).first()
    if not existing:
        db.add(Category(name=cat["name"], image=cat["image"]))

db.commit()
db.close()
>>>>>>> 4f4447a70f4a774e40751869788c5d0086421b94
