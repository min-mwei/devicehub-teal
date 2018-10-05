import ipaddress
from datetime import datetime, timedelta
from decimal import Decimal
from distutils.version import StrictVersion
from typing import Dict, List, Set, Union
from uuid import UUID

from boltons import urlutils
from boltons.urlutils import URL
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy_utils import Currency
from teal import enums
from teal.db import Model
from teal.enums import Country

from ereuse_devicehub.resources.agent.models import Agent
from ereuse_devicehub.resources.device.models import Component, Computer, Device
from ereuse_devicehub.resources.enums import AppearanceRange, Bios, FunctionalityRange, \
    PriceSoftware, RatingSoftware, ReceiverRole, SnapshotExpectedEvents, SnapshotSoftware, \
    TestHardDriveLength
from ereuse_devicehub.resources.image.models import Image
from ereuse_devicehub.resources.models import Thing
from ereuse_devicehub.resources.user.models import User


class Event(Thing):
    id = ...  # type: Column
    name = ...  # type: Column
    type = ...  # type: Column
    error = ...  # type: Column
    incidence = ...  # type: Column
    description = ...  # type: Column
    finalized = ...  # type: Column
    snapshot_id = ...  # type: Column
    snapshot = ...  # type: relationship
    author_id = ...  # type: Column
    agent = ...  # type: relationship
    components = ...  # type: relationship
    parent_id = ...  # type: Column
    parent = ...  # type: relationship
    closed = ...  # type: Column
    start_time = ...  # type: Column
    end_time = ...  # type: Column
    agent_id = ...  # type: Column

    def __init__(self, id=None, name=None, incidence=None, closed=None, error=None,
                 description=None, start_time=None, end_time=None, snapshot=None, agent=None,
                 parent=None, created=None, updated=None, author=None) -> None:
        super().__init__(created, updated)
        self.id = ...  # type: UUID
        self.name = ...  # type: str
        self.type = ...  # type: str
        self.incidence = ...  # type: bool
        self.closed = ...  # type: bool
        self.error = ...  # type: bool
        self.description = ...  # type: str
        self.start_time = ...  # type: datetime
        self.end_time = ...  # type: datetime
        self.snapshot = ...  # type: Snapshot
        self.components = ...  # type: Set[Component]
        self.parent = ...  # type: Computer
        self.agent = ...  # type: Agent
        self.author = ...  # type: User

    @property
    def url(self) -> urlutils.URL:
        pass

class EventWithOneDevice(Event):

    def __init__(self, id=None, name=None, incidence=None, closed=None, error=None,
                 description=None, start_time=None, end_time=None, snapshot=None, agent=None,
                 parent=None, created=None, updated=None, author=None, device=None) -> None:
        super().__init__(id, name, incidence, closed, error, description, start_time, end_time,
                         snapshot, agent, parent, created, updated, author)
        self.device = ...  # type: Device


class EventWithMultipleDevices(Event):

    def __init__(self, id=None, name=None, incidence=None, closed=None, error=None,
                 description=None, start_time=None, end_time=None, snapshot=None, agent=None,
                 parent=None, created=None, updated=None, author=None, devices=None) -> None:
        super().__init__(id, name, incidence, closed, error, description, start_time, end_time,
                         snapshot, agent, parent, created, updated, author)
        self.devices = ...  # type: Set[Device]


class Add(EventWithOneDevice):
    pass


class Remove(EventWithOneDevice):
    pass


class Step(Model):
    def __init__(self, num=None, success=None, start_time=None, end_time=None,
                 erasure=None, error=None) -> None:
        self.type = ...  # type: str
        self.num = ...  # type: int
        self.success = ...  # type: bool
        self.start_time = ...  # type: datetime
        self.end_time = ...  # type: datetime
        self.erasure = ...  # type: EraseBasic
        self.error = ...  # type: bool


class StepZero(Step):
    pass


class StepRandom(Step):
    pass


