import math

def calculateRating(winner_elo, loser_elo, winner_ratings, loser_ratings):
	
	if winner_ratings < 10:
		win_score = 240
	else:
		win_score = 100
	if loser_ratings < 10:
		lose_score = 240
	else:
		lose_score = 100
	
	
	prob = (1 / (1 + math.pow(10, ((loser_elo - winner_elo) / 400.0)))) 
	
	
	win_e = win_score - round(prob * win_score)
	lose_e = lose_score - round(prob * lose_score)
	
	e = round(prob * 1000) 
	calculation = {}
	calculation['winner_change'] = win_e
	calculation['loser_change'] = lose_e
	calculation['probability'] = e
	return calculation


