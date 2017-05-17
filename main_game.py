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

    def readOpp(self):
        roll = random.randrange(0, 105, 5)
        if roll<=self.readAbil and roll>1:
            success = random.randint(0, 2)
            if success == 2 or roll == 100:
                return "crit read"
            elif success == 1:
                return "read"
            else:
                return "low read"
        elif roll > 1:
            return None
        else:
            return False

    def bluffOpp(self):




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
            player_throw = False
            opp_throw = False
            throws = ("rock", "paper", "scissors")
            abils = ("read" , "bluff")
            player_ability_played = False
            opp_ability_played = False

            # Initial choices
            while not player_throw:
                player_throw = self.player_input(throws+abils)
                opp_throw = random.choice(("throw",)+abils)
                if player_throw in abils:
                    player_ability_played = True
                if opp_throw in abils:
                    opp_ability_played = True

            # Resolve choices
            if opp_ability_played or player_ability_played:
                # check player first
                if type(player_throw) == tuple:
                    if type(opp_throw) == tuple:
                        if player_throw[0] == "bluff":
                            if player_throw[1] == "crit":
                                player_throw = self.player_input(throws)
                                if player_throw == "rock":
                                    opp_throw = "scissors"
                                elif player_throw == "scissors":
                                    opp_throw = "paper"
                                else:
                                    opp_throw = "rock"
                            elif player_throw[1] == "normal":
                                player_throw = self.player_input(throws)
                                new_throws = list(throws)
                                if opp_throw[0] == "read":
                                    if opp_throw[1] not in ("crit","fail"):
                                        new_throws.remove(self.get_opposite(player_throw))
                                        opp_throw = random.choice(new_throws)
                                    elif opp_throw[1] == "crit":
                                        new_throws.remove(player_throw)
                                        opp_throw = random.choice(new_throws)
                                    elif opp_throw[1] == "fail":
                                        opp_throw = self.get_opposite(self.get_opposite(player_throw))
                                else:
                                    new_throws.remove(self.get_opposite(player_throw))
                                    opp_throw = random.choice(new_throws)
                            elif player_throw[1] == "weak":
                                if opp_throw[0] == "read":
                                    if opp_throw[1] not in ("crit","fail"):
                                        new_throws.remove(player_throw)
                                        opp_throw = random.choice(new_throws)
                                    elif opp_throw[1] == "crit":
                                        new_throws.remove(self.get_opposite(self.get_opposite(player_throw)))
                                        opp_throw = random.choice(new_throws)
                                    else:
                                        opp_throw = self.get_opposite(self.get_opposite(player_throw))
                            elif player_throw[1] == "fail":
                                opp_throw = self.get_opposite(player_throw)
                        elif player_throw[0] == "read":
                            if opp_throw[0] == "bluff":
                                if opp_throw[1] not in ("crit","fail"):
                                    if player_throw[1] == "crit":
                                        self.print_opp_chances("full")
                                    elif player_throw[1] == "normal":
                                        if opp_throw[1] == "normal":
                                            self.print_opp_chances("low")
                                        else:
                                            self.print_opp_chances("single")
                                    elif player_throw[1] == "low":
                                        if opp_throw != "low":
                                            print("They seemed to have blocked your read.")
                                        else:
                                            self.print_opp_chances("low")







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

    def print_opp_chances(self, level):
        if level == "full":
            paper = len(self.opp.paper)
            sciz = len(self.opp.scissors)
            rock = len(self.opp.rock)
            total_throws = paper + rock + sciz
            paper = (paper/total_throws)*100
            rock = (rock/total_throws)*100
            sciz = (sciz/total_throws)*100
            output_str = "Paper:\t%.2f%%\nRock:\t%.2f%%\nScissors:\t%.2f%%" % (paper, rock, sciz)
            print(output_str)
        elif level == "single":
            paper = len(self.opp.paper)
            sciz = len(self.opp.scissors)
            rock = len(self.opp.rock)
            total_throws = paper + rock + sciz
            paper = (paper / total_throws) * 100
            rock = (rock / total_throws) * 100
            sciz = (sciz / total_throws) * 100
            paper = ["paper",paper]
            rock = ["rock",rock]
            sciz = ["scissors",sciz]
            throw_dict={}
            for a in (paper,rock,sciz):
                throw_dict[int(a[0])]=a
            x = max(throw_dict)
            output_str = "%s:\t%.2f%%" % tuple(throw_dict[x][1])
            print(output_str)
        else:
            paper = len(self.opp.paper)
            sciz = len(self.opp.scissors)
            rock = len(self.opp.rock)
            total_throws = paper + rock + sciz
            paper = (paper / total_throws) * 100
            rock = (rock / total_throws) * 100
            sciz = (sciz / total_throws) * 100
            paper = ["paper", paper]
            rock = ["rock", rock]
            sciz = ["scissors", sciz]
            throw_dict = {}
            for a in (paper, rock, sciz):
                throw_dict[int(a[0])] = a
            x = max(throw_dict)
            output_str = "Maybe %s." % throw_dict[x][0]
            print(output_str)

    def get_opposite(self, throw):
        if throw == "rock":
            return "paper"
        elif throw == "paper":
            return "scissors"
        elif throw == "scissors":
            return "rock"

    def check_player_bluff(self, bluff, player_throw):
        if bluff == "crit bluff":
            if player_throw == "rock":
                opp_throw = "scissors"
            elif player_throw == "paper":
                opp_throw = "rock"
            else:
                opp_throw = "paper"
            return opp_throw
        elif bluff == "bluff":
            if player_throw == "rock":
                self.opp.paper = 0
            elif player_throw == "paper":
                self.opp.scissors = 0
            else:
                self.opp.rock = 0
        elif bluff == "weak bluff":
            if player_throw == "rock":
                self.opp.paper /= 2
                self.opp.scissors *= 1.5
            elif player_throw == "paper":
                self.opp.scissors /= 2
                self.opp.rock *= 1.5
            else:
                self.opp.rock /= 2
                self.opp.paper *= 1.5
        elif bluff:
            if player_throw == "rock":
                opp_throw = "paper"
            elif player_throw == "paper":
                opp_throw = "scissors"
            else:
                opp_throw = "rock"
            return opp_throw

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