class Snapshot(EventWithOneDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.uuid = ...  # type: UUID
        self.version = ...  # type: StrictVersion
        self.software = ...  # type: SnapshotSoftware
        self.elapsed = ...  # type: timedelta
        self.device = ...  # type: Computer
        self.events = ...  # type: Set[Event]
        self.expected_events = ...  # type: List[SnapshotExpectedEvents]


class Install(EventWithOneDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = ...  # type: str
        self.elapsed = ...  # type: timedelta
        self.success = ...  # type: bool


class SnapshotRequest(Model):
    def __init__(self, **kwargs) -> None:
        self.id = ...  # type: UUID
        self.request = ...  # type: dict
        self.snapshot = ...  # type: Snapshot


class Rate(EventWithOneDevice):
    rating = ...  # type: Column
    appearance = ...  # type: Column
    functionality = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rating = ...  # type: float
        self.software = ...  # type: RatingSoftware
        self.version = ...  # type: StrictVersion
        self.appearance = ...  # type: float
        self.functionality = ...  # type: float
        self.rating_range = ...  # type: str


class IndividualRate(Rate):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.aggregated_ratings = ...  # type: Set[AggregateRate]


class AggregateRate(Rate):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ratings = ...  # type: Set[IndividualRate]
        self.price = ...  # type: Price


class ManualRate(IndividualRate):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.labelling = ...  # type: bool
        self.appearance_range = ...  # type: AppearanceRange
        self.functionality_range = ...  # type: FunctionalityRange


class WorkbenchRate(ManualRate):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.processor = ...  # type: float
        self.ram = ...  # type: float
        self.data_storage = ...  # type: float
        self.graphic_card = ...  # type: float
        self.bios = ...  # type: Bios


class AppRate(ManualRate):
    pass


class PhotoboxRate(IndividualRate):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.num = ...  # type: int
        self.image = ...  # type: Image


class PhotoboxUserRate(PhotoboxRate):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.assembling = ...  # type: int
        self.parts = ...  # type: int
        self.buttons = ...  # type: int
        self.dents = ...  # type: int
        self.decolorization = ...  # type: int
        self.scratches = ...  # type: int
        self.tag_adhesive = ...  # type: int
        self.dirt = ...  # type: int


class PhotoboxSystemRate(PhotoboxRate):
    pass


class Price(EventWithOneDevice):
    currency = ...  # type: Column
    price = ...  # type: Column
    software = ...  # type: Column
    version = ...  # type: Column
    rating_id = ...  # type: Column
    rating = ...  # type: relationship

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.price = ...  # type: Decimal
        self.currency = ...  # type: Currency
        self.software = ...  # type: PriceSoftware
        self.version = ...  # type: StrictVersion
        self.rating = ...  # type: AggregateRate


class EreusePrice(Price):
    MULTIPLIER = ...  # type: Dict

    def __init__(self, rating: AggregateRate, **kwargs) -> None:
        super().__init__(**kwargs)


class Test(EventWithOneDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.elapsed = ...  # type: timedelta
        self.success = ...  # type: bool


class TestDataStorage(Test):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.id = ...  # type: UUID
        self.length = ...  # type: TestHardDriveLength
        self.status = ...  # type: str
        self.lifetime = ...  # type: timedelta
        self.first_error = ...  # type: int
        self.passed_lifetime = ...  # type: timedelta
        self.assessment = ...  # type: int
        self.reallocated_sector_count = ...  # type: int
        self.power_cycle_count = ...  # type: int
        self.reported_uncorrectable_errors = ...  # type: int
        self.command_timeout = ...  # type: int
        self.current_pending_sector_count = ...  # type: int
        self.offline_uncorrectable = ...  # type: int
        self.remaining_lifetime_percentage = ...  # type: int


class StressTest(Test):
    pass


class EraseBasic(EventWithOneDevice):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_time = ...  # type: datetime
        self.end_time = ...  # type: datetime
        self.steps = ...  # type: List[Step]
        self.zeros = ...  # type: bool
        self.success = ...  # type: bool


class EraseSectors(EraseBasic):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class Benchmark(EventWithOneDevice):
    pass


class BenchmarkDataStorage(Benchmark):
    read_speed = ...  # type: Column
    write_speed = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.read_speed = ...  # type: float
        self.write_speed = ...  # type: float


class BenchmarkWithRate(Benchmark):
    rate = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.rate = ...  # type: int


class BenchmarkProcessor(BenchmarkWithRate):
    pass


class BenchmarkProcessorSysbench(BenchmarkProcessor):
    pass


class BenchmarkRamSysbench(BenchmarkWithRate):
    pass


class ToRepair(EventWithMultipleDevices):
    pass


class Repair(EventWithMultipleDevices):
    pass


class ReadyToUse(EventWithMultipleDevices):
    pass


class ToPrepare(EventWithMultipleDevices):
    pass


class Prepare(EventWithMultipleDevices):
    pass


class Live(EventWithOneDevice):
    ip = ...  # type: Column
    subdivision_confidence = ...  # type: Column
    subdivision = ...  # type: Column
    city = ...  # type: Column
    city_confidence = ...  # type: Column
    isp = ...  # type: Column
    organization = ...  # type: Column
    organization_type = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ip = ...  # type: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
        self.subdivision_confidence = ...  # type: int
        self.subdivision = ...  # type: enums.Subdivision
        self.city = ...  # type: str
        self.city_confidence = ...  # type: int
        self.isp = ...  # type: str
        self.organization = ...  # type: str
        self.organization_type = ...  # type: str
        self.country = ...  # type: Country


class Organize(EventWithMultipleDevices):
    pass


class Reserve(Organize):
    pass


class Trade(EventWithMultipleDevices):
    shipping_date = ...  # type: Column
    invoice_number = ...  # type: Column
    price = ...  # type: relationship
    to = ...  # type: relationship
    confirms = ...  # type: relationship

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shipping_date = ...  # type: datetime
        self.invoice_number = ...  # type: str
        self.price = ...  # type: Price
        self.to = ...  # type: Agent
        self.confirms = ...  # type: Organize


class Sell(Trade):
    pass


class Donate(Trade):
    pass


class Rent(Trade):
    pass


class CancelTrade(Trade):
    pass


class ToDisposeProduct(Trade):
    pass


class DisposeProduct(Trade):
    pass


class Receive(EventWithMultipleDevices):
    role = ...  # type:Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.role = ...  # type: ReceiverRole


class Migrate(EventWithMultipleDevices):
    other = ...  # type: Column

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.other = ...  # type: URL


class MigrateTo(Migrate):
    pass


class MigrateFrom(Migrate):
    pass
