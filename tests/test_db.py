# tests/test_db.py
"""
Tests for db.py

These tests verify:
- engine can be created
- SessionLocal produces a working session
- get_db() yields a session and then closes it
"""

from app.db import engine, SessionLocal, get_db

def test_engine_exists():
    # Just assert that engine is not None and has a URL attribute
    assert engine is not None
    assert hasattr(engine, "url")

def test_sessionlocal_creates_session():
    db = SessionLocal()
    try:
        # basic sanity check: the session should have a bind (the engine)
        assert db.bind is engine
    finally:
        db.close()

def test_get_db_yields_session():
    # get_db() is a generator dependency; we can manually iterate it
    gen = get_db()
    db = next(gen)  # get the yielded session
    assert db.bind is engine

    # After closing, StopIteration should be raised if we call next() again
    try:
        next(gen)
    except StopIteration:
        # This is expected: the generator has finished cleanly
        assert True
    else:
        # If no StopIteration, something is wrong
        assert False