import datetime
import glob
import math
import random
import sys
import threading
import time

import numpy as np
import pyautogui
import pygetwindow
from PIL import Image
from scipy import interpolate

DEFAULT_MAX_RUN_TIME = 4 * 60 * 60  # 4 hours

KEYBIND_FOR_SURGE = '7'
KEYBIND_FOR_BLADED_DIVE = 'u'
KEYBIND_FOR_EXTREME_RC_POTION = '4'
KEYBIND_FOR_POWERBURST = 'g'
KEYBIND_FOR_WILDERNESS_SWORD = 'f'
KEYBIND_FOR_FIRST_PRESET = 'f1'
KEYBIND_FOR_SECOND_PRESET = 'f2'
KEYBIND_FOR_SUPER_RESTORE = '2'
KEYBIND_FOR_POUCH = '3'

ACTIVE_WINDOW_REGION = []
ACTIVE_WINDOW_MIDDLE_REGION = []
ACTIVE_WINDOW_CENTER = []

ALTAR_NAME = 'blood'
ALTAR_IMAGES = []
ALTAR_RIFT_IMAGES = []
ALTAR_RIFT_CONFIRMATION_IMAGE = None
ALTAR_MINIMAP_IMAGE = None

ACTION_BAR_REGION = []
ACTION_BAR_SLOT_REGION = {}
ACTION_BAR_SLOT_REGION_CENTER = {}

# this is used to ensure that clicks target the outer circle to avoid putting character near altar door
ALTAR_MINIMAP_SKEW = {"blood": [-15, 0]}

MINIMAP_REGION = []
COMPASS_CENTER = []

BANKER_IMAGE = None
BANKER_CONFIRMATION_IMAGES = []
BANKER_LAST_POSITION = [1000, 1355]
BANKER_LAST_REGION = []
BANKING_ICON_SCREEN_REGION = []
BANKING_ICON = None

LAST_POWERBURST_TIME = datetime.datetime.now() - datetime.timedelta(hours=1)
RC_POT_ACTIVE = datetime.datetime.now() - datetime.timedelta(hours=1)
FAMILIAR_REFRESH_TIME = datetime.datetime.now() + datetime.timedelta(hours=1)

SLAYER_MASTER_IMAGE = None
SLAYER_MASTER_LAST_POSITION = [2127, 635]
WALL_IMAGES = []
WALL_CONFIRMATION_IMAGE = None

TREE_IMAGES = []
TREE_LAST_POSITION = None
RIVER_IMAGES = None
RIVER_LAST_POSITION = [2292, 544]

WIZARD_IMAGES = []
ABYSS_THROAT_IMAGE = None

EDGE_BANK_ON_MINIMAP = None
RESTART_MAIN_LOOP = None


def initialize_game_window():
    global ACTIVE_WINDOW_REGION
    global ACTIVE_WINDOW_MIDDLE_REGION
    global ACTIVE_WINDOW_CENTER

    print("Trying to find and initialize the game window...")
    print("Running in a windowed client should be faster when locating items on screen (smaller area to search from)")

    active_game_window = pygetwindow.getWindowsWithTitle("RuneScape")[0]
    active_game_window.activate()

    ACTIVE_WINDOW_REGION = [active_game_window.left, active_game_window.top, active_game_window.width, active_game_window.height]

    # This is used every time we rotate camera to start from an area which shouldn't have interfaces
    ACTIVE_WINDOW_CENTER = pyautogui.center(ACTIVE_WINDOW_REGION)

    # limits the area that we search stuff for to 1/2 of the active game window size
    ACTIVE_WINDOW_MIDDLE_REGION = [active_game_window.left + int(1 / 4 * active_game_window.width),
                                   active_game_window.top + int(1 / 5 * active_game_window.height),
                                   active_game_window.width - int(1 / 2 * active_game_window.width),
                                   active_game_window.height - int(1 / 3 * active_game_window.height)]

    print("Game window initialization done, dont re-size or move your window.\n")


