import sqlite3, random, re, os

class npc_player:

    def __init__(self, player):
        player_file=""
        for a in os.listdir(os.path.curdir):
            player_file = os.path.abspath(a)
            if bool(re.search("players.db", player_file)):
                break
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
        self.paper = random.randint(0,100)
        self.rock = random.randint(0,100)
        self.scissors = random.randint(0,100)

    def updateRecord(self, outcome):
        select_query = "SELECT %s WHERE player_id = %s" % (outcome, self.playerID)
        update_query = "UPDATE players SET %s=(%s)+1 WHERE player_id = %s" % (outcome, select_query, self.playerID)
        print(update_query)
        self.curr.execute(update_query)

        self.conn.commit()

    def rerollThrows(self):
        self.paper = random.randint(0, 100)
        self.rock = random.randint(0, 100)
        self.scissors = random.randint(0, 100)

    def throw(self):
        papers = ["paper"]*int(self.paper)
        rocks = ["rock"]*int(self.rock)
        scissors = ["scissors"]*int(self.scissors)
        pool = papers+rocks+scissors
        choice = random.choice(pool)
        self.rerollThrows()
        return choice


class player(npc_player):

    def updateStats(self, opponent):
        opp_avg = (opponent.readAbil + opponent.bluffAbil)/2
        play_avg = (self.readAbil + self.bluffAbil)/2
        points_added = 2 + 10*((opp_avg-play_avg)/100)
        skills = ("read_ability", "bluff_ability")
        update_query = "UPDATE players SET %s = %s WHERE player_id = %s"
        print(update_query % (skills[0], self.readAbil+points_added, self.playerID))
        print(update_query % (skills[0], self.bluffAbil+points_added, self.playerID))

        self.curr.execute(update_query % (skills[0], self.readAbil+points_added, self.playerID))
        self.curr.execute(update_query % (skills[1], self.bluffAbil+points_added, self.playerID))

        # UPDATE CHARACTER WITH NEW STATS
        stats_query = "SELECT read_ability, bluff_ability, paper, rock, scissors FROM" \
                      " players WHERE player_id=%s"
        self.curr.execute(stats_query % self.playerID)
        x = self.curr.fetchone()
        self.readAbil = x[0]
        self.bluffAbil = x[1]
        self.paper = int(x[2])
        self.rock = int(x[3])
        self.scissors = int(x[4])

        self.conn.commit()


