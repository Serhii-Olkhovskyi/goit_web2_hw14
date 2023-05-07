import unittest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    remove_contact,
    get_contacts_by_info,
    get_contacts_by_birthday,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=3, db=self.user, user=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            first_name="Cristina",
            last_name="Rono",
            email="hfhghgc@gmail.com",
            phone="803123123",
            birthday=date(2005, 2, 3)
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        body = ContactUpdate(
            first_name="Cristina",
            last_name="Rono",
            email="hfhghgc@gmail.com",
            phone="803123123",
            birthday=date(2005, 2, 3)
        )
        contact = ContactModel(
            first_name="Melinda",
            last_name="Rono",
            email="hfhghgc@gmail.com",
            phone="803123123",
            birthday=date(2005, 2, 3)
        )
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(
            first_name="Cristina",
            last_name="Rono",
            email="hfhghgc@gmail.com",
            phone="803123123",
            birthday=date(2005, 2, 3)
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_by_info(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_by_info(contact_info="example@gmail.com", user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_birthday_found(self):
        contacts = [Contact(birthday=date(2000, 3, 15))]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_by_birthday(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_birthday_not_found(self):
        contacts = []
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_by_birthday(user=self.user, db=self.session)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
