import pandas as pd
import pandera.pandas as pa
import pytest

from pipeline.schemas import OrdersCleanSchema, RawOrdersSchema


# ============================================================
# Helpers
# ============================================================

def make_raw(overrides=None):
    """Un DataFrame brut valide (1 ligne), modifiable."""
    default = {
        "order_id": 1001,
        "order_date": "2026-10-05",
        "customer_id": "C001",
        "country": "Tunisia",
        "product": "Mouse",
        "quantity": 1,
        "unit_price": 10.0,
    }
    if overrides:
        default.update(overrides)
    return pd.DataFrame([default])


def make_clean(overrides=None):
    """Un DataFrame propre valide (1 ligne), modifiable."""
    default = {
        "order_id": 1001,
        "order_date": pd.Timestamp("2026-10-05"),
        "customer_id": "C001",
        "country": "Tunisia",
        "product": "Mouse",
        "quantity": 1,
        "unit_price": 10.0,
    }
    if overrides:
        default.update(overrides)
    return pd.DataFrame([default])


# ============================================================
# RawOrdersSchema — structure brute
# ============================================================

def test_raw_schema_accepts_valid_data():
    RawOrdersSchema.validate(make_raw())


def test_raw_schema_rejects_missing_column():
    df = make_raw().drop(columns=["unit_price"])
    with pytest.raises(pa.errors.SchemaError):
        RawOrdersSchema.validate(df)


def test_raw_schema_rejects_negative_order_id():
    df = make_raw({"order_id": -1})
    with pytest.raises(pa.errors.SchemaError):
        RawOrdersSchema.validate(df)


# ============================================================
# OrdersCleanSchema — les 6 règles de qualité
# ============================================================

def test_clean_schema_accepts_valid_data():
    OrdersCleanSchema.validate(make_clean())


def test_clean_schema_rejects_negative_quantity():
    """Règle 3 : quantity >= 1."""
    df = make_clean({"quantity": -2})
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)


def test_clean_schema_rejects_zero_quantity():
    """Règle 3 : quantity >= 1 (0 est rejeté)."""
    df = make_clean({"quantity": 0})
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)


def test_clean_schema_rejects_unknown_country():
    """Règle 6 : country dans la liste."""
    df = make_clean({"country": "Spain"})
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)


def test_clean_schema_rejects_price_too_high():
    """Règle 4 : unit_price <= 1000."""
    df = make_clean({"unit_price": 4500.0})
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)


def test_clean_schema_rejects_price_too_low():
    """Règle 4 : unit_price >= 0.01."""
    df = make_clean({"unit_price": 0.0})
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)


def test_clean_schema_rejects_duplicate_order_id():
    """Règle 5 : order_id unique."""
    df = pd.concat([make_clean(), make_clean()], ignore_index=True)
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)


def test_clean_schema_rejects_null_customer():
    """Règle 1 : customer_id obligatoire."""
    df = make_clean({"customer_id": None})
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)


def test_clean_schema_rejects_null_date():
    """Règle 2 : order_date valide."""
    df = make_clean({"order_date": None})
    with pytest.raises(pa.errors.SchemaError):
        OrdersCleanSchema.validate(df)