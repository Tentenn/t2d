# This is the runner and tester for the project
from Generator import Generator
from Aligner import Aligner


def main():
    texts = ["Horse#Girl"]
    generator = Generator()
    aligner = Aligner()

    for text in texts:
        textline = text.split("#")
        effects = generator.new_effects(textline=textline, mode=2, r_alt=2)
        aligner.get_new_design(textline=textline, effects=effects)



if __name__ == "__main__":
    main()