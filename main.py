# Imports
import pygame as pg
import random
import numpy as np
import time
np.random.seed(0)
random.seed = 0

# Gameplay variables
N_SAMPLES = 7
N_LEVELS = 11
HAND_SIZE = 5
STARTING_SIGNIFICANCE = 4
N_RESEARCHERS = 2

START_POSITIONS = [0, 2, 4, 5, 6, 8, 10]
DIE_SIDES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
sample_cols = [chr(65 + x) for x in range(N_SAMPLES)]
researcher_names = ['Red', 'Blue']

N_CARDS_BY_CATEGORY = {
    'rounding': 30,
    'contaminated': 10,
    'outlier': 10,
    'swap': 10,
    'audit': 10,
    'copy': 5,
    'challenge': 5,
    'significance': 2
}

# display variables
SCREEN_CAPTION = 'p-hacking'
SCREEN_HEIGHT = 750
SCREEN_WIDTH = 1400

INTRO_SCREEN_RGB = (51, 204, 204)
SCREEN_RGB = (154, 182, 60)
AXIS_LABELS_RGB = (0, 0, 0)
BOXES_RGB = (255, 255, 255)
HIGHLIGHT_BOXES_RGB = (251, 202, 16)
RESEARCHER_RGBS = [(255, 0, 0), (0, 0, 255)]
SIGNIFICANCE_LEVEL_RGB = (0, 0, 0)

CARD_DIMS = (100, 150)
PILE_DIMS = (150, 210)

GAME_ICON_PATH = 'assets/phacking_logo_v1.jpg'
DRAW_PILE_PATH = 'assets/draw_pile.png'
SOUND_PATH = 'assets/explosion.wav'

FONT_SIZE = 32
DESCRIPTION_FONT_SIZE = 20
NOTIFICATION_FONT_SIZE = 24
SCORE_FONT_SIZE = 36
GAME_END_TITLE_FONT_SIZE = 64
GAME_END_DETAIL_FONT_SIZE = 32
FONT_FILE = 'freesansbold.ttf'

# Positioning variables
BUFFER_SIZE_GRID = 10
BUFFER_SIZE_HAND = 5
SQUARE_SIZE_GRID = 30
BUFFER_SIZE_DEFAULT = 10
LEFT_BUFFER_SIZE = 20
UPPER_BUFFER_SIZE = 30
SIG_LEVEL_DX = 90
NOTIF_DX = 150
DRAW_PILE_DY = 180
HANDS_DY = 50

# Compute positions of objects
YAXIS_CENTER_X = LEFT_BUFFER_SIZE + FONT_SIZE / 2
YTICKS_CENTER_X = YAXIS_CENTER_X + 2 * FONT_SIZE
GRID_LEFT_X = YTICKS_CENTER_X + FONT_SIZE
XAXIS_A_CENTER_X = GRID_LEFT_X + (N_SAMPLES / 2) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID)
XAXIS_B_CENTER_X = GRID_LEFT_X + (N_SAMPLES * 3 / 2 + 1) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID)
SIGLEVEL_LABEL_X = GRID_LEFT_X + (N_SAMPLES * 2 + 2) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) + SIG_LEVEL_DX
DESCRIPTION_X = SIGLEVEL_LABEL_X + NOTIF_DX
DRAW_PILE_X = SIGLEVEL_LABEL_X - int(PILE_DIMS[0] / 2)
HANDS_X = LEFT_BUFFER_SIZE
NOTIF_X = 1000

YAXIS_CENTER_Y = UPPER_BUFFER_SIZE + (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) * (N_LEVELS / 2)
XTICKS_CENTER_Y = UPPER_BUFFER_SIZE + (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) * (N_LEVELS + .5)
XAXIS_CENTER_Y = XTICKS_CENTER_Y + (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) * 1
SIGLEVEL_LABEL_Y = UPPER_BUFFER_SIZE + int(FONT_SIZE / 2)
DRAW_PILE_Y = SIGLEVEL_LABEL_Y + SQUARE_SIZE_GRID + DRAW_PILE_DY
DESCRIPTION_Y = SIGLEVEL_LABEL_Y + 5 * FONT_SIZE
HANDS_Y = XAXIS_CENTER_Y + HANDS_DY

