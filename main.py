import random
import time
import datetime
import os
from funcenter import cprint, fprint
from pygame import mixer

mixer.init()

game_over = False
month = 3
day = 1
miles_left = 2000
food = 500
health = 5
sick_days = [0, 0]
sick = False
out_of_food = False
win = False
reason = ""
dev = False

MIN_TRAVEL_DAYS = 3
MAX_TRAVEL_DAYS = 7
MIN_ACTIVITY_DAYS = 2
MAX_ACTIVITY_DAYS = 5
MIN_TRAVEL_MILES = 30
MAX_TRAVEL_MILES = 60
DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
TEXT_MONTHS = [
    '', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
    'August', 'September', 'October', 'November', 'December'
]

def parsePlaythrough(player):
    print('Parsing...')
    skip = False
    with open('saved-playthroughs.txt', 'r') as f:
        lines = f.readlines()
        readData = False
        for line in lines:
            print('Reading:', line)
            print('Skipping? ', skip)
            if readData:
                if 'Data:' not in line:
                    print(TEXT_MONTHS.index(line.split(':').strip()))
            else:
                if skip == False:
                    name = line.split(' - ')[0].split(':')[1].strip()
                    if player == name:
                        print('Found player.')
                        readData = True
                    print('Did not find player.', player, 'is not', name)
                    skip = True
                    print(skip)
                skip = False

def sfx(sound='positive'):
    if sound == 'positive':
        mixer.music.load('./assets/fail.mp3')
    elif sound == 'chirp':
        mixer.music.load('./assets/short-chirp.mp3')
    elif sound == 'flat':
        mixer.music.load('./assets/flat-beep.mp3')
    elif sound == 'fail':
        mixer.music.load('./assets/fail.mp3')
    mixer.music.play()


def clear():
    time.sleep(0.8)
    os.system('clear')


def loading():
    est_time = round(
        (random.randint(10, 20) / 10) + (random.randint(5, 9) / 10) +
        (random.randint(5, 9) / 10) + (random.randint(5, 9) / 10) +
        (random.randint(5, 9) / 10), 2)
    loading_msg = [
        'Loading assets...', 'Loading variables...',
        'Loading saved playthroughs...', 'Loading...'
    ]
    print('\n' * 3)
    fprint('bold', '----------------------------------------')
    cprint('red',
           "↻ Loading... Estimated runtime: {0} seconds.".format(est_time))
    time.sleep(random.randint(10, 15) / 10)
    for i in range(0, 4):
        time.sleep(0.9)
        cprint('italic', '  $ ~> ' + loading_msg[i])
    time.sleep(0.9)
    cprint('green', "✓ Loading complete.")
    fprint('bold', '----------------------------------------\n')


def set_sick_days():
    global sick_days
    sick_days[0] = random.randint(1, DAYS_IN_MONTH[month])
    sick_days[1] = random.randint(1, DAYS_IN_MONTH[month])
    while sick_days[0] == sick_days[1]:
        sick_days[1] = random.randint(1, DAYS_IN_MONTH[month])
    if dev:
        fprint(
            'bold', "You will get sick on {0}/{1} and {2}/{3}.".format(
                month, sick_days[0], month, sick_days[1]))


def status():
    global TEXT_MONTHS, month, day, miles_left, health, food
    print('''    MONTH: \033[1m{0}\033[0;37m
    DAY: \033[1m{1}\033[0;37m
    MILES LEFT: \033[0;32m{2}\033[0;37m
    HEALTH: \033[0;31m{3}\033[0;37m
    FOOD: \033[0;33m{4}\033[0;37m lbs'''.format(TEXT_MONTHS[month], day,
                                                miles_left, health, food))


def status_check():
    global game_over, reason, win
    if health == 0:
        game_over = True
        reason = "You died of tetanus!"
    if month == 12 and is_last_day():
        game_over = True
        reason = "You ran out of time!"
    if out_of_food:
        game_over = True
        reason = "You ran out of food!"
    if miles_left == 0:
        win = True
        game_over = True


def is_last_day():
    global day, month, DAYS_IN_MONTH
    if day == DAYS_IN_MONTH[month]:
        return True
    else:
        return False


def next_day():
    global day, month, sick_days, DAYS_IN_MONTH, health, food, sick, out_of_food
    if day in sick_days:
        health -= 1
        if health == 1:
            if dev:
                cprint('red', "You are on your last health point!")
                sfx('flat')
        if not sick:
            cprint('red', "You got sick and lost some health.")
            sfx('flat')
            sick = True
    if food != 0:
        food -= 5
    else:
        out_of_food = True
    if 30 < food < 100:
        if dev:
            cprint('yellow', "You are running low on food!")
            sfx('flat')
    if is_last_day():
        day = 1
        month += 1
        set_sick_days()
    else:
        day += 1


def advance_game_clock(days_to_advance):
    global month, day, sick
    i = 0
    sick = False
    while i != days_to_advance:
        next_day()
        status_check()
        if game_over or win:
            break
        else:
            i += 1
    sick = False


