from typing import List
from datetime import datetime, timedelta
from sqlalchemy import and_

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Returns a list of contacts for the user.

    :param skip: int: Skip the first n records
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the user_id from the user model
    :param db: Session: Access the database
    :return: A list of contacts
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Returns a contact from the database.
        Args:
            contact_id (int): The id of the contact to be returned.
            user (User): The user who owns the requested Contact object.
            db (Session): A database session for querying and updating data in a relational database.

    :param contact_id: int: Get the contact with that id
    :param user: User: Get the user_id of the contact
    :param db: Session: Access the database
    :return: A contact object
    """
    return db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()


async def get_contacts_by_info(contact_info: str, user: User, db: Session) -> List[User]:
    """
    Takes a string and returns a list of users that have the string in their first name, last name or email.
        Args:
            contact_info (str): The string to search for.
            db (Session): A database session object.
            user (User): An authenticated user object.

    :param contact_info: str: Pass the information that we want to search for
    :param db: Session: Create a connection to the database
    :param user: User: Get the user id from the database
    :return: A list of users with the specified information
    """
    response = []
    info_by_first_name = db.query(Contact).filter(
        and_(Contact.user_id == user.id, func.lower(Contact.first_name).like(f'%{contact_info.lower()}%'))).all()
    if info_by_first_name:
        for n in info_by_first_name:
            response.append(n)
    info_by_last_name = db.query(Contact).filter(
        and_(Contact.user_id == user.id, func.lower(Contact.last_name).like(f'%{contact_info.lower()}%'))).all()
    if info_by_last_name:
        for n in info_by_last_name:
            response.append(n)
    info_by_email = db.query(Contact).filter(
        and_(Contact.user_id == user.id, Contact.email.like(f'%{contact_info}%'))).all()
    if info_by_email:
        for n in info_by_email:
            response.append(n)

    return response


async def get_contacts_by_birthday(user: User, db: Session) -> List[Contact]:
    """
    Returns a list of contacts whose birthday is within the next week.

    :param user: User: Get the user's id, which is used to filter out contacts that belong to other users
    :param db: Session: Pass in the database session
    :return: A list of contacts whose birthday is within the next 7 days
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id,
                                             extract('month', Contact.birthday) == next_week.month,
                                             extract('day', Contact.birthday) <= next_week.day,
                                             extract('day', Contact.birthday) >= today.day,
                                             )).all()

    birthday_contacts = []
    for contact in contacts:
        bday_this_year = contact.birthday.replace(year=today.year)
        if bday_this_year >= today:
            birthday_contacts.append(contact)
    return birthday_contacts


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact in the database.

    :param body: ContactModel: Pass in the json data from the request body
    :param user: User: Get the user_id from the user model
    :param db: Session: Connect to the database
    :return: A contact object
    """
    contact = Contact(first_name=body.first_name, last_name=body.last_name, email=body.email, phone=body.phone,
                      birthday=body.birthday, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    Updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactUpdate): The updated information for the contact.
            user (User): The user who is updating this contact.
        Returns:
            Contact | None: A Contact object if successful, otherwise None.

    :param contact_id: int: Identify which contact to update
    :param body: ContactUpdate: Pass the json data to the function
    :param user: User: Get the user id of the current user
    :param db: Session: Pass the database session to the function
    :return: A contact object, which is a model
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            user (User): The user who owns the contacts list.
            db (Session): A session object for interacting with a SQLAlchemy database engine.
        Returns:
            Contact | None: If successful, returns an instance of Contact; otherwise, returns None.

    :param contact_id: int: Identify the contact to be removed
    :param user: User: Get the user_id from the user object
    :param db: Session: Pass the database session to the function
    :return: A contact object
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