# Short-term notifications
N_SECONDS_NOTIFICATION = 1.5
ACTION_NOTIFS = {
    'copy': "You are copying your opponent's last move",
    'challenge': "You undid your opponent's last move",
    'significance': 'The significance threshold decreased',
}

# Turn phase descriptions
TURN_PHASE_NOTIFS = {
    'draw': 'Draw a card',
    'choose_card': 'Choose a card to play',
    'choose_sample': 'Choose a sample to manipulate',
    'card_effect': '',
    'notify': '',
}

# Game context options
CONTEXTS = [
    ('cancer-curing ability', ('dark chocolate', 'milk chocolate')),
    ('refreshingness', ('Coke', 'Pepsi')),
    ('cuteness', ('dogs', 'cats')),
    ('intelligence level', ('Democrats', 'Republicans')),
    ('tastiness', ('Chipotle', 'Taco Bell')),
    ('user satisfaction', ('iOS', 'Android')),
    ('level of fake news', ('Facebook', 'Twitter'))
]

# initialize the game and display
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption(SCREEN_CAPTION)
pg.display.set_icon(pg.image.load(GAME_ICON_PATH))
font = pg.font.Font(FONT_FILE, FONT_SIZE)

# Draw board
def display_board(game_context, draw_deck):

    # Display axes labels
    text = font.render(game_context[0], True, AXIS_LABELS_RGB)
    text = pg.transform.rotate(text, 90)
    text_rect = text.get_rect(center=(YAXIS_CENTER_X, YAXIS_CENTER_Y))
    screen.blit(text, text_rect)

    text = font.render(game_context[1][0], True, AXIS_LABELS_RGB)
    text_rect = text.get_rect(center=(XAXIS_A_CENTER_X, XAXIS_CENTER_Y))
    screen.blit(text, text_rect)

    text = font.render(game_context[1][1], True, AXIS_LABELS_RGB)
    text_rect = text.get_rect(center=(XAXIS_B_CENTER_X, XAXIS_CENTER_Y))
    screen.blit(text, text_rect)

    # Label y-axis levels
    for level_num in range(N_LEVELS-1, -1, -1):
        level_label_blit = font.render(str(level_num), True, AXIS_LABELS_RGB)
        text_rect = level_label_blit.get_rect(center=(YTICKS_CENTER_X,
                                                      UPPER_BUFFER_SIZE + (N_LEVELS - .5 - level_num) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID)))
        screen.blit(level_label_blit, text_rect)

    # Label x-axis columns
    for sample_num, sample_letter in enumerate(sample_cols):
        level_label_blit = font.render(sample_letter, True, AXIS_LABELS_RGB)
        text_rect = level_label_blit.get_rect(center=(GRID_LEFT_X + (sample_num) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) + (.5 * SQUARE_SIZE_GRID),
                                                      XTICKS_CENTER_Y))
        screen.blit(level_label_blit, text_rect)

        # Population B
        text_rect = level_label_blit.get_rect(center=(GRID_LEFT_X + (N_SAMPLES + 1 + sample_num) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) + (.5 * SQUARE_SIZE_GRID),
                                                      XTICKS_CENTER_Y))
        screen.blit(level_label_blit, text_rect)

    # Create grids of boxes
    for sample_num in range(N_SAMPLES):
        for level_num in range(N_LEVELS):
            for researcher_i in range(N_RESEARCHERS):
                # Determine if box is highlighted
                if START_POSITIONS[sample_num] == level_num:
                    box_color = HIGHLIGHT_BOXES_RGB
                else:
                    box_color = BOXES_RGB
                x_left = GRID_LEFT_X + ((N_SAMPLES + 1) * researcher_i + sample_num) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID)
                y_top = UPPER_BUFFER_SIZE + (N_LEVELS - 1 - level_num) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID)
                pg.draw.rect(screen, box_color, pg.Rect(x_left, y_top, SQUARE_SIZE_GRID, SQUARE_SIZE_GRID))

    # Significance level title
    text = font.render('Significance', True, AXIS_LABELS_RGB)
    text_rect = text.get_rect(center=(SIGLEVEL_LABEL_X, SIGLEVEL_LABEL_Y))
    screen.blit(text, text_rect)
    text = font.render('Level', True, AXIS_LABELS_RGB)
    text_rect = text.get_rect(center=(SIGLEVEL_LABEL_X, SIGLEVEL_LABEL_Y + FONT_SIZE))
    screen.blit(text, text_rect)

    # Significance level boxes
    all_sig_levels = list(range(STARTING_SIGNIFICANCE, STARTING_SIGNIFICANCE - N_CARDS_BY_CATEGORY['significance'] - 1, -1))
    for i_sig_lev, sig_lev in enumerate(all_sig_levels):
        # determine box color
        if i_sig_lev == 0:
            box_rgb = HIGHLIGHT_BOXES_RGB
        else:
            box_rgb = BOXES_RGB

        # draw box
        box_x = SIGLEVEL_LABEL_X - (.5 * SQUARE_SIZE_GRID)
        box_y = SIGLEVEL_LABEL_Y + SQUARE_SIZE_GRID * (2 + 1.5 * i_sig_lev)
        pg.draw.rect(screen, box_rgb, pg.Rect(box_x, box_y, SQUARE_SIZE_GRID, SQUARE_SIZE_GRID))

        # sig level # label
        level_label_blit = font.render(str(sig_lev), True, AXIS_LABELS_RGB)
        screen.blit(level_label_blit, (box_x - SQUARE_SIZE_GRID, box_y))

    # Draw pile
    if len(draw_deck) > 0:
        screen.blit(pg.transform.scale(pg.image.load(DRAW_PILE_PATH), PILE_DIMS), (DRAW_PILE_X, DRAW_PILE_Y))


