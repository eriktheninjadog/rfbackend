
import textprocessing
import articlecrawler
import database

from snownlp import SnowNLP

import api

#print(str(api.get_article('https://news.rthk.hk/rthk/ch/component/k2/1700265-20230512.htm?spTabChangeable=0')))

sample = """
一、科學邊界

汪淼覺得，來找他的這四個人是一個奇怪的組合︰兩名警察和兩名軍人，如果那兩個軍人是武警還算正常，但這是兩名陸軍軍官。

汪淼第一眼就對來找他的警察沒有好感。其實那名穿警服的年輕人還行，舉止很有禮貌，但那位便衣就讓人討厭了。這人長得五大三粗，一臉橫肉，穿著件髒兮兮的皮夾克，渾身菸味，說話粗聲大嗓，是最令汪淼反感的那類人。

「汪淼？」那人問，直呼其名令汪淼很不舒服，況且那人同時還在點菸，頭都不抬一下。不等汪淼回答，他就向旁邊那位年輕人示意了一下，後者向汪淼出示了警官證，他點完菸後就直接向屋裡闖。

「請不要在我家裡抽菸。」汪淼攔住了他。

「喔，對不起，汪教授。這是我們史強隊長。」年輕的警官微笑著說，同時對姓史的使了個眼色。

「成，那就在樓道裡說吧。」史強說著，深深地吸了一大口，手中的菸幾乎燃下去一半，之後竟不見吐出煙來。「你問。」他又向年輕警官偏了一下頭。

「汪教授，我們是想了解一下，最近你與『科學邊界』學會的成員有過接觸，是吧？」

「『科學邊界』是一個在國際學術界很有影響的學術組織，成員都是著名學人。這樣一個合法的學術組織，我怎麼就不能接觸了呢？」

「你看看你這個人！」史強大聲說，「我們說它不合法了嗎？我們說不讓你接觸了嗎？」他說著，剛才吸進肚子裡的煙都噴到汪淼臉上。

「那好，這屬於個人隱私，我沒必要回答你們的問題。」

「還啥都成隱私了，像你這樣一個著名學人，總該對公共安全負責吧。」史強把手中的菸頭扔掉，又從壓扁了的菸盒裡抽出一根。

「我有權不回答，你們請便吧。」汪淼說著要轉身回屋。

「等等！」史強厲聲說，同時朝旁邊的年輕警官揮了一下手，「給他地址和電話，下午去走一趟。」

「你要幹什麼！」汪淼憤怒地質問，這爭吵引得鄰居們也探出頭來，想看看出了什麼事。

「史隊！你說你——」年輕警官生氣地將史強拉到一邊，顯然他的粗俗不只是讓汪淼一人不適應。

「汪教授，請別誤會。」一名少校軍官急忙上前，「下午有一個重要會議，要請幾位學人和專家參加，長官讓我們來邀請您。」

「我下午很忙。」

「這我們清楚，長官已經向超導中心領導打了招呼。這次會議上不能沒有您，實在不行，我們只有把會議延期等您了。」

史強和他的同事沒再說話，轉身下樓了，兩位軍官看著他們走遠，似乎都長出了一口氣。

「這人怎麼這樣兒
"""


sample2 = """
九龍城道8度海逸酒店一款蛋糕，蠟樣芽孢桿菌含量超標。

食物安全中心派員到酒店內一間食肆抽取蛋糕樣本進行檢測，結果顯示，蠟樣芽孢桿菌的含量是指引的130倍，屬不滿意水平。中心已指示暫停出售相關食品，並要求改善生產流程，進行徹底清潔消毒。如足夠證據，將提出檢控。

發言人說，進食含過量蠟樣芽孢桿菌的食物，可能引致嘔吐及腹瀉。

"""


parts = textprocessing.split_text_paragraphs(sample)
for p in parts:
    print(p)


#parts = textprocessing.split_text_parts(sample2)
#print( str( parts ) )
#lucky = textprocessing.find_start_end_of_parts(sample2,parts)
#print( str(  textprocessing.find_start_end_of_parts(sample2,parts) ) )

#print(parts[3])
#print(sample2[lucky[3][0]:lucky[3][1] ] )
#id = database.add_ai_question("How did it go?",1,114,0,20)
#print(str(id))
#lst = database.get_unanswered_questions(1)
#print(str(lst))
#database.answer_ai_response(7369,440)

#print( str( textprocessing.length_so_far(2,['er2','tito','black22mail','hiy','devil','joke'])))



