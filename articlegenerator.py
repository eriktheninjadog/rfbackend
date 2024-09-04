# article generator

import random

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os

from pydub import AudioSegment


import subtitles
import openrouter
import json

people = ["Abraham Lincoln ","Adam Smith ","Adolf Hitler","Akhenaten ","Al Gore","Albert Einstein","Alexander Hamilton",
"Alexander the Great","Amos Alonzo Stagg ","Andrew Jackson ","Anne Boleyn ","Anthony the Great ",
"Aristotle","Arnold Schwarzenegger","Askar Akayev ","Attila ","Augustine of Hippo ","Augustus ","Barack Obama",
"Benito Mussolini","Benjamin Franklin","Bill Clinton","Bill Gates","Billy the Kid ","Bob Dylan","Bob Hope ",
"Britney Spears","Caligula ","Carl Linnaeus","Charlemagne","Charles Darwin","Charles Dickens","Charles I","Charles II ","Charles V ",
"Che Guevara","Chiang Kai-shek","Christina Aguilera","Christopher Columbus",
"Cicero ","Cnut the Great ","Constantine the Great ","Dante Alighieri ","David Bowie","Diana","Dwight D. Eisenhower","E. Bowes-Lyon ","Edgar Allan Poe ",
"Edward Bernays ","Edward I ","Edward II ","Elizabeth I","Elizabeth I ","Elizabeth II","Elvis Presley","Eminem","Emomalii Rahmon ","Emperor Meiji ","Ernest Hemingway",
"Ferdinand Marcos ","Fidel Castro","Francis Bacon ","Franklin D. Roosevelt","Franz Schubert ","Friedrich Nietzsche","Galileo Galilei ","Gautama Buddha ",
"Genghis Khan","George Bernard Shaw ","George H. W. Bush","George III ","George W. Bush","George Washington","Gerald Ford",
"Giuseppe Verdi ","Grover Cleveland ","Gyanendra of Nepal ","Harry S. Truman","Henry VIII ",
"Hillary Rodham Clinton","Ho Chi Minh","Immanuel Kant ","Isaac Newton","Islam Karimov ","J. R. R. Tolkien",
"J. Rousseau ","J. W. von Goethe ","James Cook ","James I ","James Madison","Jawaharlal Nehru ","Jean-Jacques Rousseau ","Jesse James ","Jesus ",
"Jigme Singye Wangchuck ","Jimi Hendrix ","Jimmy Carter","Joan of Arc ","Johann Sebastian Bach ","Johann Wolfgang von Goethe ","John Adams ","John Calvin ","John D. Rockefeller ","John Dewey ","John F. Kennedy","John Keats ",
"John Kerry","John Lennon","John Locke","John Locke ","John McCain","John Wilkes Booth ","Joseph Smith ","Joseph Stalin","Joseph Stalin ",
"Julius Caesar","Junius Richard Jayewardene ","Karl Marx","Katharine Hepburn ","Kaysone Phomvihane ","Kim Il-sung ","King Arthur ","Lady Jane Grey ","Lee Kuan Yew ","Leonardo da Vinci",
"Louis XIV","Ludwig van Beethoven ","Lyndon B. Johnson","Madonna","Mahathir Mohamad ",
"Mao Zedong ","Margaret Thatcher","Mariah Carey","Marilyn Monroe","Mark Twain ","Martin Luther",
"Martin Luther ","Martin Luther King","Maumoon Abdul Gayoom ","Michael Jackson","Michael Jordan","Michelangelo ",
"Mimar Sinan ","Mohandas K. Gandhi ","Mohandas Karamchand Gandhi ","Muhammad ","Napoleon ","Ne Win ","Nelson Mandela",
"Nicolaus Copernicus ","Nikola Tesla ","Noam Chomsky","Nursultan Nazarbayev ",
"Oliver Cromwell ","Osama bin Laden","Oscar Wilde ","Otto von Bismarck ","P. I. Tchaikovsky ","Paul McCartney","Paul the Apostle",
"Paul the Apostle ","Percy B. Shelley ","Person","Person Dates Sig","Philip II ","Plato","Pocahontas ","Pol Pot ","Pope Benedict XVI",
"Pope John Paul II","Pyotr Ilyich Tchaikovsky ","Queen Victoria","Ramesses II ","René Descartes ","Richard I ","Richard III ","Richard Nixon",
"Richard Wagner ","Robert E. Lee ","Roger Federer","Ronald Reagan ","Rose Kennedy ","Sacagawea ","Saddam Hussein","Saint George ","Saint Peter",
"Saparmurat Niyazov ","Sarah Palin","Sheikh Mujibur Rahman","Sigmund Freud","Socrates ",
"Soong May-ling","Steven Spielberg","Suharto ","Thaksin Shinawatra ","Theodore Roosevelt","Thomas Aquinas ","Thomas Edison","Thomas Hobbes ",
"Thomas Jefferson","Tony Blair","Tsakhiagiin Elbegdorj ","Tutankhamun ","Ulysses S. Grant ","Vincent van Gogh ","Vladimir Lenin ","Vladimir Putin","Voltaire ",
"William Shakespeare ","William the Conqueror ","Winston Churchill ","Wolfgang A. Mozart ","Wolfgang Amadeus Mozart ","Woodrow Wilson","Évariste Galois ","John the Baptist ","Tiberius ",
"Herod the Great ","Pontius Pilate ","Saint Matthew ","Mark the Evangelist ","Mary Magdalene ","Luke the Evangelist ","Saint Joseph ","Saint Stephen ","Judas Iscariot ",
"John the Evangelist ","Barnabas","Flavius Josephus","William Nelson","Mary I of England",
"August Bebel","Charles Babbage","David Geffen","Louis Le Prince","Flora MacDonald","Giovanni Battista Tiepolo","Sami Yusuf","Giulio Romano","Plutarch","John Howland",
"Carl Perkins","Curtis Mayfield","Diana Ross","Lynyrd Skynyrd","Nine Inch Nails","Guns n’ Roses","Carlos Santana","Jay-Z","Tupac Shakur","Black Sabbath",
"Eminem","Elvis Costello","The Stooges","Beastie Boys","Hank Williams","Radiohead","Frank Zappa",
"Tina Turner","Joni Mitchell","Metallica","The Sex Pistols","Howlin’ Wolf","Patti Smith","Janis Joplin","Public Enemy",
"The Doors","Michael Jackson","Neil Young","Johnny Cash","Bruce Springsteen","The Velvet Underground","Jimi Hendrix",
"Bob Dylan","Genghiz Khan","Hannibal Barca","Khalid ibn al-Walid","Horatio Nelson","Subutai","Jan Zizka","Oda Nobunaga",
"linus torvalds","Ada Lovelace","James Gosling","Brian Kernighan","Paula Tsui","Sammi Cheng","Faye Wong","Miriam Yeung",
"ISAAC NEWTON","ALBERT EINSTEIN","ALEXANDER FLEMING","SRINIVASA RAMANUJAN","LOUIS PASTEUR","JOHANNES KEPLER","LIU HUI",
"MAX PLANCK","AUGUSTIN-LOUIS CAUCHY","JAMES CLERK MAXWELL","AVICENNA of PERSIA (IBN SINA)",
"HERMANN von HELMHOLTZ","LEONHARD EULER","DMITRI MENDELEEV","ROBERT KOCH","ERNEST RUTHERFORD","NICOLAUS COPERNICUS","GEORG BERNHARD RIEMANN",
"ZHANG HENG","BLAISE PASCAL","MUHAMMAD IBN MUSA AL-KHWARIZMI","JULES HENRI POINCARÉ","ABU RAYHAN AL-BIRUNI","GOTTFRIED von LEIBNIZ",
"ISAMBARD KINGDOM BRUNEL","CLAUDIUS GALEN of PERGAMON","JOSEPH-LOUIS LAGRANGE","QIN JIUSHAO","PAUL EHRLICH","JOHN von NEUMANN","NASIR AL-DIN AL-TUSI",
"ROBERT BOYLE","PIERRE-SIMON LAPLACE","DANIEL BERNOULLI","CARL FRIEDRICH GAUSS","WERNHER von BRAUN","HENRI BECQUEREL","DAVID HILBERT",
"ABU al-QASIM IBN al-ABBAS al-ZAHRAWI","ZHU SHIJIE","GREGOR MENDEL","AMELIE EMMY NOETHER","ANTOINE LAVOISIER","BRAHMAGUPTA","EDWARD JENNER",
"MICHAEL FARADAY","AMEDEO AVOGADRO","ZU CHONGZHI","JAMES WATT","ABU-BAKR MUHAMMAD IBN-ZAKARIYA AL-RAZI","SERGEI PAVLOVICH KOROLEV",
"OMAR AL-KHAYYAM","SIMÉON DENIS POISSON","ROBERT HOOKE","GEORGE WASHINGTON CARVER","NIELS BOHR","ALHAZEN IBN al-HAYTHAM",
"JOSEPH LOUIS GAY-LUSSAC","ARYABHATA","ALESSANDRO VOLTA","CHRISTIAAN HUYGENS","CARL LINNAEUS","WALTHER HERMANN NERNST",
"HIPPOCRATES of COS","CHARLES-AUGUSTIN de COULOMB","GEROLAMO CARDANO","ANDREY KOLMOGOROV","GALILEO GALILEI","SHEN KUO","ANDREAS VESALIUS","ABU-YUSUF AL-KINDI","HEINRICH HERTZ","ZHANG ZHONGJING","HANS CHRISTIAN OERSTED","MADHAVA of SANGAMAGRAMA","JOHN DALTON",
"ANDRÉ-MARIE AMPÈRE","ENRICO FERMI","NIKOLA TESLA","CLAUDE BERNARD","JOHANN HEINRICH LAMBERT","JAMES PRESCOTT JOULE","SEKI KOWA TAKAKAZU","HENDRIK ANTOON LORENTZ",
"OTTO HAHN","LUIGI GALVANI","JEAN-BAPTISTE JOSEPH FOURIER","KATHERINE COLEMAN JOHNSON","GEORG SIMON OHM","MARIE SKLODOWSKA-CURIE","WILLIAM THOMSON KELVIN",
"JOHN BARDEEN","LI SHIZHEN","JAMES JOSEPH SYLVESTER","VIVIEN THEODORE THOMAS","WILHELM CONRAD ROENTGEN",
"ANTONIE van LEEUWENHOEK","JESSE ERNEST WILKINS, Jr.","HUMPHRY DAVY","LISE MEITNER","Joseph Priestley","Louis Pasteur",
"Alfred Nobel","Dmitri Mendeleev","Marie Curie","Alice Ball","Dorothy Hodgkin","Rosalind Franklin","Marie Maynard Daly",
"Mario Molina","Victor Hugo","Jules Verne","Honoré de Balzac","Sartre","Denis Diderot","Alexandre Dumas","Charles Pierre Baudelaire"

] 



