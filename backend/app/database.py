from __future__ import annotations

from sqlmodel import SQLModel, Session, create_engine, select

from models import StarSystem

DB_URL = "sqlite:///./gemini.db"
engine = create_engine(DB_URL, echo=False)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# ---------------------------------------------------------------------------
# Seed data – 88 IAU constellations
# format: (name, meaning, area_sq_deg, quadrant, lat_max, lat_min)
# ---------------------------------------------------------------------------
STAR_SYSTEMS: list[tuple] = [
    ("Andromeda",           "Andromeda",                722.278,  "NQ1", 90, 40),
    ("Antlia",              "Air Pump",                 238.901,  "SQ2", 45, 90),
    ("Apus",                "Bird of Paradise",         206.327,  "SQ3",  5, 90),
    ("Aquarius",            "Water Bearer",             979.854,  "SQ4", 65, 90),
    ("Aquila",              "Eagle",                    652.473,  "NQ4", 90, 75),
    ("Ara",                 "Altar",                    237.057,  "SQ3", 25, 90),
    ("Aries",               "Ram",                      441.395,  "NQ1", 90, 60),
    ("Auriga",              "Charioteer",               657.438,  "NQ2", 90, 40),
    ("Boötes",              "Herdsman",                 906.831,  "NQ3", 90, 50),
    ("Caelum",              "Chisel",                   124.865,  "SQ1", 40, 90),
    ("Camelopardalis",      "Giraffe",                  756.828,  "NQ2", 90, 10),
    ("Cancer",              "Crab",                     505.872,  "NQ2", 90, 60),
    ("Canes Venatici",      "Hunting Dogs",             465.194,  "NQ3", 90, 40),
    ("Canis Major",         "Greater Dog",              380.118,  "SQ2", 60, 90),
    ("Canis Minor",         "Lesser Dog",               183.367,  "NQ2", 90, 75),
    ("Capricornus",         "Sea Goat",                 413.947,  "SQ4", 60, 90),
    ("Carina",              "Keel",                     494.184,  "SQ2", 20, 90),
    ("Cassiopeia",          "Cassiopeia",               598.407,  "NQ1", 90, 20),
    ("Centaurus",           "Centaur",                 1060.422,  "SQ3", 25, 90),
    ("Cepheus",             "Cepheus",                  587.787,  "NQ4", 90, 10),
    ("Cetus",               "Whale (or Sea Monster)",  1231.411,  "SQ1", 70, 90),
    ("Chamaeleon",          "Chameleon",                131.592,  "SQ2",  0, 90),
    ("Circinus",            "Compass (drafting tool)",   93.353,  "SQ3", 30, 90),
    ("Columba",             "Dove",                     270.184,  "SQ1", 45, 90),
    ("Coma Berenices",      "Berenice's Hair",          386.475,  "NQ3", 90, 70),
    ("Corona Australis",    "Southern Crown",           127.696,  "SQ4", 40, 90),
    ("Corona Borealis",     "Northern Crown",           178.710,  "NQ3", 90, 50),
    ("Corvus",              "Crow",                     183.801,  "SQ3", 60, 90),
    ("Crater",              "Cup",                      282.398,  "SQ2", 65, 90),
    ("Crux",                "Southern Cross",            68.447,  "SQ3", 20, 90),
    ("Cygnus",              "Swan",                     803.983,  "NQ4", 90, 40),
    ("Delphinus",           "Dolphin",                  188.549,  "NQ4", 90, 70),
    ("Dorado",              "Dolphinfish",              179.173,  "SQ1", 20, 90),
    ("Draco",               "Dragon",                  1082.952,  "NQ3", 90, 15),
    ("Equuleus",            "Little Horse (Foal)",       71.641,  "NQ4", 90, 80),
    ("Eridanus",            "Eridanus (river)",        1137.919,  "SQ1", 32, 90),
    ("Fornax",              "Furnace",                  397.502,  "SQ1", 50, 90),
    ("Gemini",              "Twins",                    513.761,  "NQ2", 90, 60),
    ("Grus",                "Crane",                    365.513,  "SQ4", 34, 90),
    ("Hercules",            "Hercules",                1225.148,  "NQ3", 90, 50),
    ("Horologium",          "Pendulum Clock",           248.885,  "SQ1", 30, 90),
    ("Hydra",               "Hydra",                   1302.844,  "SQ2", 54, 83),
    ("Hydrus",              "Water Snake",              243.035,  "SQ1",  8, 90),
    ("Indus",               "Indian",                   294.006,  "SQ4", 15, 90),
    ("Lacerta",             "Lizard",                   200.688,  "NQ4", 90, 40),
    ("Leo",                 "Lion",                     946.964,  "NQ2", 90, 65),
    ("Leo Minor",           "Lesser Lion",              231.956,  "NQ2", 90, 45),
    ("Lepus",               "Hare",                     290.291,  "SQ1", 63, 90),
    ("Libra",               "Scales",                   538.052,  "SQ3", 65, 90),
    ("Lupus",               "Wolf",                     333.683,  "SQ3", 35, 90),
    ("Lynx",                "Lynx",                     545.386,  "NQ2", 90, 55),
    ("Lyra",                "Lyre",                     286.476,  "NQ4", 90, 40),
    ("Mensa",               "Table Mountain",           153.484,  "SQ1", 49, 90),
    ("Microscopium",        "Microscope",               209.513,  "SQ4", 45, 90),
    ("Monoceros",           "Unicorn",                  481.569,  "NQ2", 75, 90),
    ("Musca",               "Fly",                      138.355,  "SQ3", 10, 90),
    ("Norma",               "Level",                    165.290,  "SQ3", 30, 90),
    ("Octans",              "Octant",                   291.045,  "SQ4",  0, 90),
    ("Ophiuchus",           "Serpent Bearer",           948.340,  "SQ3", 80, 80),
    ("Orion",               "Orion (the Hunter)",       594.120,  "NQ1", 85, 75),
    ("Pavo",                "Peacock",                  377.666,  "SQ4", 30, 90),
    ("Pegasus",             "Pegasus",                 1120.794,  "NQ4", 90, 60),
    ("Perseus",             "Perseus",                  614.997,  "NQ1", 90, 35),
    ("Phoenix",             "Phoenix",                  469.319,  "SQ1", 32, 80),
    ("Pictor",              "Easel",                    246.739,  "SQ1", 26, 90),
    ("Pisces",              "Fishes",                   889.417,  "NQ1", 90, 65),
    ("Piscis Austrinus",    "Southern Fish",            245.375,  "SQ4", 55, 90),
    ("Puppis",              "Stern",                    673.434,  "SQ2", 40, 90),
    ("Pyxis",               "Compass",                  220.833,  "SQ2", 50, 90),
    ("Reticulum",           "Reticle",                  113.936,  "SQ1", 23, 90),
    ("Sagitta",             "Arrow",                     79.932,  "NQ4", 90, 70),
    ("Sagittarius",         "Archer",                   867.432,  "SQ4", 55, 90),
    ("Scorpius",            "Scorpion",                 496.783,  "SQ3", 40, 90),
    ("Sculptor",            "Sculptor",                 474.764,  "SQ1", 50, 90),
    ("Scutum",              "Shield (of Sobieski)",     109.114,  "SQ4", 80, 90),
    ("Serpens",             "Snake",                    636.928,  "NQ3", 80, 80),
    ("Sextans",             "Sextant",                  313.515,  "SQ2", 80, 90),
    ("Taurus",              "Bull",                     797.249,  "NQ1", 90, 65),
    ("Telescopium",         "Telescope",                251.512,  "SQ4", 40, 90),
    ("Triangulum",          "Triangle",                 131.847,  "NQ1", 90, 60),
    ("Triangulum Australe", "Southern Triangle",        109.978,  "SQ3", 25, 90),
    ("Tucana",              "Toucan",                   294.557,  "SQ4", 25, 90),
    ("Ursa Major",          "Great Bear",              1279.660,  "NQ2", 90, 30),
    ("Ursa Minor",          "Little Bear",              255.864,  "NQ3", 90, 10),
    ("Vela",                "Sails",                    499.649,  "SQ2", 30, 90),
    ("Virgo",               "Virgin (Maiden)",         1294.428,  "SQ3", 80, 80),
    ("Volans",              "Flying Fish",              141.354,  "SQ2", 15, 90),
    ("Vulpecula",           "Fox",                      268.165,  "NQ4", 90, 55),
]


def seed_star_systems() -> None:
    """Insert all 88 constellations if the table is empty."""
    with Session(engine) as session:
        existing = session.exec(select(StarSystem)).first()
        if existing:
            return  # already seeded
        for row in STAR_SYSTEMS:
            session.add(StarSystem(
                name=row[0],
                meaning=row[1],
                area_sq_deg=row[2],
                quadrant=row[3],
                latitude_max=row[4],
                latitude_min=row[5],
            ))
        session.commit()


if __name__ == "__main__":
    create_db_and_tables()
    seed_star_systems()
    print("Database created and seeded.")