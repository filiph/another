import sqlite3

import logging
logger = logging.getLogger("another.vote_history_manager")

class VoteHistoryManager:
    def __init__(self, filename="vote_history.db"):
        self.database_filename = filename
        self.no_emit_yet = True

    def close(self):
        pass

    def _create_connection(self):
        return sqlite3.connect(self.database_filename)

    def _create_table_if_not_exists(self):
        conn = self._create_connection()
        conn.execute("CREATE TABLE IF NOT EXISTS votes ("
                     "id INTEGER PRIMARY KEY, "
                     "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,"
                     "phenotype_id INTEGER,"
                     "vote INTEGER);")
        conn.commit()
        conn.close()

    YES = 1
    NO = -1
    MEH = 0

    def emit(self, phenotype, vote):
        if self.no_emit_yet == True:
            self._create_table_if_not_exists()
        conn = self._create_connection()
        conn.execute("INSERT INTO votes (phenotype_id, vote) VALUES (?, ?)", (phenotype.idn, vote))
        conn.commit()
        conn.close()

