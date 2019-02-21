from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from api.database import Base, Database, read_scope, write_scope


class Food(Base):
    __tablename__ = 'food'
    id = Column(String(32), primary_key=True)
    category = Column(String(32))


favourite_food_table = Table('favourites', Base.metadata,
    Column('person_id', Integer, ForeignKey('person.pid')),
    Column('food_id', String, ForeignKey('food.id'))
)


class Company(Base):
    __tablename__ = 'company'
    cid = Column(Integer, primary_key=True)
    name = Column(String(16))
    employees = relationship("Person") # one-to-many relationship from company to person


friendship = Table(
    'friendship',
    Base.metadata,
    Column('person_id', Integer, ForeignKey('person.pid'), index=True),
    Column('friend_id', Integer, ForeignKey('person.pid')),
    UniqueConstraint('person_id', 'friend_id', name='unique_friendship')) # prohibit `Person` from befriending itself


class Person(Base):
    __tablename__ = 'person'
    pid = Column(Integer, primary_key=True)
    name = Column(String(64))
    age = Column(Integer)
    address = Column(String(128))
    email = Column(String(128))
    phone = Column(String(32))
    eye_color = Column(String(16))
    alive = Column(Boolean)

    company_id = Column(Integer, ForeignKey('company.cid'))

    # a self-referential many-to-many relationship
    friends = relationship('Person',
                           secondary=friendship,
                           primaryjoin=pid == friendship.c.person_id,
                           secondaryjoin=pid == friendship.c.friend_id)

    # many-to-many foods relationship
    favourite_foods = relationship("Food", secondary=favourite_food_table)

    def befriend(self, friend):
        if friend not in self.friends:
            self.friends.append(friend)
            friend.friends.append(self)
