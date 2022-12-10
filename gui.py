import customtkinter as ctk
from Generator import Generator
from Aligner import Aligner

class BGUI:
    def __init__(self):
        self.init_frame()

        self.generator = Generator()
        self.aligner = Aligner()

        self.label = ctk.CTkLabel(master=self.frame, text="t2d_0.01")
        self.label.pack(pady=12, padx=10)

        self.entry_text = ctk.CTkEntry(master=self.frame, placeholder_text="text", width=400)
        self.entry_text.pack(pady=12, padx=10)

        self.counter_entry = ctk.CTkEntry(master=self.frame, placeholder_text="1", width=40)
        self.counter_entry.pack(pady=12, padx=10)

        self.banner_toggle = ctk.CTkCheckBox(master=self.frame, text="disable banner")
        self.banner_toggle.pack()

        self.generate = ctk.CTkButton(master=self.frame, text="Generate", command=self.exec_command)
        self.generate.pack(pady=12, padx=10)

        self.test_button = ctk.CTkButton(master=self.frame, text="Test", command=self.exec_test)
        self.test_button.pack(pady=12, padx=10)

        self.root.mainloop()

    def exec_command(self):
        textline = self.entry_text.get().split("#")
        counter = int(self.counter_entry.get())
        place_banner = self.banner_toggle.get()
        self.aligner.set_disable_banner(place_banner)
        for _ in range(counter):
            effects = self.generator.new_effects(textline=textline, mode=2, r_alt=2)
            self.aligner.get_new_design(textline=textline, effects=effects)

    def exec_test(self):
        print("entry button: ", self.entry_text.get())
        print("counter entry: ", self.counter_entry.get())
        print("banner checkbox: ", self.banner_toggle.get())

    def init_frame(self):

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = ctk.CTk()
        self.frame = ctk.CTkFrame(master=self.root)
        self.root.geometry("500x350")
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

def main():
    BGUI()

if __name__ == "__main__":
    main()