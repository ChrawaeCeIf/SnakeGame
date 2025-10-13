from pynput import keyboard

current_key = None

def on_press(key):
    global current_key
    current_key = key

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def KeyboardControl():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener

def gameKeyboardControl():
    return current_key