def initialize_deck():
    all_cards = [[card_name] * n for card_name, n in N_CARDS_BY_CATEGORY.items()]
    all_cards = [x for y in all_cards for x in y]
    # return list(np.random.permutation(all_cards))
    return list(np.random.permutation(all_cards))


def deal_hands(draw_deck):
    researcher_hands = [[] for _ in range(N_RESEARCHERS)]
    for i in range(HAND_SIZE):
        for r in range(N_RESEARCHERS):
            researcher_hands[r].append(draw_deck.pop())
    return researcher_hands


def display_cards(researcher_hands):
    for r in range(N_RESEARCHERS):
        for card_i, card in enumerate(researcher_hands[r]):
            card_x = HANDS_X + card_i * (CARD_DIMS[0] + BUFFER_SIZE_HAND)
            if r == 1:
                card_x += (HAND_SIZE + 2) * (CARD_DIMS[0] + BUFFER_SIZE_HAND)
            screen.blit(pg.transform.scale(pg.image.load(f'assets/card_{card}.png'), CARD_DIMS), (card_x, HANDS_Y))


def display_samples(sample_values):
    for pop_i, pop in enumerate(sample_values):
        for samp_i, samp_value in enumerate(pop):
            circle_x = int(GRID_LEFT_X + (samp_i + (N_SAMPLES + 1)*pop_i) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) + (.5 * SQUARE_SIZE_GRID))
            circle_y = int(UPPER_BUFFER_SIZE + (N_LEVELS - 1 - samp_value) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) + (.5 * SQUARE_SIZE_GRID))
            pg.draw.circle(screen, RESEARCHER_RGBS[pop_i], [circle_x, circle_y],
                                                int(SQUARE_SIZE_GRID / 3), 0)


