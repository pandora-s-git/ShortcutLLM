import sys
import time
import keyboard
from huggingface_hub import InferenceClient
import pyautogui
import pyperclip

class ShortLLM():
    def __init__(self, shortcut: str = "ctrl+space", stop_shortcut: str = "ctrl", system: str = "Help the user with any task.", max_new_tokens: int = 512, temperature: int = 0.3):
        self.shortcut = shortcut
        self.stop_shortcut = stop_shortcut
        self.system = system
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        if sys.platform.startswith("win"):
            self.sys = "windows"
        else:
            raise ValueError(f"Operative System not compatible: {sys.platform}")
        self.inf = InferenceClient(model="mistralai/Mixtral-8x7B-Instruct-v0.1")

    def write(self, txt: str):
        pyperclip.copy(txt)
        pyautogui.hotkey('ctrl', 'v')
        pyperclip.copy('')

    def type_shift_enter(self):
        pyautogui.keyDown('shift')
        pyautogui.press('enter')
        pyautogui.keyUp('shift')

    def ask_stream(self, txt: str):
        return self.inf.text_generation("<s>[INST] {}\nThe user said:\n{} [/INST] ".format(self.system, txt), max_new_tokens=self.max_new_tokens, temperature=self.temperature, stream=True)

    def on_release(self):
        time.sleep(1)
        if not keyboard.is_pressed(self.shortcut):
            pyautogui.hotkey('ctrl', 'c')
            selected_text = pyperclip.paste()
            print(selected_text)
            pyautogui.press('esc')
            pyautogui.hotkey('right')
            self.type_shift_enter()
            for token in self.ask_stream(selected_text):
                if keyboard.is_pressed(self.stop_shortcut):
                    break
                if "\n" in token:
                    self.type_shift_enter()
                    token = token.replace("\n","")
                self.write(token.replace("</s>",""))
            print("Finished.")

    def run(self):
        keyboard.add_hotkey(self.shortcut, self.on_release)
        while True:
            try:
                keyboard.wait()
            except KeyboardInterrupt:
                print("\nExiting...")
                break
        keyboard.remove_hotkey(self.on_release)

if __name__ == "__main__":
    short_like_me = ShortLLM()
    short_like_me.run()