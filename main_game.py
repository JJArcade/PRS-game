import sqlite3, random, re, os

class npc_player:

    def __init__(self, player):
        player_file = os.path.abspath("players.db")
        self.conn = sqlite3.connect(player_file)
        self.curr = self.conn.cursor()
        self.playerID = player
        # get name
        self.curr.execute("SELECT player_name FROM players WHERE player_id = %s" % player)
        self.playerName = ""
        for a in self.curr:
            self.playerName = a[0]

        # set stats
        stats_query = "SELECT read_ability, bluff_ability, paper, rock, scissors FROM" \
                      " players WHERE player_id=%s"
        self.curr.execute(stats_query % self.playerID)
        x = self.curr.fetchone()
        self.readAbil = x[0]
        self.bluffAbil = x[1]
        self.paper = int(x[2])
        self.rock = int(x[3])
        self.scissors = int(x[4])

    def updateRecord(self, outcome):
        select_query = "SELECT %s WHERE player_id = %s" % (outcome, self.playerID)
        update_query = "UPDATE players SET %s=(%s)+1 WHERE player_id = %s" % (outcome, select_query, self.playerID)
        #print(update_query)
        #curr.execute(update_query)

    def throw(self):
        papers = ["paper"]*self.paper
        rocks = ["rock"]*self.rock
        scissors = ["scissors"]*self.scissors
        pool = papers+rocks+scissors
        choice = random.choice(pool)
        return choice

class player(npc_player):

    def updateStats(self, opponent):
        opp_avg = (opponent.readAbil + opponent.bluffAbil)/2
        play_avg = (self.readAbil + self.bluffAbil)/2
        points_added = 2 + 10*((opp_avg-play_avg)/100)
        skills = ("read_ability", "bluff_ability")
        update_query = "UPDATE players SET %s = %s WHERE player_id = %s"
        #print(update_query % (skills[0], self.readAbil+points_added, self.playerID))
        #print(update_query % (skills[0], self.bluffAbil+points_added, self.playerID))

        #self.curr.execute(update_query % (skills[0], self.readAbil+points_added, self.playerID))
        #self.curr.execute(update_query % (skills[1], self.bluffAbil+points_added, self.playerID))

class gameplay:

    def __init__(self, Player, Opponent):
        self.papers = ("paper", "Paper")
        self.rocks = ("rock", "Rocks")
        self.sciz = ("scissors", "Scissors")
        self.opp = Opponent
        self.opp_name = Opponent.playerName

        print("%s VS %s \nLETS GET IT ON!" % ("You", self.opp_name))

    def match(self):
        Round = 1
        score = 0

        while Round <= 3:
            print("ROUND %s" % Round)
            player_throw = self.player_input()
            opp_throw = self.opp.throw()
            result = self.outcome(player_throw, opp_throw)
            action_str = "You:\t%s\n%s:\t%s" % (player_throw, self.opp_name, opp_throw)
            print(action_str)
            result_str = "It's a %s." % result
            print(result_str)
            if result == "win":
                score+=1
            elif result == "loss":
                score-=1
            #print(abs(score))
            if abs(score) == 2:
                break
            Round+=1

        return score

    def player_input(self):
        choice = input("Enter your move!\n")
        possible_choices = self.papers+self.rocks+self.sciz
        good_choice = bool(choice in possible_choices)
        if not good_choice:
            while not good_choice:
                choice = input("Not a valid throw choice.\n Try again.\n")
                good_choice = bool(choice in possible_choices)
        return choice

    def outcome(self, player_throw, opp_throw):
        if player_throw in self.rocks:
            if opp_throw in self.papers:
                return "loss"
            elif opp_throw in self.rocks:
                return "draw"
            elif opp_throw in self.sciz:
                return "win"

        if player_throw in self.papers:
            if opp_throw in self.papers:
                return "draw"
            elif opp_throw in self.rocks:
                return "win"
            elif opp_throw in self.sciz:
                return "loss"

        if player_throw in self.sciz:
            if opp_throw in self.papers:
                return "win"
            elif opp_throw in self.rocks:
                return "loss"
            elif opp_throw in self.sciz:
                return "draw"

if __name__ == "__main__":
    player_file = os.path.abspath("players.db")
    conn = sqlite3.connect(player_file)
    curr = conn.cursor()
    # grab players
    select_query = "SELECT player_id FROM players WHERE player_name != \"_player\""
    curr.execute(select_query)
    players = []
    for a in curr:
        players.append(a[0])

    # set up player
    curr.execute("SELECT player_id FROM players WHERE player_name = \"_player\"")
    main_id = curr.fetchone()
    main_id = main_id[0]
    you = player(main_id)

    # main loop
    Exit = False
    while not Exit:
        y = random.choice(players)
        curr_opponent = npc_player(y)
        game = gameplay(you, curr_opponent)
        curr_game = game.match()
        if curr_game>0:
            you.updateStats(curr_opponent)
            you.updateRecord("wins")
            curr_opponent.updateRecord("losses")
            print("You WON the match!")
            print("%s slinks away in defeat..." % curr_opponent.playerName)
        elif curr_game<0:
            you.updateRecord("losses")
            curr_opponent.updateRecord("wins")
            print("You LOST the match!")
            print("%s texts your mom about your failure..." % curr_opponent.playerName)
        else:
            you.updateRecord("draws")
            curr_opponent.updateRecord("draws")
            print("The match is a draw.")
            print("I have no feelings on the matter.")
        conn.commit()
        leave = input("Exit? y/n\n")
        if leave in ("y", "Y"):
            Exit = True





