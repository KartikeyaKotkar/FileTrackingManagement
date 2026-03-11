from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] / "sql"


class SQLRegistry:
    def __init__(self):
        self.documents = {}
        self.versions = {}
        self.movement = {}
        self.logs = {}

        self._load_queries()

    def _load_queries(self):

        for category in ["documents", "versions", "movement", "logs"]:
            folder = BASE_DIR / category

            queries = {}

            for file in folder.glob("*.sql"):
                name = file.stem
                queries[name] = file.read_text()

            setattr(self, category, type("SQLGroup", (), queries))


sql = SQLRegistry()
