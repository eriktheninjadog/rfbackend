from wonderwords import RandomWord
import api
import constants

r = RandomWord()


def create_story():
    w1 = r.word(include_parts_of_speech=["nouns"])
    w2 = r.word(include_parts_of_speech=["nouns"])
    w3 = r.word(include_parts_of_speech=["nouns"])
    result = "Write a story in traditional Chinese about a " + w1 + ", a " + w2 + " and a " + w3 
    api.create_generative_text(result)



def create_sales_text():
    w1 = r.word(include_parts_of_speech=["nouns"])
    result = "Write a sales letter in traditional chinese selling " + w1
    api.create_generative_text(result)


def create_history_text():
    w1 = r.word(include_parts_of_speech=["nouns"])
    result = "Write a brief history of "  + w1 + " using traditional chinese"
    api.create_generative_text(result)

#for i in range(100):
#    create_story()
#    create_sales_text()
#    create_history_text()


# its more complicated than this!

l = api.get_responsecws_of_responsetype(constants.RESPONSE_TYPE_GENERATE_TEXT)
for c in l:
    txt = c.orgtext
    api.create_verify_challenge(txt)
