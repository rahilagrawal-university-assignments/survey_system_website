import unittest
import os
from auction import *
from sqlalchemy import exc, orm


class TestUser(unittest.TestCase):

    def setUp(self):
        self.auction = Auction()
        self.auction.create_table()

    def test_insert_empty_user(self):
        with self.assertRaises(TypeError):
            self.auction.insert_user('0')

    def test_successfully_insert_user(self):
        self.auction.insert_user('0', 'Jack', '123123')
        user = self.auction.query_user('0')
        self.assertEqual(user.id, 0)
        self.assertEqual(user.name, 'Jack')
        self.assertEqual(user.password, '123123')

    def test_insert_duplicate_user(self):
        self.auction.insert_user('0', 'Jack', '123123')
        with self.assertRaises(exc.IntegrityError):
            self.auction.insert_user('0', 'Jack', '123123')

    def test_insert_user_with_duplicate_id(self):
        self.auction.insert_user('0', 'Jack', '123123')
        with self.assertRaises(exc.IntegrityError):
            self.auction.insert_user('0', 'Tom', '121212')

    def test_insert_user_with_duplicate_info(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.insert_user('1', 'Jack', '123123')
        u1 = self.auction.query_user('0')
        u2 = self.auction.query_user('1')
        self.assertNotEqual(u1.id, u2.id)
        self.assertEqual(u1.name, u2.name)
        self.assertEqual(u1.password, u2.password)

    def tearDown(self):
        os.remove('auction.db')


class TestItem(unittest.TestCase):

    def setUp(self):
        self.auction = Auction()
        self.auction.create_table()

    def test_post_empty_item(self):
        #with self.assertRaises(TypeError):
            self.auction.post_item('0', '0')

    def test_post_item_without_seller(self):
        with self.assertRaises(TypeError):
            self.auction.post_item('0', 'iphoneX', 'The latest iphone')

    def test_post_item_with_invalid_seller(self):
        with self.assertRaises(orm.exc.NoResultFound):
            self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')

    def test_successfully_post_item(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')
        item = self.auction.query_item('0')
        self.assertEqual(item.id, 0)
        self.assertEqual(item.seller_id, 0)
        self.assertEqual(item.name, 'iphoneX')
        self.assertEqual(item.desc, 'The latest iphone')

    def test_access_seller_info(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')
        item = self.auction.query_item('0')
        with self.assertRaises(orm.exc.DetachedInstanceError):
            self.assertEqual(item.seller.id, 0)

    def test_post_duplicate_item(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')
        with self.assertRaises(exc.IntegrityError):
            self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')

    def test_post_item_with_duplicate_id(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.insert_user('1', 'Tom', '121212')
        self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')
        with self.assertRaises(exc.IntegrityError):
            self.auction.post_item('1', '0', 'Macbook', 'A good laptop')

    def test_post_item_with_duplicate_info(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.insert_user('1', 'Tom', '121212')
        self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')
        self.auction.post_item('1', '1', 'iphoneX', 'The latest iphone')
        i1 = self.auction.query_item('0')
        i2 = self.auction.query_item('1')
        self.assertNotEqual(i1.id, i2.id)
        self.assertEqual(i1.name, i2.name)
        self.assertEqual(i1.desc, i2.desc)

    def test_post_item_with_same_seller(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.post_item('0', '0', 'iphoneX', 'The latest iphone')
        self.auction.post_item('0', '1', 'Macbook', 'A good laptop')
        i1 = self.auction.query_item('0')
        i2 = self.auction.query_item('1')
        self.assertNotEqual(i1.id, i2.id)
        self.assertEqual(i1.seller_id, i2.seller_id)

    def tearDown(self):
        os.remove('auction.db')


class TestBid(unittest.TestCase):

    def setUp(self):
        self.auction = Auction()
        self.auction.create_table()

    def insert_pre_info(self):
        self.auction.insert_user('0', 'Jack', '123123')
        self.auction.insert_user('1', 'Tom', '121212')
        self.auction.post_item('1', '0', 'iphoneX', 'The latest iphone')
        self.auction.post_item('1', '1', 'Macbook', 'A good laptop')

    def test_make_empty_bid(self):
        with self.assertRaises(TypeError):
            self.auction.perform_bid()

    def test_make_bid_without_price(self):
        self.insert_pre_info()
        with self.assertRaises(TypeError):
            self.auction.perform_bid('0', '0', '0')

    def test_make_bid_with_invalid_item(self):
        self.insert_pre_info()
        with self.assertRaises(orm.exc.NoResultFound):
            self.auction.perform_bid('0', '0', '2', '100')

    def test_make_bid_with_invalid_user(self):
        self.insert_pre_info()
        with self.assertRaises(orm.exc.NoResultFound):
            self.auction.perform_bid('0', '2', '0', '100')

    def test_successfully_make_bid(self):
        self.insert_pre_info()
        self.auction.perform_bid('0', '0', '0', '100')
        self.auction.perform_bid('1', '0', '1', '300')

    def test_make_duplicate_bid(self):
        self.insert_pre_info()
        self.auction.perform_bid('0', '0', '0', '100')
        with self.assertRaises(exc.IntegrityError):
            self.auction.perform_bid('0', '0', '0', '100')

    def test_make_bid_with_duplicate_id(self):
        self.insert_pre_info()
        self.auction.perform_bid('0', '0', '0', '100')
        with self.assertRaises(exc.IntegrityError):
            self.auction.perform_bid('0', '0', '1', '300')

    def test_make_bid_with_duplicate_info(self):
        self.insert_pre_info()
        self.auction.perform_bid('0', '0', '0', '100')
        self.auction.perform_bid('1', '0', '1', '300')

    def tearDown(self):
        os.remove('auction.db')


if __name__ == '__main__':
    unittest.main()