def load_images_from_folder(folder: str) -> list:
    images = []
    for filename in glob.glob(folder):
        im = Image.open(filename)
        images.append(im)
    return images


def initialize_images() -> str:
    global ALTAR_MINIMAP_IMAGE
    global ALTAR_IMAGES
    global ALTAR_RIFT_IMAGES
    global ALTAR_RIFT_CONFIRMATION_IMAGE
    global SLAYER_MASTER_IMAGE
    global WALL_IMAGES
    global WALL_CONFIRMATION_IMAGE
    global TREE_IMAGES
    global RIVER_IMAGES
    global WIZARD_IMAGES
    global ABYSS_THROAT_IMAGE
    global EDGE_BANK_ON_MINIMAP
    global BANKER_IMAGE
    global BANKING_ICON

    print("Trying to initialize and load images...")

    ALTAR_RIFT_IMAGES = load_images_from_folder('Images/Altars/' + ALTAR_NAME + '/RiftImages/*.png')
    ALTAR_IMAGES = load_images_from_folder('Images/Altars/' + ALTAR_NAME + '/AltarImages/*.png')
    WALL_IMAGES = load_images_from_folder('Images/Wall/*.png')
    TREE_IMAGES = load_images_from_folder('Images/Tree/*.png')
    WIZARD_IMAGES = load_images_from_folder('Images/Wizard/*.png')
    RIVER_IMAGES = load_images_from_folder('Images/Minimap/River/*.png')

    # shuffle images so that we dont try same angle multiple times in a row
    random.shuffle(ALTAR_RIFT_IMAGES)
    random.shuffle(ALTAR_IMAGES)
    random.shuffle(WIZARD_IMAGES)
    random.shuffle(WALL_IMAGES)

    ALTAR_MINIMAP_IMAGE = Image.open('Images/Minimap/Abyss/' + ALTAR_NAME + '.png')
    if ALTAR_MINIMAP_IMAGE is None:
        return "Failed to fetch altar minimap image from Images/Minimap/Abyss/" + ALTAR_NAME

    ALTAR_RIFT_CONFIRMATION_IMAGE = Image.open('Images/Altars/Messages/RiftConfirmation/' + ALTAR_NAME + '.png')
    if ALTAR_RIFT_CONFIRMATION_IMAGE is None:
        return "Failed to rift confirmation image from Images/Altars/Messages/RiftConfirmation/"

    BANKER_CONFIRMATION_IMAGES.append(Image.open('Images/Banker/Messages/blue.png'))
    BANKER_CONFIRMATION_IMAGES.append(Image.open('Images/Banker/Messages/yellow.png'))
    if None in BANKER_CONFIRMATION_IMAGES:
        return "Failed to fetch banker confirmation images from Images/Banker/Messages/ should be 2 images, blue and yellow."

    WALL_CONFIRMATION_IMAGE = Image.open('Images/Wall/Messages/wildy.png')
    if WALL_CONFIRMATION_IMAGE is None:
        return "Failed to fetch wilderness wall hop confirmation image from Images/Wall/Messages/wildy.png"

    ABYSS_THROAT_IMAGE = Image.open('Images/Minimap/Abyss/throat.png')
    if ABYSS_THROAT_IMAGE is None:
        return "Failed to fetch abyss minimap image from Images/Minimap/Abyss/throat.png"

    EDGE_BANK_ON_MINIMAP = Image.open('Images/Minimap/bank.png')
    if EDGE_BANK_ON_MINIMAP is None:
        return "Failed to fetch rotated edge bank minimap image from Images/Minimap/bank.png"

    BANKER_IMAGE = Image.open('Images/Banker/banker.png')
    if BANKER_IMAGE is None:
        return "Failed to fetch rotated edge banker image from Images/Banker/banker.png"

    BANKING_ICON = Image.open('Images/Inventory/banking.png')
    if BANKING_ICON is None:
        return "Failed to fetch bank locked icon from Images/Inventory/banking.png"

    SLAYER_MASTER_IMAGE = Image.open('Images/Minimap/slayer_master_icon.png')
    if SLAYER_MASTER_IMAGE is None:
        return "Failed to slayer master minimap icon from Images/Minimap/slayer_master_icon.png"

    print("Images initialized. Selected altar is " + ALTAR_NAME + "\n")


