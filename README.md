# PA1465_project

This project is a comprehensive test suite designed to verify the stability and consistency of Python's built-in pickle module across various data types, custom classes and protocols.

## Features

* Verifies stable serialization output using SHA-256 hashing

* Tests a wide range of objects including:

    + Basic types (int, str, list, dict, etc.)

    + User-defined classes with and without __slots__

    + Classes using __getstate__ / __setstate__

    + Circular references

    + Exceptions and module-level functions

    + Tests multiple pickle protocols

Includes a round-trip check (optional) to ensure semantic equality after serialization