def format_time(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')



def generate_srt(text, duration, output_srt):
    words = text.split("\n")
    word_count = len(words)
    avg_word_duration = duration / word_count
    with open(output_srt, 'w') as srt_file:
        current_time = 0
        for i, word in enumerate(words, 1):
            start_time = current_time
            end_time = start_time + avg_word_duration            
            start = format_time(start_time)
            end = format_time(end_time)            
            srt_file.write(f"{i}\n{start} --> {end}\n{word}\n\n")            
            current_time = end_time



def text_to_speech(text, outputname,volume_increase_db=3.0):
    # Create a client using your default AWS configuration
    polly_client = boto3.client('polly')
    output_file = outputname + ".mp3"
    output_srt = outputname + ".srt"
    try:
        # Request speech synthesis
        response = polly_client.synthesize_speech (
            Text=text,
            OutputFormat='mp3',
            VoiceId='Hiujin',
            # You can choose different voices,
            Engine='neural'
        )
                
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                with open(output_file, "wb") as file:
                    file.write(stream.read())

        # Increase volume using pydub
        audio = AudioSegment.from_mp3(output_file)
        louder_audio = audio + volume_increase_db
        louder_audio.export(output_file, format="mp3")

        generate_srt(text, audio.duration_seconds, output_srt)

 
        print(f"Speech synthesized and volume adjusted. Audio saved to {output_file}")
        print(f"SRT file saved to {output_srt}")
        

    except (BotoCoreError, ClientError) as error:
        # The service returned an error
        print(f"Error: {error}")
        raise error


def article_prompt():
    person = random.choice(people)
    prompt = "Write 1000 word article in English, using grammar of someone on A2 level but use nouns on a C1 level, about the famous person: " + person
    return prompt



def generate_english_article():
    prompt = article_prompt()    
    result = openrouter.do_open_opus_questions(prompt)
    return result
 

def translate_to_cantonese(text):
    prompt = "Translate the following text to casual Cantonese. Return the result in traditional characters omly:\n" + text
    result = openrouter.do_open_opus_questions(prompt)
    return result
 

def get_article():
    engtext = generate_english_article()
    cantext = translate_to_cantonese(engtext)
    return cantext

import shutil

for i in range(0,10):
    filename = "genan" + str(random.randint(100,900))
    text_to_speech(get_article(),filename)
    shutil.move(filename+".mp3","/home/erik/Downloads")
    shutil.move(filename+".srt","/home/erik/Downloads")
    subtitles.process_mp3(filename)
    print("done with " + filename)