def initialize_banking():
    global BANKING_ICON_SCREEN_REGION
    print("Initializing banking area...")

    banking_icon_region = None
    while banking_icon_region is None:
        banking_icon_region = pyautogui.locateOnScreen(BANKING_ICON,
                                                       confidence=0.6,
                                                       region=ACTIVE_WINDOW_REGION)
        if banking_icon_region is not None:
            BANKING_ICON_SCREEN_REGION = [banking_icon_region.left - 50,
                                          banking_icon_region.top - 50,
                                          banking_icon_region.width + 100,
                                          banking_icon_region.height + 100]

        print("Please open your bank to configure banking area.")
        print("Retrying in 2 seconds ...")
        time.sleep(2)
    print("Banking area initialized.\n")
    pyautogui.press('esc')


def find_minimap():
    global MINIMAP_REGION
    global COMPASS_CENTER

    configured = False
    while not configured:

        try:
            compass_box = pyautogui.locateOnScreen('Images/Minimap/Generic/compass_half.png', confidence=0.8, region=ACTIVE_WINDOW_REGION)
            hometele_box = pyautogui.locateOnScreen('Images/Minimap/Generic/hometele.png', confidence=0.7, region=ACTIVE_WINDOW_REGION)
            run_energy_box = pyautogui.locateOnScreen('Images/Minimap/Generic/full_run_energy.png', confidence=0.9, region=ACTIVE_WINDOW_REGION)

            compass_center = pyautogui.center(compass_box)
            width = abs(compass_center[0] - pyautogui.center(run_energy_box)[0])
            height = abs(compass_center[1] - pyautogui.center(hometele_box)[1])

            # Use left, top, width, and height to define where minimap is on the client for faster recognition cycles
            # 50px is the approx amount of lost data
            MINIMAP_REGION = [compass_box.left, compass_box.top, width + 50, height + 50]
            COMPASS_CENTER = [compass_center[0], compass_center[1]]

            configured = True
        except Exception as e:
            print("Failed to configure minimap, check that run energy is 100% and compass points north (click compass once and move mouse away)")


def find_main_actionbar():
    global ACTION_BAR_REGION
    global ACTION_BAR_SLOT_REGION
    global ACTION_BAR_SLOT_REGION_CENTER

    print("Trying to locate main actionbar...")
    action_bar_anchors = load_images_from_folder('Images/Actionbar/Generic/Anchor/*.png')

    while True:
        for anchor_image in action_bar_anchors:
            bar = pyautogui.locateOnScreen(anchor_image, confidence=0.95, region=ACTIVE_WINDOW_REGION)
            if bar is not None:
                ACTION_BAR_REGION = [bar.left, bar.top, 655, 95]
                for i in range(0, 14):
                    ACTION_BAR_SLOT_REGION[i + 1] = [bar.left + 5 + i * 45, bar.top + 50, 40, 40]
                    ACTION_BAR_SLOT_REGION_CENTER[i + 1] = pyautogui.center(ACTION_BAR_SLOT_REGION[i + 1])
                print("Main actionbar located.")
                return

        print("Failed to find main actionbar.")
        print("Set interface transparency to 0%, interface scaling to 100% and your main actionbar horizontally.")
        print("Retrying to find main actionbar after 5 seconds...\n")
        time.sleep(5)