def display_significance(significance_value):
    circle_x = int(SIGLEVEL_LABEL_X)
    circle_y = int(SIGLEVEL_LABEL_Y + SQUARE_SIZE_GRID * (2.5 + 1.5 * (4 - significance_value)))
    pg.draw.circle(screen, SIGNIFICANCE_LEVEL_RGB, [circle_x, circle_y],
                   int(SQUARE_SIZE_GRID / 3), 0)


def display_description(description):
    font = pg.font.Font(FONT_FILE, DESCRIPTION_FONT_SIZE)
    text = font.render(description, True, AXIS_LABELS_RGB)
    screen.blit(text, (DESCRIPTION_X, DESCRIPTION_Y))


def draw_card(whose_turn, draw_deck, researcher_hands):
    researcher_hands[whose_turn].append(draw_deck.pop())


def execute_action(mouse, whose_turn, turn_phase, sample_values, current_action, last_action,
                   chosen_sample_researcher, chosen_sample, chosen_sample_val, click):
    done_action = True
    if current_action == 'rounding':
        if click[0] == 1:
            # If click above the current sample, increase current sample value by one; otherwise decrease
            current_sample_y = UPPER_BUFFER_SIZE + (N_LEVELS - 1 - chosen_sample_val) * (
            SQUARE_SIZE_GRID + BUFFER_SIZE_GRID)
            if mouse[1] < current_sample_y:
                sample_values[chosen_sample_researcher][chosen_sample] = min(chosen_sample_val + 1, N_LEVELS - 1)

            elif mouse[1] > current_sample_y + SQUARE_SIZE_GRID:
                sample_values[chosen_sample_researcher][chosen_sample] = max(chosen_sample_val - 1, 0)
            else:
                done_action = False
        else:
            done_action = False

    elif current_action == 'contaminated':
        sample_values[chosen_sample_researcher][chosen_sample] = 5

    elif current_action == 'outlier':
        sample_values[chosen_sample_researcher][chosen_sample] = random.randint(0,9)

    elif current_action == 'swap':
        sample_values[chosen_sample_researcher][chosen_sample], sample_values[1 - chosen_sample_researcher][
            chosen_sample] = sample_values[1 - chosen_sample_researcher][chosen_sample], \
                             sample_values[chosen_sample_researcher][chosen_sample]

    elif current_action == 'audit':
        sample_values[chosen_sample_researcher][chosen_sample] = START_POSITIONS[chosen_sample]

    elif current_action == 'copy':
        current_action = last_action
        turn_phase = 'notify'
        last_action = None
        done_action = False

    elif current_action == 'challenge':
        if last_action == 'swap':
            sample_values[chosen_sample_researcher][chosen_sample], sample_values[1 - chosen_sample_researcher][
                chosen_sample] = sample_values[1 - chosen_sample_researcher][chosen_sample], \
                                 sample_values[chosen_sample_researcher][chosen_sample]
            chosen_sample_researcher = 1 - chosen_sample_researcher
        else:
            old_sample_val = sample_values[chosen_sample_researcher][chosen_sample]
            sample_values[chosen_sample_researcher][chosen_sample] = chosen_sample_val
            chosen_sample_val = old_sample_val
        current_action = last_action
    else:
        raise ValueError(f'Cannot handle action {current_action}')

    if done_action:
        whose_turn = 1 - whose_turn
        turn_phase = 'draw'
        last_action = current_action
    return sample_values, chosen_sample_researcher, chosen_sample_val, current_action, turn_phase, last_action, whose_turn


