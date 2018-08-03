"""Contains model objects being used as input/output of modules endpoints.
"""
import os
import json
import pydoc

from datetime import datetime


class _JSONFileSerializable(object):
    """Base class providing serialisation to file features."""

    def to_file(self, path):
        """Saves this object as JSON at provided path. If file already exists,
        it is erased.

        :param path: Destination file path. Intermediate folders are created if
            necessary.
        :type path: str
        """
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(path, 'w') as fd:
            json.dump(self.to_dict(), fd)

    @classmethod
    def from_file(cls, path):
        """Creates and returns an object from provided JSON file if that file
        exists.

        :param path: Path to the file.
        :type path: str
        :return: The created object or None if the file does not exist.
        :type: cls|None
        """
        if not os.path.exists(path):
            return None

        with open(path) as fd:
            return cls.from_dict(json.load(fd))

    def to_dict(self):
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, path):
        raise NotImplementedError()


class TypedNamed(object):
    """Stands for an object that has a name and a type."""

    def __init__(self, name, typ):
        """Creates a new TypedNamed from provided arguments.

        :param name: The object name.
        :type name: str
        :param typ: The object type
        :type typ: Union[type|str]
        """
        self.name = name
        self.type = pydoc.locate(typ) if isinstance(typ, str) else typ

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        type_str = self.type.__name__ if self.type else str(None)
        return {'name': self.name, 'type': type_str}

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        return cls(json_dct['name'], json_dct['type'])


class Variable(TypedNamed):
    """Stands for an object that has a name and a typed value."""

    def __init__(self, name, typ, value):
        """Creates a new TypedValue from provided arguments.

        :param name: The object name.
        :type name: str
        :param typ: The object type
        :type typ: Union[type|str]
        :param value: The value which must match provided type.
        """
        super().__init__(name, typ)
        self.value = value

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        return dict(super().to_dict(), **{'value': self.value})

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        return cls(json_dct['name'], json_dct['type'], json_dct['value'])


class EndPointDef(TypedNamed):
    """Stands for the definition of and enpoint in a Smart Contract."""

    def __init__(self, name, typ, params=None, doc=None):
        """Creates a new EndPointDef from provided arguments.

        :param name: The object name.
        :type name: str
        :param typ: The object type
        :type typ: Union[type|str]
        :param params: The list of named parameters accepted by the endpoint.
        :type params: list[TypedNamed]
        :param doc: Optional documentation string for the endpoint.
        :type doc: str
        """
        super().__init__(name, typ)
        self.params = params
        self.doc = doc

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        params = [arg.to_dict() for arg in self.params]
        return dict(super().to_dict(), **{'params': params, 'doc': self.doc})

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        return cls(
            json_dct['name'],
            json_dct['type'],
            [TypedNamed.from_dict(arg) for arg in json_dct.get('params', [])],
            json_dct['doc'],
        )


class ContractInterface(_JSONFileSerializable):
    """Stands for the resulting interface obtained after parsing a Smart
    Contract.
    """

    def __init__(self, name=None, storage_vars=None, endpoints=None):
        """Creates a new ContractInterface from its specifications.

        :param name: The name of the contract.
        :type name: str
        :param storage_vars: The list of variables that must be saved and
            restored between calls. The value of the variable is the initial
            value.
        :type storage_vars: list[Variable]
        :param endpoints: The list of endpoints that can be called directly by
            an user.
        :type endpoints: list[EndpointDef]
        """
        self.name = name or 'unnamed'
        self.storage_vars = storage_vars or []
        self.endpoints = endpoints or []

    @property
    def endpoints_names(self):
        """Gets a list of names of the endpoints in this contract."""
        return tuple(ep.name for ep in self.endpoints)

    def get_endpoint(self, endpoint_name):
        matches = list(ep for ep in self.endpoints if ep.name == endpoint_name)
        return None if not matches else matches[0]

    def get_canonical_signature(self, endpoint_name):
        """Obtains the canonical signature of an endpoint.

        :param endpoint_name: Name of the endpoint which canonical form is
            requested.
        :type endpoint_name: str
        :return: The canonical signature of that endpoint.
        :rtype: str
        """
        ep = self.get_endpoint(endpoint_name)
        params_part = ','.join(param.type.__name__ for param in ep.params)
        return f'{endpoint_name}({params_part})'

    def is_supported_endpoint(self, endpoint_name):
        """Tells if provided endpoint name is supported by this contract.

        :param endpoint_name: Name of endpoint to test.
        :type endpoint_name: str
        :rtype: bool
        """
        return any(ep.name == endpoint_name for ep in self.endpoints)

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        return {
            'name': self.name,
            'storage': [var.to_dict() for var in self.storage_vars],
            'endpoints': [endpoint.to_dict() for endpoint in self.endpoints]
        }

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        return cls(
            json_dct['name'],
            [Variable.from_dict(var) for var in json_dct.get('storage', [])],
            [EndPointDef.from_dict(ep) for ep in json_dct.get('endpoints', [])]
        )