def check_main_action_bar():
    global ACTION_BAR_SLOT_REGION
    print("Checking that main actionbar matches given action bar...")

    while True:
        test = []
        massive = Image.open('Images/Actionbar/Pouches/massive.png')
        test.append(pyautogui.locateOnScreen(massive, confidence=0.7, region=ACTION_BAR_SLOT_REGION[1]))

        familiar = Image.open('Images/Actionbar/Generic/familiar.png')
        test.append(pyautogui.locateOnScreen(familiar, confidence=0.7, region=ACTION_BAR_SLOT_REGION[2]))

        giant = Image.open('Images/Actionbar/Pouches/giant.png')
        test.append(pyautogui.locateOnScreen(giant, confidence=0.7, region=ACTION_BAR_SLOT_REGION[3]))

        medium = Image.open('Images/Actionbar/Pouches/medium.png')
        test.append(pyautogui.locateOnScreen(medium, confidence=0.7, region=ACTION_BAR_SLOT_REGION[4]))

        large = Image.open('Images/Actionbar/Pouches/large.png')
        test.append(pyautogui.locateOnScreen(large, confidence=0.7, region=ACTION_BAR_SLOT_REGION[5]))

        small = Image.open('Images/Actionbar/Pouches/small.png')
        test.append(pyautogui.locateOnScreen(small, confidence=0.5, region=ACTION_BAR_SLOT_REGION[6]))

        familiar = Image.open('Images/Actionbar/Generic/familiar.png')
        test.append(pyautogui.locateOnScreen(familiar, confidence=0.7, region=ACTION_BAR_SLOT_REGION[7]))

        body = Image.open('Images/Actionbar/Generic/body.png')
        test.append(pyautogui.locateOnScreen(body, confidence=0.5, region=ACTION_BAR_SLOT_REGION[8]))

        if None not in test:
            print("Main actionbar OK.\n")
            return

        print("Main action bar not matching. Ensure that your main action bar is set up to have items in same order as in example image.")
        print("Turn your revolution off and ensure that mouse is not hovering the main action bar.")
        print("Retrying in 10 seconds...")
        time.sleep(10)


def point_dist(current_x: int, current_y: int, destination_x: int, destination_y: int):
    return math.sqrt(abs(destination_x - current_x) ** 2 + abs(destination_y - current_y) ** 2)


def get_position() -> [int, int]:
    position = pyautogui.position()
    return int(position[0]), int(position[1])


def perform_move(x: int, y: int, ms_variation=None):
    if ms_variation is None:
        ms_variation = [20, 40]

    current_x, current_y = get_position()
    cp = random.randint(3, 5)  # Number of control points. Must be at least 2.

    # Distribute control points between start and destination evenly.
    array_x = np.linspace(current_x, x, num=cp, dtype='int')
    array_y = np.linspace(current_y, y, num=cp, dtype='int')

    # Randomise inner points a bit (+-RND at most).
    rnd = 10
    xr = [random.randint(-rnd, rnd) for k in range(cp)]
    yr = [random.randint(-rnd, rnd) for k in range(cp)]
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    array_x += xr
    array_y += yr

    # Approximate using Bezier spline.
    degree = 3 if cp > 3 else cp - 1  # Degree of b-spline. 3 is recommended.
    # Must be less than number of control points.
    try:
        tck, u = interpolate.splprep([array_x, array_y], k=degree)
        # Move up to a certain number of points
        u = np.linspace(0, 1, num=2 + int(point_dist(current_x, current_y, x, y) / 50.0))
        x_points, y_points = interpolate.splev(u, tck)
        xy_points = list(zip([int(x) for x in x_points], [int(y) for y in y_points]))

        # Move mouse.
        duration = random.randint(*ms_variation) / 100
        timeout = duration / len(xy_points)
        for point in xy_points:
            pyautogui.moveTo(*point)
            time.sleep(timeout)
    except:
        pass


