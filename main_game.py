import sqlite3, random

class npc_player:

    def __init__(self, player):
        self.conn = sqlite3.connect("./players.db")
        self.curr = self.conn.cursor()
        self.playerID = player
        # set stats
        stats_query = "SELECT read_ability, bluff_ability, paper, rock, scissors FROM" \
                      " players WHERE player_id=%s"
        self.curr.execute(stats_query % self.playerID)
        x = self.curr.fetchone()
        self.readAbil = x[0]
        self.bluffAbil = x[1]
        self.paper = x[2]
        self.rock = x[3]
        self.scissors = x[4]

    def updateRecord(self, outcome):
        select_query = "SELECT %s WHERE player_id = %s" % (outcome, self.playerID)
        update_query = "UPDATE players SET %s=(%s)+1 WHERE player_id=%s" % (outcome, select_query, self.playerID)
        print(update_query)
        #curr.execute(update_query)

    def throw(self):
        papers = ["paper"]*self.paper
        rocks = ["rock"]*self.rock
        scissors = ["scissors"]*self.scissors
        pool = papers+rocks+scissors
        choice = random.choice(pool)
        return choice

if __name__ == "__main__":
    conn = sqlite3.connect("./players.db")
    curr = conn.cursor()
    # grab players
    select_query = "SELECT player_id FROM players WHERE player_name != \"_player\""
    curr.execute(select_query)
    players = []
    for a in curr:
        players.append(a[0])



