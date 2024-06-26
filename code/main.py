import pygame
import pygame.freetype
from enum import Enum
from pygame.sprite import RenderUpdates
from Player import mplayer, connect_to_server, check_connection
import OverviewUIHexagon
import UIElements
import os

pygame.init()
# Colours
BLUE = (26, 79, 101, 200)
WHITE = (200, 200, 200)
RED = (100, 0, 0)
GREEN = (0, 100, 0)
BLACK = (0, 0, 0)


class GameState(Enum):
    QUIT = -1
    TITLE = 0
    MAIN_SCREEN = 1
    NEXT_LEVEL = 2


class LoginInfo:
    def __init__(self):
        self.__username = None
        self.__password = None

    def set_login_info(self, username, password):
        self.__username = username
        self.__password = password

    def get_login_user(self):
        return self.__username

    def get_login_pass(self):
        return self.__password


clock = pygame.time.Clock()
login = LoginInfo()


def main():
    client = connect_to_server()
    # establish connection with server
    game_state = GameState(0)
    pygame.init()
    pygame.key.set_repeat(200)
    info = pygame.display.Info()
    w = 500
    h = 600
    screen = pygame.display.set_mode((w, h))

    while True:
        if game_state == GameState.TITLE:
            game_state = title_screen(screen, game_state)

        if game_state == GameState.MAIN_SCREEN:
            username = login.get_login_user()
            password = login.get_login_pass()
            request = "login" + " " + username + " " + password
            print(request)
            client.send(request.encode("utf-8")[:1024])
            received = client.recv(1024).decode("utf-8")
            if received.lower() == "accepted":
                mplayer.set_parameters(client, username, password)
                OverviewUIHexagon.overview_ui(mplayer)
            elif received.lower() == "rejected":
                box = UIElements.TextBox(
                    center_position=(screen.get_width() / 2, 200),
                    font_size=50,
                    bg_rgb=None,
                    text_rgb=RED,
                    text="Wrong Password",)
                box.draw(screen)
                pygame.display.update()
                pygame.time.wait(2000)
                game_state = title_screen(screen, game_state)

        if game_state == GameState.QUIT:
            client.close()
            print('closing from login screen')
            pygame.quit()
            quit()


def title_screen(screen, game_state):
    title = UIElements.TextBox(
        center_position=(screen.get_width() / 2, 100),
        font_size=50,
        bg_rgb=None,
        text_rgb=WHITE,
        text="Leviathans legacy",
    )
    start_btn = UIElements.UIElement(
        center_position=(screen.get_width() / 2, 300),
        font_size=30,
        bg_rgb=None,
        text_rgb=WHITE,
        text="Login",
        action=game_state.MAIN_SCREEN,
    )
    quit_btn = UIElements.UIElement(
        center_position=(screen.get_width() / 2, 475),
        font_size=30,
        bg_rgb=None,
        text_rgb=WHITE,
        text="Quit",
        action=game_state.QUIT,
    )
    login_box = UIElements.InputBox((screen.get_width() / 2) - 100, 350, 200, 36, "Enter your username")
    pass_box = UIElements.InputBoxPass((screen.get_width() / 2) - 100, 400, 200, 36, "Enter your password")

    buttons = RenderUpdates(title, start_btn, quit_btn)
    inputboxes = [login_box, pass_box]
    return inputs(screen, buttons, inputboxes, game_state)


def play_level(screen, game_state):
    return_btn = UIElements.UIElement(
        center_position=(140, 570),
        font_size=20,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="Return to main menu",
        action=game_state.TITLE,
    )

    nextlevel_btn = UIElements.UIElement(
        center_position=(400, 400),
        font_size=30,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="Next level",
        action=game_state.QUIT,
    )

    buttons = RenderUpdates(return_btn, nextlevel_btn)
    inputboxes = []

    return inputs(screen, buttons, inputboxes, game_state)


def inputs(screen, buttons, inputboxes, game_state):
    previous_state = game_state
    base_dir = os.path.dirname(os.path.abspath(__file__))
    background_path = os.path.join(base_dir, '..', 'sprites', 'BackgroundPlaceHolder.png')

    while True:
        background = pygame.image.load(background_path)
        background = pygame.transform.scale(background, (600, 600))
        screen.blit(background, (0, 0))
        UIElements.draw_rect_alpha(screen, (26, 79, 101, 200), (0, 60, 1000, 80))
        mouse_up = False
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                return GameState.QUIT
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            for button in buttons:
                ui_action = button.update(pygame.mouse.get_pos(), mouse_up, event)
                if ui_action is not None:
                    return ui_action
            for box in inputboxes:
                box.handle_event(event)

        for box in inputboxes:
            box.update()
            login.set_login_info(inputboxes[0].text_return(), inputboxes[1].text_return())
        for box in inputboxes:
            box.draw(screen)
        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(30)

        if previous_state == game_state:
            pass

        else:
            return game_state


main()