def perform_click(should_doubleclick: int = None):
    if should_doubleclick is None:
        should_doubleclick = random.randint(1, 12)

    if should_doubleclick < 3:
        # generate random number between 0.15 and 0.3s as the time between doubleclick
        doubleclick_interval = random.randint(15, 25) / 100
        pyautogui.click(clicks=2, interval=doubleclick_interval)
    else:
        pyautogui.click()
        time.sleep(random.randint(15, 25) / 100)
    move_mouse_after_click = random.randint(1, 12)
    if move_mouse_after_click < 3:
        current_x, current_y = get_position()
        x_to_move = random.randint(25, 75)
        y_to_move = random.randint(25, 75)
        perform_move(x=current_x + x_to_move,
                     y=current_y + y_to_move,
                     ms_variation=[15, 30])


def path_to_altar(altar_name: str):
    altar_on_minimap = None
    while altar_on_minimap is None:
        altar_on_minimap = pyautogui.locateOnScreen(ALTAR_MINIMAP_IMAGE, confidence=0.7, region=MINIMAP_REGION)
        if altar_on_minimap is not None:
            a_m_x, a_m_y = pyautogui.center(altar_on_minimap)

            x_to_click = a_m_x + random.randint(*ALTAR_MINIMAP_SKEW[altar_name])
            y_to_click = a_m_y + random.randint(-5, 5)

            perform_move(x_to_click, y_to_click)
            perform_click()
            return


def focus_minimap_north():
    x_to_click = COMPASS_CENTER[0] + random.randint(-10, 10)
    y_to_click = COMPASS_CENTER[1] + random.randint(-10, 10)
    perform_move(x_to_click, y_to_click)
    perform_click()


def rotate_camera(rotation_angle: int):
    # ~center mouse to prep for the camera rotation
    perform_move(x=ACTIVE_WINDOW_CENTER[0] + random.randint(-200, 100),
                 y=ACTIVE_WINDOW_CENTER[1] + random.randint(-200, 200))

    current_x, current_y = get_position()

    # rotate camera using middle mouse button
    pyautogui.mouseDown(button='middle')
    perform_move(x=current_x + random.randint(rotation_angle - 20, rotation_angle + 20),
                 y=current_y + random.randint(-15, 15))
    pyautogui.mouseUp(button='middle')


def find_and_enter_altar():
    rift_x, rift_y = None, None
    while None in [rift_x, rift_y]:
        rift_x, rift_y = find_and_click_from_image_list(ALTAR_RIFT_IMAGES, region=ACTIVE_WINDOW_MIDDLE_REGION, x_variance=[-10, 10],
                                                        y_variance=[-5, 20], confirmation_image=ALTAR_RIFT_CONFIRMATION_IMAGE)


def craft_runes():
    global LAST_POWERBURST_TIME

    if LAST_POWERBURST_TIME + datetime.timedelta(seconds=90) < datetime.datetime.now():
        pyautogui.press(KEYBIND_FOR_POWERBURST, presses=random.randint(1, 4), interval=random.randint(20, 40) / 100)
        LAST_POWERBURST_TIME = datetime.datetime.now()

    print("searching for altar")
    altar_search_timer = datetime.datetime.now() + datetime.timedelta(seconds=30)
    altar_x, altar_y = None, None
    while None in [altar_x, altar_y]:
        altar_x, altar_y = find_and_click_from_image_list(ALTAR_IMAGES, region=ACTIVE_WINDOW_MIDDLE_REGION, x_variance=[-20, 20],
                                                          y_variance=[-20, 20], confidence=0.4)
        if datetime.datetime.now() > altar_search_timer:
            return
    time.sleep(random.randint(24, 40) / 10)


def teleport_to_edge():
    focus_minimap_north()

    edge_bank = None
    while edge_bank is None:
        pyautogui.press(KEYBIND_FOR_WILDERNESS_SWORD, presses=random.randint(1, 3), interval=(random.randint(15, 25) / 100))
        time.sleep(random.randint(30, 50) / 10)

        print("searching for bank")
        edge_bank = pyautogui.locateOnScreen(EDGE_BANK_ON_MINIMAP, confidence=0.7, region=MINIMAP_REGION)
        if edge_bank is not None:
            bank_center = pyautogui.center(edge_bank)
            perform_move(x=bank_center[0] + random.randint(10, 20),
                         y=bank_center[1] + random.randint(-10, -5))
            perform_click()


