# -*- coding: utf-8 -*-

import bottle
import random
SNAKE_ID = '3d2f2b54-6c65-402f-b1ea-75b72d2ccbfb'


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        'color': '#717171',
        'head': head_url
    }


@bottle.post('/start')
def start():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': _get_trump_taunt()
    }


@bottle.post('/move')
def move():
    data = bottle.request.json
    snakes = data['snakes']
    snake = None

    for snake in snakes:
        if snake['id'] == SNAKE_ID:
            snake = snake

    # If snake is hungry, priority is food
    # Only ever go for food or go for gold
    gold_priority = True
    if _snake_is_hungry(snake):
        gold_priority = False

    move = _get_best_move(data, snake, gold_priority)

    response = {
        'move': move,
    }
    if data['turn'] % 4 == 0:
        response['taunt'] = _get_trump_taunt(snakes)

    return response


@bottle.post('/end')
def end():

    return {
        'taunt': _get_trump_taunt()
    }


def _snake_is_hungry(snake):
    return snake['health'] < 101


def _get_direction_to_target(snake, target_coords, head_position):
    move = 'north'
    body_coord = snake['coords'][1]

    if target_coords[0] < head_position[0]:
        if not body_coord[0] < head_position[0]:
            move = 'west'
    elif target_coords[0] > head_position[0]:
        if not body_coord[0] > head_position[0]:
            move = 'east'
    elif target_coords[1] < head_position[1]:
        if not body_coord[1] < head_position[1]:
            move = 'north'
    elif target_coords[1] > head_position[1]:
        if not body_coord[1] > head_position[1]:
            move = 'south'
    return move


def _get_best_move(data, snake, gold_priority):
    head_position = snake['coords'][0]
    # Priority is food
    if not gold_priority:
        food_coords = data['food']
        # Find closest food
        try:
            if food_coords:
                distance_x = abs(head_position[0] - food_coords[0][0])
                distance_y = abs(head_position[1] - food_coords[0][1])
                # [TOTAL_DISTANCE, COORDS]
                closest = [distance_x + distance_y, food_coords[0]]
                # Don't check the first element since that is set to closest as default
                for coords in food_coords[1:]:
                    food_distance = abs(head_position[0] - coords[0]) + abs(head_position[1] - coords[1])
                    if food_distance < closest[0]:
                        print 'FOUND NEW CLOSEST FOOD'
                        closest = [food_distance, coords]
        except IndexError as e:
            print e
            # That list of food was was less than 1 food!
            gold_priority = True
        else:
            print 'NO FOOD, GO NORTH'
            return 'north'
            move = _get_direction_to_target(snake, closest[1], head_position)
    return move

    # Priority is gold
        # Gold exists on the board
        # Gold does not exist on the board


def _get_trump_taunt(snakes=None):
    if not snakes:
        return 'I promise I will never be in a snake competition'

    # Dont make fun of ourselves..
    other_snakes = []
    for snake in snakes:
        if not snake['id'] == SNAKE_ID:
            other_snakes.append(snake)

    name = random.choice(other_snakes)['name']

    quotes = [
        'My net worth is many, many times that of %s\'s' % name,
        'I want to see %s\'s birth certificate' % name,
        'Did anyone notice %s was crying through my speech?' % name,
        'Why is %s playing basketball today' % name,
        'All of the snakes on the board flirted with me',
        'Global warming was invented by the mongooses'
    ]

    return random.choice(quotes)


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host='127.0.0.1', port=8080)
