import pickle
import hashlib
import unittest

class MyClass:
    """A simple custom class for testing pickle stability."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return isinstance(other, MyClass) and self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash((self.x, self.y))

class MySubClass(MyClass):
    """A subclass of MyClass to test subclass pickling stability."""
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z
    def __eq__(self, other):
        return isinstance(other, MySubClass) and super().__eq__(other) and self.z == other.z
    def __hash__(self):
        return hash((super().__hash__(), self.z))

class GetSetStateClass:
    """Class implementing __getstate__ and __setstate__ for custom pickling behavior."""
    def __init__(self, data):
        self.data = data
    def __getstate__(self):
        return self.data
    def __setstate__(self, state):
        self.data = state

class SlotsClass:
    """Class using __slots__ to restrict attributes, testing pickling of slots."""
    __slots__ = ['a', 'b']
    def __init__(self, a, b):
        self.a = a
        self.b = b

def module_level_func(x):
    """A simple module-level function for testing function pickling."""
    return x * 2

class TestPickleStability(unittest.TestCase):
    """Test suite to verify pickle serialization stability and consistency."""

    def hash_pickle(self, obj, protocol=None):
        """
        Helper method to pickle an object and return the SHA-256 hash of the serialized bytes.
        This is used to verify that repeated serialization produces identical output.
        """
        if protocol is None:
            data = pickle.dumps(obj)
        else:
            data = pickle.dumps(obj, protocol=protocol)
        return hashlib.sha256(data).hexdigest()

    def round_trip(self, obj, protocol=None):
        """
        Helper method to pickle and then unpickle an object, returning the deserialized object.
        Used to verify round-trip serialization/deserialization behavior.
        """
        if protocol is None:
            data = pickle.dumps(obj)
        else:
            data = pickle.dumps(obj, protocol=protocol)
        return pickle.loads(data)

    def test_basic_types_stability(self):
        """
        Test that basic data types produce hash-identical pickle output on repeated serialization,
        and that round-trip deserialization returns an equivalent object.
        """
        test_values = [
            42,
            3.14159,
            "hello world",
            b"bytes data",
            True,
            None,
            [1, 2, 3, 4],
            (5, 6, 7),
            {"a": 1, "b": 2},
            {1, 2, 3},
            frozenset([4, 5, 6]),
            complex(1, 2),
            range(10)
        ]
        for value in test_values:
            with self.subTest(value=value):
                hash1 = self.hash_pickle(value)
                hash2 = self.hash_pickle(value)
                self.assertEqual(hash1, hash2, f"Pickle output hash differs for value: {value}")
                round_trip_obj = self.round_trip(value)
                self.assertEqual(round_trip_obj, value, f"Round-trip deserialization failed for value: {value}")

    def test_custom_class_stability(self):
        """
        Test that instances of custom classes produce hash-identical pickle output on repeated serialization,
        and that round-trip deserialization returns an equivalent object.
        """
        obj = MyClass(10, "test")
        hash1 = self.hash_pickle(obj)
        hash2 = self.hash_pickle(obj)
        self.assertEqual(hash1, hash2, "Pickle output hash differs for custom class instance")
        round_trip_obj = self.round_trip(obj)
        self.assertEqual(round_trip_obj, obj, "Round-trip deserialization failed for custom class instance")

    def test_subclass_stability(self):
        """
        Test that instances of subclassed custom classes produce hash-identical pickle output on repeated serialization,
        and that round-trip deserialization returns an equivalent object.
        """
        obj = MySubClass(1, 2, 3)
        hash1 = self.hash_pickle(obj)
        hash2 = self.hash_pickle(obj)
        self.assertEqual(hash1, hash2, "Pickle output hash differs for subclass instance")
        round_trip_obj = self.round_trip(obj)
        self.assertEqual(round_trip_obj, obj, "Round-trip deserialization failed for subclass instance")

    def test_getsetstate_class(self):
        """
        Test pickling of class with __getstate__ and __setstate__ methods for custom serialization,
        and verify round-trip deserialization returns an equivalent object.
        """
        obj = GetSetStateClass({"key": "value"})
        hash1 = self.hash_pickle(obj)
        hash2 = self.hash_pickle(obj)
        self.assertEqual(hash1, hash2, "Pickle output hash differs for GetSetStateClass instance")
        round_trip_obj = self.round_trip(obj)
        self.assertEqual(round_trip_obj.data, obj.data, "Round-trip deserialization failed for GetSetStateClass instance")

    def test_slots_class(self):
        """
        Test pickling of class with __slots__ attribute to ensure slot attributes are serialized correctly,
        and verify round-trip deserialization returns an equivalent object.
        """
        obj = SlotsClass(1, 2)
        hash1 = self.hash_pickle(obj)
        hash2 = self.hash_pickle(obj)
        self.assertEqual(hash1, hash2, "Pickle output hash differs for SlotsClass instance")
        round_trip_obj = self.round_trip(obj)
        self.assertEqual((round_trip_obj.a, round_trip_obj.b), (obj.a, obj.b), "Round-trip deserialization failed for SlotsClass instance")

    def test_circular_reference(self):
        """
        Test pickling of objects with circular references to verify pickle handles cycles correctly,
        and verify round-trip deserialization returns an equivalent structure.
        """
        a = []
        b = [a]
        a.append(b)
        hash1 = self.hash_pickle(a)
        hash2 = self.hash_pickle(a)
        self.assertEqual(hash1, hash2, "Pickle output hash differs for circular reference")
        round_trip_obj = self.round_trip(a)
        self.assertEqual(len(round_trip_obj), 1, "Round-trip deserialization failed for circular reference")
        self.assertIs(round_trip_obj[0][0], round_trip_obj, "Round-trip deserialization failed to preserve circular reference")

    def test_exception_pickling(self):
        """
        Test pickling of exception instances to ensure exceptions serialize and deserialize consistently,
        and verify round-trip deserialization returns an equivalent exception.
        """
        exc = ValueError("error message")
        hash1 = self.hash_pickle(exc)
        hash2 = self.hash_pickle(exc)
        self.assertEqual(hash1, hash2, "Pickle output hash differs for exception instance")
        round_trip_obj = self.round_trip(exc)
        self.assertEqual(str(round_trip_obj), str(exc), "Round-trip deserialization failed for exception instance")

    def test_module_level_function(self):
        """
        Test pickling of a module-level function to verify functions defined at module scope are pickled consistently,
        and verify round-trip deserialization returns the same function object.
        """
        hash1 = self.hash_pickle(module_level_func)
        hash2 = self.hash_pickle(module_level_func)
        self.assertEqual(hash1, hash2, "Pickle output hash differs for module-level function")
        round_trip_obj = self.round_trip(module_level_func)
        self.assertEqual(round_trip_obj, module_level_func, "Round-trip deserialization failed for module-level function")

    def test_empty_containers(self):
        """
        Test stability of empty containers including list, tuple, dict, set, and frozenset,
        and verify round-trip deserialization returns equivalent empty containers.
        """
        containers = [[], (), {}, set(), frozenset()]
        for container in containers:
            with self.subTest(container=container):
                hash1 = self.hash_pickle(container)
                hash2 = self.hash_pickle(container)
                self.assertEqual(hash1, hash2, f"Pickle output hash differs for empty container: {container}")
                round_trip_obj = self.round_trip(container)
                self.assertEqual(round_trip_obj, container, f"Round-trip deserialization failed for empty container: {container}")

    def test_unpicklable_lambda(self):
        """
        Test that unpicklable lambda functions raise an exception when pickled.
        """
        with self.assertRaises(Exception):
            pickle.dumps(lambda x: x)

    def test_pickle_protocols(self):
        """
        Test that pickle output is stable across multiple serializations for all supported pickle protocols.
        """
        value = {"key": "value", "number": 12345}
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            with self.subTest(protocol=protocol):
                hash1 = self.hash_pickle(value, protocol=protocol)
                hash2 = self.hash_pickle(value, protocol=protocol)
                self.assertEqual(hash1, hash2, f"Pickle output hash differs for protocol {protocol}")

if __name__ == "__main__":
    unittest.main()