def confirm_banker_found():
    current_region = BANKER_LAST_REGION if len(BANKER_LAST_REGION) > 0 else ACTIVE_WINDOW_MIDDLE_REGION

    confirm_yellow = pyautogui.locateOnScreen(BANKER_CONFIRMATION_IMAGES[1],
                                              confidence=0.8,
                                              region=current_region)
    if confirm_yellow is not None:
        return True

    confirm_blue = pyautogui.locateOnScreen(BANKER_CONFIRMATION_IMAGES[0],
                                            confidence=0.8,
                                            region=current_region)
    if confirm_blue is not None:
        return True

    return False


def drink_rc_pot():
    global RC_POT_ACTIVE

    now = datetime.datetime.now()

    if RC_POT_ACTIVE < now:
        pyautogui.press(KEYBIND_FOR_EXTREME_RC_POTION, presses=random.randint(1, 3), interval=random.randint(10, 15) / 100)
        RC_POT_ACTIVE = now + datetime.timedelta(minutes=6)


def find_banker(use_last_position: bool = False):
    global BANKER_LAST_POSITION
    global BANKER_LAST_REGION
    global RESTART_MAIN_LOOP

    if use_last_position:
        perform_move(x=BANKER_LAST_POSITION[0],
                     y=BANKER_LAST_POSITION[1])
        perform_click()

    current_region = BANKER_LAST_REGION if len(BANKER_LAST_REGION) > 0 else ACTIVE_WINDOW_REGION
    banking_icon = None
    retries = 4
    banking_time_limit = datetime.datetime.now() + datetime.timedelta(seconds=20)
    while banking_icon is None:
        print("finding banker")
        banking_icon = pyautogui.locateOnScreen(BANKING_ICON, confidence=0.8, region=BANKING_ICON_SCREEN_REGION)
        if banking_icon is None:
            banker_region = pyautogui.locateOnScreen(BANKER_IMAGE, confidence=0.5, region=current_region)
            if banker_region is not None:
                banker_x, banker_y = pyautogui.center(banker_region)
                perform_move(x=banker_x + random.randint(-10, 5),
                             y=banker_y - 60 + random.randint(-10, 20))
                if confirm_banker_found():
                    perform_click(4)
                    BANKER_LAST_POSITION = get_position()
                    BANKER_LAST_REGION = [banker_region.left - 150,
                                          banker_region.top - 150,
                                          banker_region.width + 300,
                                          banker_region.height + 300]
        retries -= 1
        if retries < 1:
            perform_move(x=ACTIVE_WINDOW_CENTER[0] + random.randint(-200, 100),
                         y=ACTIVE_WINDOW_CENTER[1] + random.randint(-200, -100))
            current_region = ACTIVE_WINDOW_REGION
            retries = 5
        if datetime.datetime.now() > banking_time_limit:
            RESTART_MAIN_LOOP = True


def load_preset():
    icon_found = None
    while icon_found is None:
        icon_found = pyautogui.locateOnScreen(BANKING_ICON, confidence=0.8, region=BANKING_ICON_SCREEN_REGION)

        if icon_found is not None:
            pyautogui.press(KEYBIND_FOR_FIRST_PRESET, presses=random.randint(1, 3), interval=(random.randint(15, 25) / 100))
            time.sleep(random.randint(30, 45) / 100)


def fill_pouches(start_index: int, use_last_position: bool = False):
    perform_move(x=ACTION_BAR_SLOT_REGION_CENTER[start_index][0] + random.randint(-10, 10),
                 y=ACTION_BAR_SLOT_REGION_CENTER[start_index][1] + random.randint(-10, 10))
    pyautogui.click()

    for i in range(start_index + 1, start_index + 4):
        pyautogui.moveTo(ACTION_BAR_SLOT_REGION_CENTER[i][0] + random.randint(-10, 10),
                         ACTION_BAR_SLOT_REGION_CENTER[i][1] + random.randint(-10, 10))
        pyautogui.click()
        time.sleep(random.randint(20, 25) / 100)

    find_banker(use_last_position)
    if not RESTART_MAIN_LOOP:
        load_preset()


