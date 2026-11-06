import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check

# ============================================================
# Schéma de la table BRUTE (telle qu'elle arrive du CSV)
# ============================================================
# On valide ce qui est indispensable AVANT le nettoyage :
# - les colonnes obligatoires existent
# - les types sont ceux que pandas produit après read_csv()
# - les valeurs ne sont pas absurdes au point de casser le pipeline
RawOrdersSchema = DataFrameSchema(
    {
        "order_id": Column(int, Check.gt(0), nullable=False),
        "order_date": Column(str, nullable=False),
        "customer_id": Column(str, nullable=True),  # peut être vide (règle 1 le rejettera)
        "country": Column(str, nullable=False),
        "product": Column(str, nullable=False),
        "quantity": Column(int, nullable=False),
        "unit_price": Column(float, nullable=False),
    },
    strict=False,   # tolère les colonnes _row_number, _loaded_at, etc.
    coerce=False,
)

# ============================================================
# Schéma de la table PROPRE (sortie de clean_orders)
# ============================================================
# Ici, on applique TOUTES les règles de qualité :
# - règle 1 : customer_id non nul
# - règle 2 : order_date valide (converti par clean_orders)
# - règle 3 : quantity > 0
# - règle 4 : unit_price entre 0.01 et 1000
# - règle 5 : order_id unique
# - règle 6 : country dans la liste des 5 pays
OrdersCleanSchema = DataFrameSchema(
    {
        "order_id": Column(
            int,
            Check.gt(0),
            unique=True,          # règle 5 : pas de doublon
            nullable=False,
        ),
        "order_date": Column(
            "datetime64[ns]",     # clean_orders a converti en datetime
            nullable=False,       # règle 2 : pas de date vide
        ),
        "customer_id": Column(
            str,       # règle 1 : client obligatoire
            nullable=False,
        ),
        "country": Column(
            str,
            Check.isin(["France", "Germany", "Italy", "Morocco", "Tunisia"]),  # règle 6
            nullable=False,
        ),
        "product": Column(str, nullable=False),
        "quantity": Column(
            int,
            Check.ge(1),          # règle 3 : quantité >= 1
            nullable=False,
        ),
        "unit_price": Column(
            float,
            Check.in_range(0.01, 1000.0),  # règle 4 : prix plausible
            nullable=False,
        ),
    },
    strict=False,   # ignore les colonnes non listées (_row_number, etc.)
    coerce=True,    # convertit les types si nécessaire
)