# introduce score
def display_notification_and_score(whose_turn, turn_phase, current_action, low_score, high_score):
    font = pg.font.Font(FONT_FILE, NOTIFICATION_FONT_SIZE)
    if current_action == 'rounding' and turn_phase == 'card_effect':
        txt = font.render('Choose to round up or down', True, RESEARCHER_RGBS[whose_turn])
    else:
        txt = font.render(TURN_PHASE_NOTIFS[turn_phase], True, RESEARCHER_RGBS[whose_turn])
    screen.blit(txt, (NOTIF_X, UPPER_BUFFER_SIZE))

    font = pg.font.Font(FONT_FILE, SCORE_FONT_SIZE)
    if low_score[1] is None:
        low_score_txt = font.render('Lowest samples: TIE', True, BOXES_RGB)
    else:
        low_score_txt = font.render('Lowest samples: {}'.format(low_score[0]), True, RESEARCHER_RGBS[low_score[1]])
    screen.blit(low_score_txt, (NOTIF_X, UPPER_BUFFER_SIZE + int(SCORE_FONT_SIZE * 1.5)))

    if high_score[1] is None:
        high_score_txt = font.render('Highest samples: TIE', True, BOXES_RGB)
    else:
        high_score_txt = font.render('Highest samples: {}'.format(high_score[0]), True, RESEARCHER_RGBS[high_score[1]])
    screen.blit(high_score_txt, (NOTIF_X, UPPER_BUFFER_SIZE + int(SCORE_FONT_SIZE * 3)))


def compute_end_result(low_score, high_score, significance_value):
    # Determine game end result
    # If 1 researcher won each condition, no one wins, and a rematch is necessary
    if low_score[0] >= significance_value and high_score[0] >= significance_value:
        if low_score[1] != high_score[1]:
            game_result = 'conflicting_findings'
            game_winner = None
        else:
            game_result = 'conclusion'
            game_winner = high_score[1]

    elif low_score[0] < significance_value and high_score[0] < significance_value:
        # If no one reached significance threshold, then both lose
        game_result = 'null_result'
        game_winner = None

    else:
        # If 1 researcher won one or both conditions, they win
        if high_score[0] >= significance_value:
            game_result = 'conclusion'
            game_winner = high_score[1]
        else:
            game_result = 'conclusion'
            game_winner = 1 - low_score[1]
    return game_result, game_winner


def display_end_screen(low_score, high_score, significance_value, game_context):
    game_result, game_winner = compute_end_result(low_score, high_score, significance_value)

    screen.fill(SCREEN_RGB)
    title_font = pg.font.Font('freesansbold.ttf', GAME_END_TITLE_FONT_SIZE)
    reg_font = pg.font.Font('freesansbold.ttf', GAME_END_DETAIL_FONT_SIZE)
    if game_result == 'conclusion':
        txt = title_font.render(f'Researcher {researcher_names[game_winner]} wins!', True, RESEARCHER_RGBS[game_winner])
        text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 100))
        screen.blit(txt, text_rect)
        txt = reg_font.render(f'Concerning {game_context[0]}:', True, (255, 255, 255))
        text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 200))
        screen.blit(txt, text_rect)
        if game_context[1][0][-1] == 's' and game_context[1][1][-1] == 's':
            tobe = 'are'
        else:
            tobe = 'is'
        txt = reg_font.render(f'{game_context[1][game_winner]} {tobe} greater than {game_context[1][1-game_winner]}', True, (255, 255, 255))
        text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 250))
        screen.blit(txt, text_rect)
        txt = reg_font.render(f"Significance level: {'*'*significance_value}", True, (255, 255, 255))
        text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 300))
        screen.blit(txt, text_rect)

    elif game_result == 'null_result':
        txt = title_font.render(f'NULL Result!', True, (255, 255, 255))
        text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 100))
        screen.blit(txt, text_rect)

    elif game_result == 'conflicting_findings':
        txt = title_font.render(f'Conflicting findings!', True, (255, 255, 255))
        text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 100))
        screen.blit(txt, text_rect)

    else:
        raise ValueError(f'Unknown game result {game_result}')


    # Press space to restart
    txt = title_font.render('Press SPACE to return to home screen', True, (255, 255, 255))
    text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), SCREEN_HEIGHT - 100))
    screen.blit(txt, text_rect)