def refresh_familiar():
    global FAMILIAR_REFRESH_TIME

    icon_found = None
    while icon_found is None:
        icon_found = pyautogui.locateOnScreen(BANKING_ICON, confidence=0.8, region=BANKING_ICON_SCREEN_REGION)

        if icon_found is not None:
            pyautogui.press(KEYBIND_FOR_SECOND_PRESET, presses=random.randint(1, 3), interval=(random.randint(15, 25) / 100))
            time.sleep(random.randint(30, 45) / 100)

            pyautogui.press(KEYBIND_FOR_SUPER_RESTORE)
            time.sleep(0.5)
            pyautogui.press(KEYBIND_FOR_POUCH)
            FAMILIAR_REFRESH_TIME = datetime.datetime.now() + datetime.timedelta(minutes=60)
            find_banker()


def perform_banking():
    if datetime.datetime.now() > FAMILIAR_REFRESH_TIME:
        print("referesing familiar")
        refresh_familiar()

    if not RESTART_MAIN_LOOP:
        load_preset()

        # drink pot if needed while putting ess to pouches
        rc_potion = threading.Thread(target=drink_rc_pot)
        rc_potion.start()

        # click first 4 slots on main bar
        fill_pouches(1)
        fill_pouches(5, use_last_position=True)


def find_and_click_from_image_list(image_list: list, region: list, x_variance: list, y_variance: list, confirmation_image=None,
                                   confidence: float = 0.8) -> [int, int]:
    for image in image_list:
        found_image = pyautogui.locateOnScreen(image, confidence=confidence, region=region)
        print("found_image:", found_image)
        if found_image is not None:
            found_image_x, found_image_y = pyautogui.center(found_image)
            perform_move(x=found_image_x + random.randint(*x_variance),
                         y=found_image_y + random.randint(*y_variance))

            if confirmation_image is None:
                if image_list is TREE_IMAGES:
                    # bd tree and dont doubleclick
                    pyautogui.press(KEYBIND_FOR_BLADED_DIVE)
                    time.sleep(random.randint(15, 20) / 100)
                    perform_click(4)
                else:
                    perform_click()
                return found_image_x, found_image_y
            else:
                confirmed = pyautogui.locateOnScreen(confirmation_image, confidence=confidence, region=region)
                if confirmed is not None:
                    perform_click()
                    return found_image_x, found_image_y
    return None, None


def surge():
    pyautogui.press(KEYBIND_FOR_SURGE, presses=random.randint(1, 3), interval=(random.randint(15, 25) / 100))


def move_to_wall_and_hop():
    global SLAYER_MASTER_LAST_POSITION

    slayer_master = pyautogui.locateOnScreen(SLAYER_MASTER_IMAGE, confidence=0.8, region=MINIMAP_REGION)
    if slayer_master is not None:
        slayer_master_x, slayer_master_y = pyautogui.center(slayer_master)
        perform_move(x=slayer_master_x + random.randint(-10, 10),
                     y=slayer_master_y + random.randint(-10, 10))
        perform_click()
        SLAYER_MASTER_LAST_POSITION = [slayer_master_x, slayer_master_y]
    else:
        perform_move(SLAYER_MASTER_LAST_POSITION[0], SLAYER_MASTER_LAST_POSITION[1])
        perform_click()

    time.sleep(random.randint(40, 45) / 10)
    surge()
    time.sleep(random.randint(10, 15) / 100)

    print("searching for wilderness wall")
    wall_x, wall_y = None, None
    while None in [wall_x, wall_y]:
        wall_x, wall_y = find_and_click_from_image_list(WALL_IMAGES, ACTIVE_WINDOW_REGION, [-5, 5], [-5, 5],
                                                        confirmation_image=WALL_CONFIRMATION_IMAGE, confidence=0.7)
    time.sleep(random.randint(25, 30) / 10)


