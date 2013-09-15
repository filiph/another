from collections import deque
import sqlite3

import logging
logger = logging.getLogger("another.vote_history_manager")

class VoteHistoryManager:
    def __init__(self, filename="vote_history.db"):
        self.database_filename = filename
        self.no_emit_yet = True
        self.latest_votes = deque([])

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
                     "vote INTEGER,"
                     "is_trolling BOOLEAN);")
        conn.commit()
        conn.close()

    YES = 1
    NO = -1
    MEH = 0

    MAX_LATEST_VOTES = 5

    def _detect_trolling(self):
        if len(self.latest_votes) < self.MAX_LATEST_VOTES:
            return False
        all_same = all(x == self.latest_votes[0] for x in self.latest_votes)
        if all_same and (self.latest_votes[0] == self.YES or self.latest_votes[0] == self.NO):
            logger.info("Trolling detected (%s latest votes are the same).", self.MAX_LATEST_VOTES)
            return True
        else:
            return False

    def emit(self, phenotype, vote):
        self.latest_votes.append(vote)
        if len(self.latest_votes) > self.MAX_LATEST_VOTES:
            self.latest_votes.popleft()
        is_trolling = self._detect_trolling()
        try:
            if self.no_emit_yet == True:
                self._create_table_if_not_exists()
            conn = self._create_connection()
            conn.execute("INSERT INTO votes (phenotype_id, vote, is_trolling) VALUES (?, ?, ?)",
                         (phenotype.idn, vote, is_trolling))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error("Record of vote not created, error with database: %s", e)
        return is_trolling
