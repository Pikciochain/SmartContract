"""
This modules contains objects manipulating contracts to generate ABIs.
ABIs let encode calls in bytecode to be transported on the network.
"""
import json
import base64
import pickle

from Crypto.Hash import SHA3_256

from pikciosc.models import ContractInterface


class ABI(object):
    """Digests Smart Contract to offer calls encoding features."""

    _KECCAK_LEN = 8  # Keccak length used to identify an endpoint signature.

    def __init__(self, contract_interface=None):
        """Creates an ABI used to encode calls to provided contract interface.

        :param contract_interface: The contract interface to use to encode
            or decode calls.
        """
        self._interface = contract_interface or ContractInterface()
        self._selectors_map = self._make_endpoint_encoding_map(self._interface)

    @classmethod
    def from_string_interface(cls, json_string):
        """Creates a new ABI from provided JSON interface.

        :param json_string: the JSON interface. Must be valid.
        :type json_string: str
        :return: An ABI for the specified contract.
        :rtype: ABI
        """
        json_dct = json.loads(json_string)
        interface = ContractInterface.from_dict(json_dct)
        return cls(interface)

    @classmethod
    def from_file_interface(cls, file_path):
        """Creates a new ABI from provided JSON interface file.

        :param file_path: Path to the JSON interface. Must be valid.
        :return: An ABI for the specified contract.
        :rtype: ABI
        """
        with open(file_path) as fd:
            json_dct = json.load(fd)
            interface = ContractInterface.from_dict(json_dct)
            return cls(interface)

    @property
    def endpoints(self):
        """Gets the list of endpoint names supported by this ABI."""
        return self._interface.endpoints_names

    def encode_call(self, endpoint_name, kwargs):
        """Encodes a call to specified endpoint.

        :param endpoint_name: Name of endpoint to call within contract.
        :type endpoint_name: str
        :param kwargs: Dictionary of arguments names and values to provide.
        :type kwargs: dict[str,any]
        :return: The encoded call.
        :rtype: str
        """
        return base64.encodebytes(
            self._encode_endpoint(endpoint_name) +
            self._encode_arguments(kwargs)
        ).decode('utf-8')

    def decode_call(self, encoded_call):
        """Decodes a call.

        :param encoded_call: The bytes composing the call (endpoint and
            arguments.)
        :type encoded_call: str
        :return: A tuple endpoint_name, arguments for the call.
        :rtype: tuple[str,dict]
        """
        byts = base64.decodebytes(encoded_call.encode())
        return (
            self._decode_endpoint(byts[:self._KECCAK_LEN]),
            self._decode_arguments(byts[self._KECCAK_LEN:])
        )

    def _decode_endpoint(self, endpoint_selector):
        """Decodes provided endpoint selector to find its name counterpart.

        :param endpoint_selector: Encoded endpoint signature.
        :type endpoint_selector: bytes
        :return: The name of the endpoint, if that endpoint exists.
        :rtype: str
        """
        if endpoint_selector not in self._selectors_map:
            raise KeyError(f"Selector '{str(endpoint_selector)}' is "
                           f"invalid for contract '{self._interface.name}'")
        return self._selectors_map[endpoint_selector]

    def _encode_endpoint(self, endpoint_name):
        """Encodes an endpoint signature from its name.

        :param endpoint_name: The name of the endpoint to encode.
        :type: endpoint_name: str
        :return: The encoded selector for the endpoint.
        :rtype: bytes
        """
        if endpoint_name not in self._selectors_map:
            raise KeyError(f"Endpoint '{endpoint_name}' is "
                           f"invalid for contract '{self._interface.name}'")
        return self._selectors_map[endpoint_name]

    @staticmethod
    def _encode_arguments(kwargs):
        """Encodes provided named arguments.

        :param kwargs: Dictionary of arguments names and values to provide.
        :type kwargs: dict[str,any]
        :return: The encoded arguments.
        :rtype: bytes
        """
        return pickle.dumps(kwargs)

    @staticmethod
    def _decode_arguments(encoded_kwargs):
        """Decodes provided named arguments.

        :param encoded_kwargs: Encoded arguments.
        :type encoded_kwargs: bytes
        :returns: Dictionary of decoded arguments names and values.
        :rtype: dict[str,any]
        """
        return pickle.loads(encoded_kwargs)

    @staticmethod
    def encode_call_result(call_result):
        """Encodes provided named arguments.

        :param call_result: object detailing execution of a call.
        :type call_result: CallInfo
        :return: The encoded call result.
        :rtype: str
        """
        return base64.encodebytes(pickle.dumps(call_result)).decode('utf-8')

    @staticmethod
    def decode_call_result(encoded_call_result):
        """Decodes provided named arguments.

        :param encoded_call_result: Encoded call result.
        :type encoded_call_result: str
        :returns: object detailing execution of a call.
        :rtype: CallInfo
        """
        return pickle.loads(base64.decodebytes(encoded_call_result.encode()))

    def _do_encode_endpoint(self, endpoint_name):
        """Performs the actual encoding of an endpoint.

        Encoding is obtained by hashing the canonical for of the endpoint.

        :param endpoint_name: Name of endpoint to compute encoding for.
        :type endpoint_name: str
        :return: The encoded selector for the endpoint.
        :rtype: bytes
        """
        signature = self._interface.get_canonical_signature(endpoint_name)
        return SHA3_256.new(signature.encode()).digest()[:self._KECCAK_LEN]

    def _make_endpoint_encoding_map(self, contract_interface):
        """Builds a dictionary mapping endpoint names to selectors and vice
        versa.

        :param contract_interface: Contract interface to rely on.
        :type contract_interface: ContractInterface
        :return: A dictionary mapping endpoint names to selectors and vice
            versa.
        :rtype: dict[byte|str,str|bytes]
        """
        selector_to_ep = {
            self._do_encode_endpoint(ep.name): ep.name
            for ep in contract_interface.endpoints
        }
        ep_to_selector = {
            value: key
            for key, value in selector_to_ep.items()
        }
        return dict(selector_to_ep, **ep_to_selector)