def navigate_to_wizard():
    global TREE_LAST_POSITION
    global RIVER_LAST_POSITION

    tree_x, tree_y = find_and_click_from_image_list(TREE_IMAGES, ACTIVE_WINDOW_MIDDLE_REGION, [-20, 20], [-20, 20])
    if None in [tree_x, tree_y]:
        perform_move(TREE_LAST_POSITION[0], TREE_LAST_POSITION[1])
        perform_click()
    else:
        TREE_LAST_POSITION = [tree_x, tree_y]

    river_x, river_y = find_and_click_from_image_list(RIVER_IMAGES, MINIMAP_REGION, [-80, -40], [-50, 0])
    if None in [river_x, river_y]:
        perform_move(RIVER_LAST_POSITION[0], RIVER_LAST_POSITION[1])
        perform_click()
    else:
        RIVER_LAST_POSITION = [river_x, river_y]

    time.sleep(0.5)
    wizard_thread = threading.Thread(target=enter_the_abyss, daemon=True)
    wizard_thread.start()
    time.sleep(1.5)
    surge()
    perform_move(x=ACTIVE_WINDOW_CENTER[0] + random.randint(-200, 200),
                 y=ACTIVE_WINDOW_CENTER[1] + random.randint(-200, 200))
    wizard_thread.join()


def enter_the_abyss():
    global RESTART_MAIN_LOOP

    # teleport to edge and try again if wizard isnt found in 30s
    search_end_time = datetime.datetime.now() + datetime.timedelta(seconds=30)

    in_abyss = None
    while in_abyss is None:
        in_abyss = pyautogui.locateOnScreen(ABYSS_THROAT_IMAGE, confidence=0.9, region=MINIMAP_REGION)
        if in_abyss is None:
            for wizard_image in WIZARD_IMAGES:
                print("searching for wizard")
                try:
                    wizard_x, wizard_y = pyautogui.center(pyautogui.locateOnScreen(wizard_image, confidence=0.7, region=ACTIVE_WINDOW_REGION))
                    perform_move(x=wizard_x, y=wizard_y, ms_variation=[0, 5])
                    pyautogui.click()
                    print("wizard found")
                    time.sleep(3)
                except:
                    pass
        if datetime.datetime.now() > search_end_time:
            RESTART_MAIN_LOOP = True
            return


def runecrafting_loop():
    global RESTART_MAIN_LOOP
    while True:
        RESTART_MAIN_LOOP = False

        teleport_to_edge()
        find_banker()
        if not RESTART_MAIN_LOOP:
            perform_banking()

            move_to_wall_and_hop()
            navigate_to_wizard()

            if not RESTART_MAIN_LOOP:
                path_to_altar(ALTAR_NAME)

                rotate_camera(400)
                time.sleep(4)

                find_and_enter_altar()
                craft_runes()


if __name__ == "__main__":
    """
    TODO: lets comment some stuff here once this gary works okay 
    """
    # The following default settings are overwritten for more human mouse movement
    pyautogui.MINIMUM_DURATION = 0
    pyautogui.MINIMUM_SLEEP = 0
    pyautogui.PAUSE = 0

    errors = [initialize_game_window(),
              initialize_images(),
              initialize_banking()]

    if any(errors):
        for error in errors:
            print(error)
        print("\nFailed to initialize gary, exiting program.")
        exit()

    find_minimap()
    find_main_actionbar()
    check_main_action_bar()

    rc_thread = threading.Thread(target=runecrafting_loop, daemon=True)
    rc_thread.start()

    time.sleep(DEFAULT_MAX_RUN_TIME)
    teleport_to_edge()
    sys.exit()
