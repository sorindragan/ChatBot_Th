import os
import sys
from gtts import gTTS

from conversation import Conversation
from coref.coref import *
from speech_to_text import SpeechToText
from text_similarity.fail_safe import FailSafe

def main():
    coref_solver = CorefSolver()
    fail_safe = FailSafe()
    verbose = False
    if "--verbose" in sys.argv:
        verbose = True
        c = Conversation(verbose=True)
    else:
        c = Conversation()

    kb_file_name = None
    if "--kb" in sys.argv:
        pos = sys.argv.index("--kb")
        kb_file_name = sys.argv[pos + 1]

    q_file_name = None
    if "--q" in sys.argv:
        pos = sys.argv.index("--q")
        q_file_name = sys.argv[pos + 1]

    if kb_file_name:
        with open(kb_file_name, "r") as f:
            utterances = list(f)
            for u in utterances:
                print("##################################################")
                print(u)
                solved_coref, unsolved_coref = coref_solver.solve(u[:-1], previous=True, depth=10, verbose=verbose)
                if solved_coref == "":
                    solved_coref = u[:-1]

                response = c.process(solved_coref)
                print(response)

    if q_file_name:
        with open(q_file_name, "r") as f:
            questions = list(f)
            for q in questions:
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                print(q)

                print(c.process(q))
            return

    speech_to_text = SpeechToText()

    while True:
        # say
        # utterance = speech_to_text.process()
        # response = c.process(utterance)

        # type
        utterance = str(sys.stdin.readline())

        solved_coref, unsolved_coref = coref_solver.solve(utterance[:-1], previous=True, depth=5, verbose=verbose)
        if solved_coref == "":
            solved_coref = utterance[:-1]
        response = c.process(solved_coref)

        # response = c.process(utterance[:-1])

        if response:

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

            print("Bot: ",  response)

            if response in ["Glad we talked!", "Happy to help!", "Gooodbye!"]:
                break
        else:
            question, response, similarity =  fail_safe.answer_questions(solved_coref)
            print("Bot: ",  response)

            tts = gTTS(text=response, lang='en')
            tts.save("response.mp3")
            os.system("mpg123 response.mp3")

        print()


if __name__ == "__main__":
    main()
