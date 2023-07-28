
import aisocketapi
import api
import constants

def batchprocess_text(all_of_it,splitfunction,processfunction):
    # Open a file: file
    total = ''
    print(" batchprocess text - length of text: " + str(len(all_of_it)))
    splitparts = splitfunction(all_of_it)
    for i in splitparts:
        print("batchprocess_text processing one part")
        newt = processfunction(i)
        print("batchprocess_text processing one part processed !")        
        total = total + newt
    return total

def splitfunction(txt):
    maxlen = 60
    ret = []
    pos = 0
    lastpos = 0
    print(splitfunction)
    while pos < len(txt):
        pos += 1
        if (pos - lastpos) > maxlen:
            while (txt[pos] != '。' and pos < len(txt)):
                pos += 1
            print("adding a split " + str(pos))
            ret.append(txt[lastpos:pos])
            lastpos = pos
    ret.append(txt[lastpos:pos])
    print("number of splits " + str(len(ret))) 
    return ret

def simplifyfunction(txt):
    return aisocketapi.ask_ai('Rewrite this in chinese using only simple words:' + txt)

def simplify_cws(id):
    thecws = api.get_cws_text(id)
    print("simplify_cws gotten thecws "+ str(thecws.id))
    orgtext = thecws.orgtext
    simpletext = batchprocess_text(orgtext,splitfunction,simplifyfunction)
    newcws = api.process_chinese(thecws.title + ' simplified ','ai',simpletext,constants.CWS_TYPE_IMPORT_TEXT,id) 
    return newcws


print ( splitfunction("""
漁護署繼續跟進西貢海域鯨魚出沒，知悉有意見提出訂立禁船區以保護鯨魚，但鯨魚出沒的地點及時間並不固定及範圍廣闊，涉及水域須按實際情況隨時改變，因此在不影響其他海上使用人士的情況下，執行上並不可行。漁護署表示，會聯同警方及海事處等部門加強巡邏，每當發現鯨魚露出水面覓食而有船隻太過接近鯨魚，在場的政府人員會即時採取適當行動，包括指示有關船隻與鯨魚保持距離。若相關人士拒絕合作則會進行執法，以確保鯨魚不會受到觀鯨船隻滋擾。

署方與海洋公園保育基金及其他保育團體的專家同意鯨魚背部的傷痕並非近期受傷所致。由於鯨魚情況穩定，有能力進食及游動，傷口亦在癒合，未有患病及擱淺的行為表現，因此現時並沒有需要作出救治或其他介入行動。

對於有建議引領鯨魚游向外海，署方與一眾專家商討後，仍未找到穩妥安全及合適的具體可行方案。漁護署會繼續與專家探討合適及有效方法。

漁護署重申，所有鯨豚動物均受《野生動物保護條例》保護，不負責任的觀鯨行為可能構成故意干擾受保護野生動物罪，違者一經定罪，最高可被判監禁1年及罰款10萬元。
""") )