def display_welcome_screen():
    screen.fill(INTRO_SCREEN_RGB)
    screen.blit(pg.transform.scale(pg.image.load(GAME_ICON_PATH), (300,300)), ((SCREEN_WIDTH / 2 - 150), 50))

    font = pg.font.Font('freesansbold.ttf', 48)
    txt = font.render('p-hacking: The board game', True, (255, 255, 255))
    text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 400))
    screen.blit(txt, text_rect)

    font = pg.font.Font('freesansbold.ttf', 36)
    txt = font.render('Read rules at bit.ly/phackingrules', True, (0, 0, 0))
    text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 500))
    screen.blit(txt, text_rect)

    font = pg.font.Font('freesansbold.ttf', 36)
    txt = font.render('Instructional video', True, (0, 0, 0))
    text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 550))
    screen.blit(txt, text_rect)

    font = pg.font.Font('freesansbold.ttf', 48)
    txt = font.render('PRESS SPACE TO BEGIN', True, (255, 255, 255))
    text_rect = txt.get_rect(center=(int(SCREEN_WIDTH / 2), 650))
    screen.blit(txt, text_rect)


def compute_high_score(sample_values):
    return compute_score(range(N_LEVELS-1, -1, -1), sample_values)


def compute_low_score(sample_values):
    return compute_score(range(N_LEVELS), sample_values)


def compute_score(my_range, sample_values):
    n_samples_low = [0, 0]
    n_samples_proposed = [0, 0]
    for v in my_range:
        for r in range(2):
            n_samples_proposed[r] += sum([val==v for val in sample_values[r]])

        if min(n_samples_proposed) == 0:
            n_samples_low = [n_samples_proposed[0], n_samples_proposed[1]]
        else:
            if n_samples_low[0] == n_samples_low[1]:
                return (0, None)
            elif n_samples_low[0] == 0:
                return (n_samples_low[1], 1)
            else:
                return (n_samples_low[0], 0)