def travel():
    global miles_left, month, day
    distance = random.randint(MIN_TRAVEL_MILES, MAX_TRAVEL_MILES)
    if miles_left <= distance:
        distance = miles_left
    miles_left -= distance
    travel_days = random.randint(MIN_TRAVEL_DAYS, MAX_TRAVEL_DAYS)
    if month == 12:
        if day + travel_days == DAYS_IN_MONTH[month]:
            travel_days = DAYS_IN_MONTH[month] - day
    advance_game_clock(travel_days)
    if not game_over:
        sfx('positive')
        print(
            " ! You have traveled \033[0;32m{0}\033[0;37m miles in \033[1m{1}\033[0m days. It is now \033[1m{2}/{3}\033[0m, with \033[0;32m{4}\033[0;37m miles left."
            .format(distance, travel_days, month, day, miles_left))


def rest():
    global health, month, DAYS_IN_MONTH, day
    rest_days = random.randint(MIN_ACTIVITY_DAYS, MAX_ACTIVITY_DAYS)
    if month == 12:
        if day + rest_days == DAYS_IN_MONTH[month]:
            rest_days = DAYS_IN_MONTH[month] - day
    advance_game_clock(rest_days)
    if health != 5:
        health += 1
        cprint(
            'magenta',
            "You have rested for {0} days and gained some health. It is now {1}/{2}."
            .format(rest_days, month, day))
    else:
        cprint(
            'magenta',
            "You have rested for {0} days, but you were already at maximum health. It is now {1}/{2}."
            .format(rest_days, month, day))
    sfx('chirp')


def hunt():
    global food, month, DAYS_IN_MONTH, day
    hunt_days = random.randint(MIN_ACTIVITY_DAYS, MAX_ACTIVITY_DAYS)
    if month == 12:
        if day + hunt_days == DAYS_IN_MONTH[month]:
            hunt_days = DAYS_IN_MONTH[month] - day
    advance_game_clock(hunt_days)
    food += 100
    cprint(
        'magenta',
        "You have hunted for {0} days and gained some food. It is now {1}/{2}."
        .format(hunt_days, month, day))
    sfx('chirp')


def help():
    cprint('blue',
           "Try these commands: Travel, rest, hunt, status, help, or quit.")


def turn():
    action = input("\nSelect an action: ")
    if action in ['travel', 't']:
        travel()
    elif action in ['rest', 'r']:
        rest()
    elif action in ['hunt', 'h']:
        hunt()
    elif action in ['status', 's']:
        status()
    elif action in ['help', '?']:
        help()
    elif action == 'quit':
        pass

now = datetime.datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
clear()
loading()
cprint('bold', "Welcome to Oregon Trail!")
name = input("\033[1mWhat is your name?\033[0m ").capitalize()
cprint('bold', "\nNice to meet you, {0}!".format(name))
clear()
difficulty = input(
    "\033[1mChoose a difficulty: easy, medium, or hard:\033[0m ")
print(
    "You have chosen \033[0;94m{0}\033[1m\033[0m. Here are your instructions:\n"
    .format(difficulty))
if difficulty == 'easy' or difficulty == '$dev=true':
    MIN_TRAVEL_MILES = 50
    MAX_TRAVEL_MILES = 100
    MIN_TRAVEL_DAYS = 3
    MAX_TRAVEL_DAYS = 5
    MIN_ACTIVITY_DAYS = 1
    MAX_ACTIVITY_DAYS = 4
    if difficulty == '$dev=true':
        cprint('red', "Dev mode enabled.")
        dev = True
elif difficulty == 'hard':
    MIN_TRAVEL_MILES = 20
    MAX_TRAVEL_MILES = 50
    MIN_TRAVEL_DAYS = 5
    MAX_TRAVEL_DAYS = 8
    MIN_ACTIVITY_DAYS = 3
    MAX_ACTIVITY_DAYS = 6
else:
    if difficulty not in ['medium', 'easy', 'hard']:
        cprint('italic', "Invalid difficulty. Defaulting to medium.")
    MIN_TRAVEL_MILES = 30
    MAX_TRAVEL_MILES = 60
    MIN_TRAVEL_DAYS = 3
    MAX_TRAVEL_DAYS = 7
    MIN_ACTIVITY_DAYS = 2
    MAX_ACTIVITY_DAYS = 5
print('''It is March 1st. You have until December 31st to reach Oregon.
You have \033[0;31m5\033[0;37m health and \033[0;33m500\033[0;37m pounds of food.
You can get \033[0;33mfood\033[0;37m by hunting.
You can lose the game by running out of \033[0;33mfood\033[0;37m, health\033[0;37m, or time.
You can win the game by \033[0;32mmaking it to Oregon\033[0;37m.
You can quit the game at any time.
Good luck!
''')
set_sick_days()
while not game_over:
    turn()
if win:
    cprint(
        'green', "Congratulations {0}! You made it to Oregon!".format(
            name))
else:
    cprint('red', "Nice try {0}!".format(name))
    sfx()
    print(reason)
print('Here is your status report:')
status()
with open('saved-playthroughs.txt', 'a') as f:
    f.write(('Player: ' + name + ' - ' + dt_string))
    f.write('\nData: \n')
    f.write(''' - MONTH: {0}
 - DAY: {1}
 - MILES LEFT: {2}
 - HEALTH: {3}
 - FOOD: {4} lbs'''.format(TEXT_MONTHS[month], day, miles_left, health, food))
    f.write('\n - Win: ' + str(win) + '\n')
print("Thanks for playing!")