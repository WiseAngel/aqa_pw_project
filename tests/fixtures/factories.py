"""
Test data factories using factory_boy and faker.

Provides reproducible test data generation for API pre-conditions.
All hardcoded values are replaced with dynamic generation.
"""

from datetime import datetime, timedelta

import factory
from faker import Faker

fake = Faker()


class UserFactory(factory.Factory):
    """Factory for generating user test data."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda _: fake.user_name())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    is_active = True
    created_at = factory.LazyFunction(datetime.now)


class ClientFactory(factory.Factory):
    """Factory for generating client/customer test data."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyAttribute(lambda _: fake.name())
    email = factory.LazyAttribute(lambda _: fake.email())
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    company = factory.LazyAttribute(lambda _: fake.company())
    notes = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))


class VehicleFactory(factory.Factory):
    """Factory for generating vehicle test data."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    vin = factory.LazyAttribute(lambda _: fake.uuid4()[:17])
    reg_number = factory.LazyAttribute(
        lambda _: (
            f"{fake.random_letter()}{fake.random_int(100, 999)}{fake.random_letter()}{fake.random_letter()} {fake.random_int(100, 999)}"
        )
    )
    brand = factory.LazyAttribute(lambda _: fake.company())
    model = factory.LazyAttribute(lambda _: fake.word())
    year = factory.LazyAttribute(lambda _: fake.random_int(2015, 2026))
    mileage_km = factory.LazyAttribute(lambda _: fake.random_int(0, 200000))
    next_service_date = factory.LazyAttribute(lambda _: datetime.now() + timedelta(days=fake.random_int(30, 365)))


class OrderFactory(factory.Factory):
    """Factory for generating order/service request test data."""

    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n + 1)
    order_number = factory.LazyAttribute(lambda _: f"ORD-{fake.random_int(10000, 99999)}")
    description = factory.LazyAttribute(lambda _: fake.sentence(nb_words=10))
    status = factory.LazyAttribute(lambda _: fake.random_element(["new", "in_progress", "completed", "cancelled"]))
    total_amount = factory.LazyAttribute(lambda _: fake.random_int(1000, 50000))
    created_at = factory.LazyFunction(datetime.now)