class StopWatch(object):
    """Contains time measures about an event"""

    def __init__(self, start=None, end=None):
        """Creates a new StopWatch with already recorded measures.

        :param start: Beginning of the event, as a timestamp.
        :type start: float
        :param end: End of the event, as a timestamp
        :type end: float
        """
        self.start = start
        self.end = end

    def set_start(self, timestamp=None):
        """Defines the beginning of the event to now or to a specified time.
        Also resets end time to None.

        :param timestamp: If specified, the beginning of the event.
        :type timestamp: float
        """
        self.start = timestamp or datetime.utcnow().timestamp()
        self.end = None

    def set_end(self, timestamp=None):
        """Defines the end of the event to now or to a specified time.

        :param timestamp: If specified, the end of the event.
        :type timestamp: float
        """
        self.end = timestamp or datetime.utcnow().timestamp()

    @property
    def duration(self):
        """The total duration, if both bounds have been set. NaN otherwise."""
        return (
            float('nan') if not self.end or not self.start else
            self.end - self.start
        )

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        return {
            "start": self.start, "end": self.end, "duration": self.duration,
        }

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        return cls(json_dct['start'], json_dct['end'])


class SuccessInfo(object):
    """Contains details about the completion state of an event."""

    def __init__(self, error=None):
        """Creates a new SuccessInfo. If an error is provided, the state is
        considered unsuccessful.

        :param error: Optional error to provide in case operation wasn't
            successful.
        :type error: str
        """
        self.error = error

    @property
    def is_success(self):
        """Tells if event completed successfully."""
        return self.error is None

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        return {"is_success": self.is_success, "error": self.error}

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        return cls(json_dct['error'])


class CallInfo(object):
    """Contains details about a call made to an endpoint."""

    def __init__(self, endpoint_name, kwargs, stop_watch=None,
                 success_info=None, ret_val=None):
        """Creates a new CallInfo from provided details.

        :param endpoint_name: The name of the endpoint called.
        :type endpoint_name: str
        :param kwargs: The list of named arguments provided.
        :type kwargs: list[Variable]
        :param stop_watch: Call time measurement.
        :type stop_watch: StopWatch
        :param success_info: Details about call completion.
        :type success_info: SuccessInfo
        :param ret_val: The value returned by the call, if any.
        """
        self.stop_watch = stop_watch or StopWatch()
        self.success_info = success_info or SuccessInfo()
        self.endpoint_name = endpoint_name
        self.kwargs = kwargs
        self.ret_val = ret_val

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        return dict(
            {
                "endpoint": self.endpoint_name,
                "args": [var.to_dict() for var in self.kwargs],
                "ret_val": self.ret_val,
            },
            **self.success_info.to_dict(),
            **self.stop_watch.to_dict(),
        )

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        if json_dct is None:
            return None
        return cls(
            json_dct['endpoint'],
            [Variable.from_dict(var) for var in json_dct['args']],
            StopWatch.from_dict(json_dct),
            SuccessInfo.from_dict(json_dct),
            json_dct['ret_val']
        )


class ExecutionInfo(_JSONFileSerializable):
    """Contains broader details about an endpoint invocation."""

    def __init__(self, storage_before, call_info=None, stop_watch=None,
                 success_info=None, storage_after=None):
        """Creates a new ExecutionInfo from specified parameters.

        :param storage_before: State of storage variables before call.
        :type storage_before: list[Variable]
        :param call_info: Details about the core call.
        :type call_info: CallInfo
        :param stop_watch: Execution time measurement.
        :type stop_watch: StopWatch
        :param success_info: Details about execution completion.
        :type success_info: SuccessInfo
        :param storage_after: State of storage variables after call.
        :type storage_after: list[Variable]
        """
        super().__init__()
        self.call_info = call_info or None
        self.stop_watch = stop_watch or StopWatch()
        self.success_info = success_info or SuccessInfo()
        self.storage_before = storage_before
        self.storage_after = storage_after or storage_before

    def to_dict(self):
        """Gets a dictionary standing for this object.

        :rtype: dict
        """
        return dict(
            {
                "call": self.call_info.to_dict() if self.call_info else None,
                "storage": {
                    "before": [var.to_dict() for var in self.storage_before],
                    "after": [var.to_dict() for var in self.storage_after]
                }
            },
            **self.success_info.to_dict(),
            **self.stop_watch.to_dict(),
        )

    @classmethod
    def from_dict(cls, json_dct):
        """Creates a new object from its dictionary representation.

        :param json_dct: Dictionary that must contain each attribute.
        :type json_dct: dict
        """
        return cls(
            [Variable.from_dict(var) for var in json_dct['storage']['before']],
            CallInfo.from_dict(json_dct['call']),
            StopWatch.from_dict(json_dct),
            SuccessInfo.from_dict(json_dct),
            [Variable.from_dict(var) for var in json_dct['storage']['after']]
        )
