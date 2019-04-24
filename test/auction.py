from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import exc
import sqlite3
Base = declarative_base()


class User(Base):

    __tablename__ = 'USER'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)


class Item(Base):

    __tablename__ = 'ITEM'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    seller_id = Column(Integer, ForeignKey(User.id))
    seller = relationship(User)


class Bid(Base):

    __tablename__ = 'BID'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey(User.id))
    bidder_id = Column(Integer, ForeignKey(Item.id))
    price = Column(Integer)
    bidder = relationship(User)
    item = relationship(Item)


class Auction(object):

    def create_table(self):
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.create_all(engine)

    def insert_user(self, id, name, password):
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        user = User(id = id, name = name, password = password)
        session.add(user)
        session.commit()
        session.close()

    def post_item(self, user_id, item_id, name, desc):
        seller = self.query_user(user_id)
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        item = Item(id = item_id, name = name, desc = desc, seller_id = user_id, seller = seller)
        session.add(item)
        session.commit()
        session.close()

    def perform_bid(self, bid_id, user_id, item_id, price):
        user = self.query_user(user_id)
        item = self.query_item(item_id)
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        bid = Bid(id=bid_id, bidder_id=user_id, item_id=item_id, bidder=user, item=item,price=price)
        session.add(bid)
        session.commit()
        session.close()


    def query_user(self, user_id):
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        user = session.query(User).filter(User.id == user_id).one()
        session.close()
        if user is not None:
            return user
        else: return None

    def query_item(self, item_id):
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        item = session.query(Item).filter(Item.id == item_id).one()
        session.close()
        return item

    def search_user(self, user_id):
        user = self.query_user(user_id)
        if user is None:
            print("User not found!")
        else:
            print("User name: " + user.name + ", Password: " + user.password + "\n")

    def search_item(self, item_id):
        item = self.query_item(item_id)
        seller = self.query_user(item.seller_id)
        if item is not None:
            print("Item name: " + item.name + ", Description: " + item.desc + ", Seller: " + seller.name + "\n")
        else: return None

    def search_posts(self, user_id):
        user = self.query_user(user_id)
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        items = session.query(Item).filter(Item.seller == user)
        session.close()
        print(user.name + "'s Post: ")
        for item in items:
            print("Item: " + item.name + ", Description: " + item.desc)
        print()

    def search_user_bids(self, user_id):
        user = self.query_user(user_id)
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        bids = session.query(Bid).filter(Bid.bidder == user)
        print(user.name + "'s Bids: ")
        for bid in bids:
            print("item: " + bid.item.name + ", bidder: " + bid.bidder.name + ", price " +str(bid.price))
        print()

    def search_item_bids(self, item_id):
        item = self.query_item(item_id)
        engine = create_engine('sqlite:///auction.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        bids = session.query(Bid).filter(Bid.item == item)
        print(item.name + "'s Bids: ")
        for bid in bids:
            print("item: " + bid.item.name + ", bidder: " + bid.bidder.name + ", price " + str(bid.price))
        print()
