from datetime import date, datetime, timedelta
from datetime import timezone as tz

import pendulum
import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from pydantic_extra_types.pendulum_dt import Date, DateTime, Duration

UTC = tz.utc


class DtModel(BaseModel):
    dt: DateTime


class DateModel(BaseModel):
    d: Date


class DurationModel(BaseModel):
    delta_t: Duration


@pytest.mark.parametrize(
    'instance',
    [
        pendulum.now(),
        datetime.now(),
        datetime.now(UTC),
    ],
)
def test_existing_instance(instance):
    """
    Verifies that constructing a model with an existing pendulum dt doesn't throw.
    """
    model = DtModel(dt=instance)
    if isinstance(instance, datetime):
        assert model.dt == pendulum.instance(instance)
        if instance.tzinfo is None and isinstance(instance, datetime):
            instance = model.dt.replace(tzinfo=UTC)  # pendulum defaults to UTC
        dt = model.dt
    else:
        assert model.dt == instance
        dt = model.dt

    assert dt.day == instance.day
    assert dt.month == instance.month
    assert dt.year == instance.year
    assert dt.hour == instance.hour
    assert dt.minute == instance.minute
    assert dt.second == instance.second
    assert dt.microsecond == instance.microsecond
    assert isinstance(dt, pendulum.DateTime)
    assert type(dt) is DateTime
    if dt.tzinfo != instance.tzinfo:
        assert dt.tzinfo.utcoffset(dt) == instance.tzinfo.utcoffset(instance)


@pytest.mark.parametrize(
    'instance',
    [
        pendulum.today(),
        date.today(),
    ],
)
def test_pendulum_date_existing_instance(instance):
    """
    Verifies that constructing a model with an existing pendulum date doesn't throw.
    """
    model = DateModel(d=instance)
    if isinstance(instance, datetime):
        assert model.d == pendulum.instance(instance).date()
    else:
        assert model.d == instance
    d = model.d
    assert d.day == instance.day
    assert d.month == instance.month
    assert d.year == instance.year
    assert isinstance(d, pendulum.Date)
    assert type(d) is Date


@pytest.mark.parametrize(
    'instance',
    [
        pendulum.duration(days=42, hours=13, minutes=37),
        pendulum.duration(days=-42, hours=13, minutes=37),
        timedelta(days=42, hours=13, minutes=37),
        timedelta(days=-42, hours=13, minutes=37),
    ],
)
def test_duration_timedelta__existing_instance(instance):
    """
    Verifies that constructing a model with an existing pendulum duration doesn't throw.
    """
    model = DurationModel(delta_t=instance)

    assert model.delta_t.total_seconds() == instance.total_seconds()
    assert isinstance(model.delta_t, pendulum.Duration)
    assert model.delta_t


@pytest.mark.parametrize(
    'dt',
    [
        pendulum.now().to_iso8601_string(),
        pendulum.now().to_w3c_string(),
    ],
)
def test_pendulum_dt_from_serialized(dt):
    """
    Verifies that building an instance from serialized, well-formed strings decode properly.
    """
    dt_actual = pendulum.parse(dt)
    model = DtModel(dt=dt)
    assert model.dt == dt_actual
    assert type(model.dt) is DateTime
    assert isinstance(model.dt, pendulum.DateTime)


@pytest.mark.parametrize(
    'd',
    [pendulum.now().date().isoformat(), pendulum.now().to_w3c_string(), pendulum.now().to_iso8601_string()],
)
def test_pendulum_date_from_serialized(d):
    """
    Verifies that building an instance from serialized, well-formed strings decode properly.
    """
    date_actual = pendulum.parse(d).date()
    model = DateModel(d=d)
    assert model.d == date_actual
    assert type(model.d) is Date
    assert isinstance(model.d, pendulum.Date)


@pytest.mark.parametrize(
    'delta_t_str',
    [
        'P3.14D',
        'PT404H',
        'P1DT25H',
        'P2W',
        'P10Y10M10D',
    ],
)
def test_pendulum_duration_from_serialized(delta_t_str):
    """
    Verifies that building an instance from serialized, well-formed strings decode properly.
    """
    true_delta_t = pendulum.parse(delta_t_str)
    model = DurationModel(delta_t=delta_t_str)
    assert model.delta_t == true_delta_t
    assert type(model.delta_t) is Duration
    assert isinstance(model.delta_t, pendulum.Duration)


@pytest.mark.parametrize('dt', [None, 'malformed', pendulum.now().to_iso8601_string()[:5], 42, 'P10Y10M10D'])
def test_pendulum_dt_malformed(dt):
    """
    Verifies that the instance fails to validate if malformed dt are passed.
    """
    with pytest.raises(ValidationError):
        DtModel(dt=dt)


@pytest.mark.parametrize('date', [None, 'malformed', pendulum.today().to_iso8601_string()[:5], 42, 'P10Y10M10D'])
def test_pendulum_date_malformed(date):
    """
    Verifies that the instance fails to validate if malformed date are passed.
    """
    with pytest.raises(ValidationError):
        DateModel(d=date)


@pytest.mark.parametrize(
    'delta_t',
    [None, 'malformed', pendulum.today().to_iso8601_string()[:5], 42, '12m', '2021-01-01T12:00:00'],
)
def test_pendulum_duration_malformed(delta_t):
    """
    Verifies that the instance fails to validate if malformed durations are passed.
    """
    with pytest.raises(ValidationError):
        DurationModel(delta_t=delta_t)


@pytest.mark.parametrize(
    'input_type, value, is_instance',
    [
        (Date, '2021-01-01', pendulum.Date),
        (Date, date(2021, 1, 1), pendulum.Date),
        (Date, pendulum.date(2021, 1, 1), pendulum.Date),
        (DateTime, '2021-01-01T12:00:00', pendulum.DateTime),
        (DateTime, datetime(2021, 1, 1, 12, 0, 0), pendulum.DateTime),
        (DateTime, pendulum.datetime(2021, 1, 1, 12, 0, 0), pendulum.DateTime),
        (Duration, 'P1DT25H', pendulum.Duration),
        (Duration, timedelta(days=1, hours=25), pendulum.Duration),
        (Duration, pendulum.duration(days=1, hours=25), pendulum.Duration),
    ],
)
def test_date_type_adapter(input_type: type, value, is_instance: type):
    validated = TypeAdapter(input_type).validate_python(value)
    assert type(validated) is input_type
    assert isinstance(validated, input_type)
    assert isinstance(validated, is_instance)