def run():
    # Initialize game system
    running = True
    game_state = 'ready'
    while running:
        if game_state == 'ready':
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        game_state = 'playing'

                        # Initialize game
                        draw_deck = initialize_deck()
                        researcher_hands = deal_hands(draw_deck)
                        turn_phase = 'draw'
                        whose_turn = 0
                        game_context = CONTEXTS[random.randint(0, len(CONTEXTS) - 1)]
                        sample_values = [[START_POSITIONS[i_s] for i_s in range(N_SAMPLES)] for n in range(N_RESEARCHERS)]
                        significance_value = STARTING_SIGNIFICANCE

                        description = None
                        current_action = None
                        last_action = None
                        notify_time = None
                        not_played_sound = True

            display_welcome_screen()

        elif game_state == 'playing':

            # Respond to keystrokes
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            # Check mouse click
            mouse = pg.mouse.get_pos()
            click = pg.mouse.get_pressed()

            # Effect of chosen card
            if turn_phase == 'card_effect':
                sample_values, chosen_sample_researcher, chosen_sample_val, current_action, turn_phase, last_action, whose_turn = \
                            execute_action(mouse, whose_turn, turn_phase, sample_values, current_action, last_action,
                                           chosen_sample_researcher, chosen_sample, chosen_sample_val, click)

            # Sample choice phase
            if turn_phase == 'choose_sample':
                if click[0] == 1 and mouse[1] < XTICKS_CENTER_Y:
                    # Determine the sample that was chosen
                    for researcher_i in range(2):
                        for sample_i, sample_val in enumerate(sample_values[researcher_i]):
                            sample_left_x = GRID_LEFT_X + sample_i * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID) + \
                                            (researcher_i * ((N_SAMPLES + 1) * (SQUARE_SIZE_GRID + BUFFER_SIZE_GRID)))
                            if sample_left_x < mouse[0] < (sample_left_x + SQUARE_SIZE_GRID):
                                chosen_sample = sample_i
                                chosen_sample_val = sample_val
                                chosen_sample_researcher = researcher_i
                                turn_phase = 'card_effect'
                                break

            # Post notification for significance, copy, or challenge
            if turn_phase == 'notify':
                if current_action in ['significance', 'copy', 'challenge']:
                    if notify_time is None:
                        notify_time = time.time()
                        description = ACTION_NOTIFS[current_action]
                    else:
                        if time.time() - notify_time > N_SECONDS_NOTIFICATION:
                            notify_time = None
                            description = ''
                            if current_action == 'significance':
                                significance_value -= 1
                                turn_phase = 'draw'
                                whose_turn = 1 - whose_turn
                            elif current_action in ['copy', 'challenge']:
                                turn_phase = 'card_effect'
                else:
                    turn_phase = 'choose_sample'

            # Choose card phase
            if turn_phase == 'choose_card' and click[0] == 1:
                # Check if the mouse press was in the cards row:
                if HANDS_Y < mouse[1] < (HANDS_Y + CARD_DIMS[1]):
                    # Check if any of the researcher's cards were clicked
                    for card_i, card in enumerate(researcher_hands[whose_turn]):
                        card_x = HANDS_X + card_i * (CARD_DIMS[0] + BUFFER_SIZE_HAND)
                        if whose_turn == 1:
                            card_x += 7 * (CARD_DIMS[0] + BUFFER_SIZE_HAND)

                        if card_x < mouse[0] < (card_x + CARD_DIMS[0]):
                            researcher_hands[whose_turn].pop(card_i)
                            current_action = card
                            turn_phase = 'notify'
                            break

            # Draw phase
            if turn_phase == 'draw':
                if len(draw_deck) == 0:
                    turn_phase = 'choose_card'
                else:
                    clicked_draw_pile = click[0] == 1 and DRAW_PILE_X < mouse[0] < (
                        DRAW_PILE_X + PILE_DIMS[0]) and DRAW_PILE_Y < mouse[1] < (DRAW_PILE_Y + PILE_DIMS[1])
                    if clicked_draw_pile:
                        draw_card(whose_turn, draw_deck, researcher_hands)
                        turn_phase = 'choose_card'

            # Compute scores
            low_score = compute_low_score(sample_values)
            high_score = compute_high_score(sample_values)

            # End game check
            if low_score[0] >= significance_value or high_score[0] >= significance_value or len(researcher_hands[1])==0:
                game_state = 'over'

            # Update display
            screen.fill(SCREEN_RGB)
            display_board(game_context, draw_deck)
            display_cards(researcher_hands)
            display_samples(sample_values)
            display_description(description)
            display_significance(significance_value)
            display_notification_and_score(whose_turn, turn_phase, current_action, low_score, high_score)

        elif game_state == 'over':
            game_result, game_winner = compute_end_result(low_score, high_score, significance_value)
            if game_result == 'conclusion':
                description = f'Researcher {researcher_names[game_winner]} wins!'
            else:
                description = "Null result. No winner."

            # Update display
            screen.fill(SCREEN_RGB)
            display_board(game_context, draw_deck)
            display_cards(researcher_hands)
            display_samples(sample_values)
            display_description(description)
            display_significance(significance_value)
            display_notification_and_score(whose_turn, 'notify', current_action, low_score, high_score)

            if not_played_sound:
                end_sound = pg.mixer.Sound(SOUND_PATH)
                end_sound.play()
                not_played_sound = False

            # If space bar is pressed, go back to ready page
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        game_state = 'over_result'

        elif game_state == 'over_result':
            display_end_screen(low_score, high_score, significance_value, game_context)

            # If space bar is pressed, go back to ready page
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        game_state = 'ready'

        else:
            raise ValueError(f'Game state is unknown: {game_state}')

        pg.display.update()

# Run the Dash app
if __name__ == '__main__':
    run()