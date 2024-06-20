import sys
import random
import os
from enum import Enum
from datetime import datetime
import logging
from log import log
import csv

class Bet(Enum):
    BANKER = "Banker"
    PLAYER = "Player"
    TIE = "Tie"
    TIGER7 = "Tiger 7"
    OX6 = "Ox 6"
    KILLBONUS = "Kill Bonus"

def deal_card() -> int:
  card = random.randint(2, 11)
  return card % 10

def calculate_hand(hand: [int]) -> int:
  return sum(hand) % 10

# Simulate single round of Dai Bacc
def play_hand() -> Bet:
  player_hand = [deal_card(), deal_card()]
  banker_hand = [deal_card(), deal_card()]
  player_hand_total = calculate_hand(player_hand)
  banker_hand_total = calculate_hand(banker_hand)

  # Check for natural wins (8 or 9 totals on first two cards)
  if player_hand_total > 7 or banker_hand_total > 7:
    if player_hand_total > banker_hand_total:
      log.info("Player")
      return Bet.PLAYER
    elif player_hand_total < banker_hand_total:
      log.info("Banker")    
      return Bet.BANKER
    else: 
      log.info("Tie")
      return Bet.TIE

  # Player stands on 6 or 7
  # Banker stands on 7
  # Player draws on any total less than 6
  # If Player draws, Banker onlys draw on less than 7 following rules below
  player_card = None
  banker_card = None
  if player_hand_total == 6 or player_hand_total == 7:
    if banker_hand_total < 6:
      banker_card = deal_card()
      banker_hand.append(banker_card)
  elif player_hand_total < 6:
    player_card = deal_card()
    player_hand.append(player_card)
    match banker_hand_total:
        case 0 | 1 | 2:
            banker_card = deal_card()
            banker_hand.append(banker_card)
        case 3:
            if player_card != 8:
              banker_card = deal_card()
              banker_hand.append(banker_card)
        case 4:
            if player_card in [2, 3, 4, 5, 6, 7]:
              banker_card = deal_card()
              banker_hand.append(banker_card)
        case 5:
            if player_card in [4, 5, 6, 7]:
              banker_card = deal_card()
              banker_hand.append(banker_card)
        case 6:
            if player_card in [6, 7]:
              banker_card = deal_card()
              banker_hand.append(banker_card)

  if not (player_card is None):
    player_hand_total = calculate_hand(player_hand)
  if not (banker_card is None):
    banker_hand_total = calculate_hand(banker_hand)

  log.debug(f"Player: TotalValue={player_hand_total} 3rdCard={player_card} TotalCards={len(player_hand)}")
  log.debug(f"Banker: TotalValue={banker_hand_total} 3rdCard={banker_card} TotalCards={len(banker_hand)}")

  # Determine winner
  if player_hand_total > banker_hand_total and len(player_hand) == 3 and player_hand_total == 6:
    log.info("OX6")
    return Bet.OX6
  elif player_hand_total > banker_hand_total:
    log.info("Player")
    return Bet.PLAYER
  # Dai Bacc: Tie bet when and banker card total is 3 and banker hand total is 7 
  elif player_hand_total < banker_hand_total and len(banker_hand) == 3 and banker_hand_total == 7:
    log.info("Tiger7")
    return Bet.TIGER7
  elif player_hand_total < banker_hand_total:
    log.info("Banker")
    return Bet.BANKER
  else:
    log.info("Tie")
    return Bet.TIE

def strat1(history):
  strat1 = [1, 3, 2, 4]
  strat2 = [1, 1, 1, 1]
  return 0

