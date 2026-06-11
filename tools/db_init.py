import sqlite3

DB_PATH = "ressources/app.db"


def init_db(seed: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            friendly_name TEXT NOT NULL,
            ieee_name TEXT NOT NULL UNIQUE,
            display_name TEXT,
            status TEXT NOT NULL,
            power_state INTEGER DEFAULT 0,
            last_states TEXT
        )
    """)

    # Optional seed data
    if seed:
        cursor.executemany("""
            INSERT INTO devices (
                friendly_name,
                ieee_name,
                display_name,
                status,
                power_state,
                last_states
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                "living_room_light",
                "0x0017880102345678",
                "Living Room Light",
                "ACTIVE",
                0,
                '{"brightness": 100, "color": "warm"}'
            ),
            (
                "kitchen_light",
                "0x0017880102345679",
                "Kitchen Light",
                "ACTIVE",
                0,
                '{"brightness": 80, "color": "neutral"}'
            )
        ])

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    # Change to True if you want templated rows inserted
    init_db(seed=False)