from __future__ import annotations

from typing import Any, ClassVar, Union

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, dataclasses
from pydantic._internal import _repr
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import ArgsKwargs, PydanticCustomError, core_schema
from typing_extensions import Self

CoordinateValueType = Union[str, int, float]


class Latitude(float):
    min: ClassVar[float] = -90.00
    max: ClassVar[float] = 90.00

    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[Any], handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.float_schema(ge=cls.min, le=cls.max)


class Longitude(float):
    min: ClassVar[float] = -180.00
    max: ClassVar[float] = 180.00

    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[Any], handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.float_schema(ge=cls.min, le=cls.max)


@dataclasses.dataclass
class Coordinate(_repr.Representation):
    _NULL_ISLAND: ClassVar[tuple[float, float]] = 0.0, 0.0

    latitude: Latitude
    longitude: Longitude

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        field_schema: dict[str, Any] = handler(core_schema)
        field_schema.update(format='coordinate')
        return field_schema

    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[Any], handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        float_schema = core_schema.float_schema()
        result = core_schema.no_info_before_validator_function(
            cls._parse_args,
            core_schema.union_schema(
                [
                    core_schema.no_info_after_validator_function(cls._debug_handler, handler(source)),
                    core_schema.no_info_after_validator_function(
                        cls._parse_tuple,
                        core_schema.tuple_positional_schema([float_schema, float_schema]),
                    ),
                    core_schema.no_info_after_validator_function(cls._parse_str, core_schema.str_schema()),
                ]
            ),
        )
        print('schema', result)
        return result

    @classmethod
    def _debug_handler(cls, value: Any) -> Any:
        print('handler', value)
        return value

    @classmethod
    def _parse_args(cls, value: Any) -> Any:
        print('maybe args', value)
        if not isinstance(value, ArgsKwargs):
            return value

        args, kwargs = value.args, value.kwargs

        if kwargs:
            print('kwargs', {k: (v, type(v)) for k, v in kwargs.items()})
            return kwargs
        if not args:
            return cls._NULL_ISLAND
        if len(args) == 1:
            print('args[0]', args[0], type(args[0]))
            return args[0]
        print('args', args)
        return args

    @classmethod
    def _parse_tuple(cls, value: tuple[float, float]) -> Self:
        print('tup', value)
        return cls(latitude=value[0], longitude=value[1])  # type: ignore

    @classmethod
    def _parse_str(cls, value: str) -> Self:
        print('str', value)
        try:
            _coords = [float(x) for x in value.split(',')]
        except ValueError:
            raise PydanticCustomError(
                'coordinate_error', 'value is not a valid coordinate: string is not recognized as a valid coordinate'
            )

        return cls(*_coords)  # type: ignore

    def __str__(self) -> str:
        return f'{self.latitude},{self.longitude}'

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Coordinate) and self.latitude == other.latitude and self.longitude == other.longitude

    def __hash__(self) -> int:
        return hash((self.latitude, self.longitude))
