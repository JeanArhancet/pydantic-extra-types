from re import Pattern
from typing import Any, Optional

import pytest
from pydantic import BaseModel, ValidationError

from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude


class Coord(BaseModel):
    coord: Coordinate


class Lat(BaseModel):
    lat: Latitude


class Lng(BaseModel):
    lng: Longitude


@pytest.mark.parametrize(
    'coord, result, error',
    [
        # Valid coordinates
        # ((20.0, 10.0), (20.0, 10.0), None),
        # ((-90.0, 0.0), (-90.0, 0.0), None),
        # (('20.0', 10.0), (20.0, 10.0), None),
        # ((20.0, '10.0'), (20.0, 10.0), None),
        ((45.678, -123.456), (45.678, -123.456), None),
        (('45.678, -123.456'), (45.678, -123.456), None),
        # (Coordinate((20.0, 10.0)), (20.0, 10.0), None),
        # # Invalid coordinates
        # ((), None, 'Field required'),  # Empty tuple
        # ((10.0,), None, 'Field required'),  # Tuple with only one value
        # (('ten, '), None, 'string is not recognized as a valid coordinate'),
        # ((20.0, 10.0, 30.0), None, 'Tuple should have at most 2 items'),  # Tuple with more than 2 values
        # ('20.0, 10.0, 30.0', None, 'Tuple should have at most 2 items'),  # Str with more than 2 values
        # (2, None, 'Input should be a dictionary or an instance of Coordinate'),  # Wrong type
    ],
)
def test_format_for_coordinate(coord: (Any, Any), result: (float, float), error: Optional[Pattern]):
    if error is None:
        _coord: Coordinate = Coord(coord=coord).coord
        print('vars(_coord)', vars(_coord))
        assert _coord.latitude == result[0]
        assert _coord.longitude == result[1]
    else:
        with pytest.raises(ValidationError, match=error):
            Coordinate(coord)


@pytest.mark.parametrize(
    'coord, error',
    [
        # Valid coordinates
        ((-90.0, 0.0), None),
        ((50.0, 180.0), None),
        # Invalid coordinates
        ((-91.0, 0.0), 'Input should be greater than or equal to -90'),
        ((50.0, 181.0), 'Input should be less than or equal to 180'),
    ],
)
def test_limit_for_coordinate(coord: (Any, Any), error: Optional[Pattern]):
    if error is None:
        _coord: Coordinate = Coord(coord=coord).coord
        assert _coord.latitude == coord[0]
        assert _coord.longitude == coord[1]
    else:
        with pytest.raises(ValidationError, match=error):
            Coordinate(coord)


@pytest.mark.parametrize(
    'latitude, valid',
    [
        # Valid latitude
        (20.0, True),
        (3.0000000000000000000000, True),
        (90.0, True),
        ('90.0', True),
        (-90.0, True),
        ('-90.0', True),
        # Unvalid latitude
        (91.0, False),
        (-91.0, False),
    ],
)
def test_format_latitude(latitude: float, valid: bool):
    if valid:
        _lat = Lat(lat=latitude).lat
        assert _lat == float(latitude)
    else:
        with pytest.raises(ValidationError, match='1 validation error for Lat'):
            Lat(lat=latitude)


@pytest.mark.parametrize(
    'longitude, valid',
    [
        # Valid latitude
        (20.0, True),
        (3.0000000000000000000000, True),
        (90.0, True),
        ('90.0', True),
        (-90.0, True),
        ('-90.0', True),
        (91.0, True),
        (-91.0, True),
        (180.0, True),
        (-180.0, True),
        # Unvalid latitude
        (181.0, False),
        (-181.0, False),
    ],
)
def test_format_longitude(longitude: float, valid: bool):
    if valid:
        _lng = Lng(lng=longitude).lng
        assert _lng == float(longitude)
    else:
        with pytest.raises(ValidationError, match='1 validation error for Lng'):
            Lng(lng=longitude)


def test_str_repr():
    assert str(Coordinate('20.0,10.0')) == '20.0,10.0'
    assert str(Coordinate((20.0, 10.0))) == '20.0,10.0'
    assert repr(Coordinate((20.0, 10.0))) == 'Coordinate(latitude=20.0, longitude=10.0)'


def test_eq():
    assert Coordinate('20.0,10.0') == Coordinate((20.0, 10.0))
    assert Coordinate('20.0,10.0') != Coordinate('20.0,11.0')


def test_color_hashable():
    assert hash(Coordinate((20.0, 10.0))) == hash(Coordinate((20.0, 10.0)))
    assert hash(Coordinate((20.0, 11.0))) != hash(Coordinate((20.0, 10.0)))