def run_simulation(strat_label: str, bank_roll: int, total_hands: int, unit_bet: int, bet: Bet) -> None:
  win_stats = { 'player': 0, 'banker': 0, 'tie': 0, 'ox6': 0, 'tiger7': 0 }
  bet_amount = unit_bet

  # Simulate playing hands
  hand_count = 0
  largest_bank_roll_iteration = 0
  largest_bank_roll = bank_roll
  bet_index = 0
  strat = [1, 3, 2, 4]
  while hand_count < total_hands:
    if bank_roll < (unit_bet * 4):
      break

    result = play_hand()
    #if hand_count == 0:
    #  bet_amount = bank_roll * .5
    #else:
    bet_amount = strat[bet_index] * unit_bet
    bank_roll, win_stats = resolve_outcome(result, bet, bet_amount, bank_roll, win_stats)

    if result == bet:
     if bet_index < 3:
       bet_index += 1
     else:
      bet_index = 0
    else:
      bet_index = 0
    
    if bank_roll > largest_bank_roll:
      largest_bank_roll = bank_roll
      largest_bank_roll_iteration = hand_count
    
    hand_count += 1

  data = [strat_label, bank_roll, hand_count, largest_bank_roll, largest_bank_roll_iteration, win_stats['player'], win_stats['banker'], win_stats['tie'], win_stats['ox6'], win_stats['tiger7']]
  csv_filename = datetime.now().strftime("stats_%Y_%m_%d.csv")
  csvfile = "./" + csv_filename
  if not os.path.exists(csvfile):
    with open(csvfile, 'w') as file:
      writer = csv.writer(file)
      writer.writerow(['Strategy', 'Final Bank Roll', 'Iterations', 'Largest Bank Roll','Largest Bank Roll Iteration', 'Player', 'Banker', 'Tie', 'Ox6', 'Tiger7'])
      writer.writerow(data)
  else:
    with open(csvfile, 'a', newline='') as file:
      writer = csv.writer(file)
      writer.writerow(data)


  print(f"########### STATS ###########")
  print(f"Bet count: {hand_count}")
  print(f"Player Win Total: {win_stats['player']}")
  print(f"Banker Win Total: {win_stats['banker']}")
  print(f"Tie Win Total: {win_stats['tie']}")
  print(f"Largest Bank Roll: {largest_bank_roll}")
  print(f"Largest Bank Roll Iteration: {largest_bank_roll_iteration}")
  print(f"Current Bank Roll: {bank_roll}")

def resolve_outcome(result: Bet, bet: Bet, bet_amount: int, bank_roll: int, win_stats: dict) -> tuple[int, dict]:
  if result == Bet.OX6:
    win_stats['ox6'] += 1
    win_stats['player'] += 1
    if (bet == Bet.OX6):
      bank_roll = bank_roll + (40 * bet_amount)
    elif (bet == Bet.PLAYER):
      bank_roll = bank_roll + bet_amount
    else:
      bank_roll = bank_roll - bet_amount
  elif result == Bet.PLAYER:
    win_stats['player'] += 1
    if (bet == Bet.PLAYER):
      bank_roll = bank_roll + bet_amount
    else:
      bank_roll = bank_roll - bet_amount
  elif result == Bet.BANKER:
    win_stats['banker'] += 1
    if (bet == Bet.BANKER):
      bank_roll = bank_roll + bet_amount
    else:
      bank_roll = bank_roll - bet_amount
  elif result == Bet.TIGER7: # Tiger 7 considered a Banker push
    win_stats['tiger7'] += 1
    if (bet == Bet.TIGER7):
      bank_roll = bank_roll + (40 * bet_amount)
  elif result == Bet.TIE:
    win_stats['tie'] += 1
    if (bet == Bet.TIE):
      bank_roll = bank_roll + (8 * bet_amount)
  
  return bank_roll, win_stats


# Example Usage: python3 sim.py play_dai_bacc strat1 5000 2000 50 player
if __name__ == "__main__":
  log = log("sim", level=logging.INFO)

  if len(sys.argv) > 2:
    func_name = sys.argv[1]
    args = sys.argv[2:]
  
    if func_name == "play_dai_bacc":
      if len(args) == 5:
        try:
          strat_label = str(args[0])
        except ValueError:
          log.error("Parameter strat_label must be a string")
          raise TypeError("Parameter strat_label must be an string")             
        try:
          bank_roll = int(args[1])
        except ValueError:
          log.error("Parameter bank_roll must be an integer")
          raise TypeError("Parameter bank_roll must be an integer")
        try:
          total_hands = int(args[2])
        except ValueError:
          log.error("Parameter total_hands must be an integer")
          raise TypeError("Parameter total_hands must be an integer")
        try:
          unit_bet = int(args[3])
        except ValueError:
          log.error("Parameter unit_bet must be an integer")
          raise TypeError("Parameter unit_bet must be an integer")
        try:
          bet_temp = str(args[4]).lower()
          bet = Bet
          if bet_temp == 'player' or bet_temp == 'p':
            bet = Bet.PLAYER
          elif bet_temp == 'banker' or bet_temp == 'b':
            bet = Bet.BANKER
          else:
            log.error("Parameter bet must be a valid value")
            raise ValueError("Parameter bet must one of the following strings: 'player', 'p', 'banker', 'b'")
        except TypeError:
          log.error("Parameter bet must be an string")
          raise TypeError("Parameter bet must be an string")
        run_simulation(strat_label=strat_label, bank_roll=bank_roll, total_hands=total_hands, unit_bet=unit_bet, bet=Bet.PLAYER)
      else:
        print("Usage: python3 sim.py play_dai_bacc [strat_label] [bank_roll] [total_hands] [unit_bet] ['player' or 'banker']")
    else:
      print("Function not found")
  else:
    print("Please provide a function name as a command-line argument")