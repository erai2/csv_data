"""Profile persistence helpers built on top of the central DB manager."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from . import db_manager


def save_profile(
    name: str,
    gender: str,
    gan: str,
    zhi: str,
    daewoon: str,
    sewoon: str,
    structure: Dict,
    result: List[Dict],
) -> None:
    """Persist a profile entry including structure and inference results."""

    db_manager.init_db()
    payload = (
        name,
        gender,
        gan,
        zhi,
        daewoon,
        sewoon,
        json.dumps(structure, ensure_ascii=False),
        json.dumps(result, ensure_ascii=False),
    )

    with db_manager.get_connection(None) as conn:
        conn.execute(
            """
            INSERT INTO profiles (name, gender, gan, zhi, daewoon, sewoon, structure_json, result_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        conn.commit()


def list_profiles() -> List[Dict[str, str]]:
    """Retrieve basic information about stored profiles."""

    db_manager.init_db()
    with db_manager.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, gender, gan, zhi, daewoon, sewoon, structure_json, result_json, created_at
            FROM profiles
            ORDER BY created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def load_profile(profile_id: int) -> Optional[Dict]:
    """Fetch the full payload for a single profile."""

    db_manager.init_db()
    with db_manager.get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, name, gender, gan, zhi, daewoon, sewoon, structure_json, result_json, created_at
            FROM profiles
            WHERE id = ?
            """,
            (profile_id,),
        ).fetchone()
    if not row:
        return None

    payload = dict(row)
    payload["structure"] = json.loads(payload.pop("structure_json"))
    payload["results"] = json.loads(payload.pop("result_json"))
    return payload


def delete_profile(profile_id: int) -> None:
    """Remove a stored profile entry."""

    db_manager.init_db()
    with db_manager.get_connection(None) as conn:
        conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        conn.commit()