class gameplay:

    def __init__(self, Player, Opponent):
        self.papers = ("paper", "Paper")
        self.rocks = ("rock", "Rock")
        self.sciz = ("scissors", "Scissors")
        self.opp = Opponent
        self.opp_name = Opponent.playerName
        self.Player = Player

        print("%s VS %s \nLETS GET IT ON!" % ("You", self.opp_name))

    def match(self):
        Round = 1
        score = 0

        while Round <= 3:
            print("".ljust(10,'=')+"ROUND %s" % Round + "".ljust(10,'=')+"\n")

            ## INPUT CYCLE
            player_thrown = False
            read_bluff_called = False
            player_fail = False
            opp_throw = None
            opp_choices = ["rock", "paper", "scissors"]
            while not player_thrown:
                if not read_bluff_called:
                    player_throw = self.player_input(("scissors","rock","paper","bluff","read"))
                else:
                    player_throw = self.player_input(("scissors","rock","paper"))
                bluff_thrown = bool(re.match(player_throw,"bluff",re.IGNORECASE))
                read_thrown = bool(re.match(player_throw,"read",re.IGNORECASE))
                if read_thrown or bluff_thrown:
                    x = None
                    read_bluff_called = True
                    if read_thrown:
                        x = self.readOpp(self.opp)
                    else:
                        x = self.bluffOpp()
                    if x is not None:
                        if read_thrown:
                            player_fail = True
                        else:
                            if x == False:
                                player_fail = True
                            else:
                                player_fail = x
                else:
                    player_thrown = True
                    if player_fail == "crit bluff":
                        if player_throw == "rock":
                            opp_throw = "scissors"
                        elif player_throw == "paper":
                            opp_throw = "rock"
                        else:
                            opp_throw = "paper"
                    elif player_fail == "bluff":
                        if player_throw == "rock":
                            self.opp.paper = 0
                        elif player_throw == "paper":
                            self.opp.scissors = 0
                        else:
                            self.opp.rock = 0
                    elif player_fail == "weak bluff":
                        if player_throw == "rock":
                            self.opp.paper/=2
                            self.opp.scissors*=1.5
                        elif player_throw == "paper":
                            self.opp.scissors/=2
                            self.opp.rock*=1.5
                        else:
                            self.opp.rock/=2
                            self.opp.paper*=1.5
                    elif player_fail:
                        if player_throw == "rock":
                            opp_throw = "paper"
                        elif player_throw == "paper":
                            opp_throw = "scissors"
                        else:
                            opp_throw = "rock"

            if opp_throw is None:
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

    def player_input(self, options):
        choice = input("Enter your move!\n--> ")
        possible_choices = options
        # CHECK CHOICES
        good_choice = False
        while not good_choice:
            for a in possible_choices:
                if bool(re.match(a,choice,re.IGNORECASE)):
                    good_choice = True
                    choice = a
                    break
            if good_choice:
                break
            else:
                choice = input("That was an invalid entry.\nEnter your choice again.\n--> ")
        return choice

    def readOpp(self, opp):

        roll = random.randrange(0,105,5)
        if roll<=self.Player.readAbil and roll>1:
            success = random.randint(0,2)
            paper_per = opp.paper / (opp.paper + opp.scissors + opp.rock) * 100
            sciz_per = opp.scissors / (opp.paper + opp.scissors + opp.rock) * 100
            rock_per = opp.rock / (opp.paper + opp.scissors + opp.rock) * 100
            if success == 2 or roll == 100:
                output_string = "Paper:\t\t%.1f%%\nRock:\t\t%.1f%%\nScissors:\t%.1f%%" % (paper_per, sciz_per, rock_per)
                print(output_string)
            elif success == 1:
                most_likely = max((paper_per, sciz_per, rock_per))
                if most_likely == paper_per:
                    print("Paper:\t%.1f%%" % paper_per)
                elif most_likely == sciz_per:
                    print("Scissors:\t%.1f%%" % sciz_per)
                else:
                    print("Rock:\t%.1f%%" % rock_per)
            else:
                most_likely = max((paper_per, sciz_per, rock_per))
                if most_likely == paper_per:
                    print("Most likely paper.")
                elif most_likely == sciz_per:
                    print("Most likely scissors.")
                else:
                    print("Most likely a rock.")
        elif roll>1:
            print("You couldn't break their mind.")
        else:
            print("Instead of piercing their mind you instead let them into yours.")
            return False

    def bluffOpp(self):

        roll = random.randrange(0,105,5)
        if roll<=self.Player.bluffAbil and roll>1:
            success = random.randint(0,2)
            if success == 2 or roll == 100:
                print("You think you got them to bite.")
                return "crit bluff"
            elif success == 1:
                print("You feel good about that move.")
                return "bluff"
            else:
                print("You have had better bluffs.")
                return "weak bluff"
        elif roll>1:
            print("Your bluff failed.")
        else:
            print("You gave away your move.")
            return False

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
    player_file=""
    for a in os.listdir(os.path.curdir):
        player_file = os.path.abspath(a)
        if bool(re.search("players.db", player_file)):
            break
    print(player_file)
    input("Press ENTER to continue")
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
        if curr_game > 0:
            you.updateStats(curr_opponent)
            you.updateRecord("wins")
            curr_opponent.updateRecord("losses")
            print("You WON the match!")
            print("%s slinks away in defeat..." % curr_opponent.playerName)
        elif curr_game < 0:
            you.updateRecord("losses")
            curr_opponent.updateRecord("wins")
            print("You LOST the match!")
            print("%s texts your mom about your failure..." % curr_opponent.playerName)
        else:
            you.updateRecord("draws")
            curr_opponent.updateRecord("draws")
            print("The match is a draw.")
            print("I have no feelings on the matter.")
        # conn.commit()
        leave = input("Exit? y/n\n")
        if leave in ("y", "Y"):
            conn.close()
            curr_opponent.conn.close()
            Exit = True





