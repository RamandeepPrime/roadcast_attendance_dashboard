import asyncio
from sqlalchemy.orm import Session
from datetime import time
from app.database.database import Roster, RosterMember, RosterShift, Shift, User
from app.database.enums import Role, Weekday
from app.database import SessionFactory
from app.utils.pwd_helper import get_password_hash

# Assuming you have an active session named `session`
session = Session()
async def insert_dummy_data():
    async with SessionFactory() as session:
        # Insert a user
        user1 = User(name="Alice Johnson", email_id="alice@example.com", hashed_password=get_password_hash('1234'), role=Role.MANAGER)
        user2 = User(name="Bob Smith", email_id="bob@example.com", hashed_password=get_password_hash('1234'), role=Role.STAFF)
        user3 = User(name="Mohan Smith", email_id="mohan@example.com", hashed_password=get_password_hash('1234'), role=Role.ADMIN)

        session.add_all([user1, user2, user3])
        await session.commit()
        
        print("Dummy data inserted successfully.")

asyncio.run(insert_dummy_data())