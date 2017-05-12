import sqlite3, random

conn=sqlite3.connect("./players.db")
curr=conn.cursor()

skips=("player_id", "player_name", "wins", "losses", "draws")
skills=("read_ability", "bluff_ability")
throws=("rock", "paper", "scissors")

curr.execute("PRAGMA table_info(players)")
info = []
for a in curr.fetchall():
	info.append(a[1])

curr.execute("select player_id from players")
players=[]
for a in curr.fetchall():
	players.append(a[0])

for a in players:
	update_str="UPDATE players SET %s=%s WHERE player_id=%s"
	query_str="SELECT %s FROM players WHERE player_id=%s"
		
	for b in info:
		if b in skills:
			curr.execute(query_str % (b,a))
			x=curr.fetchall()
			#DEBUG LINE
			print(query_str % (b,a))
			if x[0][0]==0:
				new_skill=random.randrange(20,100, 5)
				curr.execute(update_str % (b,new_skill,a))
				#DEBUG LINE
				print(update_str % (b,new_skill,a))
		elif b in throws:
			curr.execute(query_str % (b,a))
			x=curr.fetchall()
			#DEBUG LINE
			print(query_str % (b,a))
			new_throw=random.randrange(10,40,2)
			curr.execute(update_str % (b,new_throw,a))
			#DEBUG LINE
			print(update_str % (b,new_throw,a))
conn.commit()

		
				
				

