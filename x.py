from jh_server.apps.jidou_hikki.models import *
from jh_server.apps.jidou_hikki.utils.sudachi import *

t1 = "適当に歩き回ってたら、不意のエンカウントでデッドエンドの未来しか見えない"
t2 = "そもそもさー、私生まれ変わる前は「運動？　何それ？」ってタイプのインドア派よ？"
t3 = "そりゃ、野生の蜘蛛の方が運動能力高いに決まってるじゃん。"
t4 = "私が人に誇れる運動能力なんて、ゲームで鍛えた親指の動きくらいだって。"

t = """このダンジョンからの脱出は諦めた。

　適当に歩き回ってたら、不意のエンカウントでデッドエンドの未来しか見えない。

　魔物にしろ、人間にしろ、今の私には等しく強敵だ。

　強敵と書いて、ライバル、とか、とも、とか読まない。

　正真正銘命の危険が危ないってやつだ。


　幸い、というのかなんなのか、この狭い通路に出現する魔物は、そんなに素早いやつはいないっぽい。

　でなきゃ、私が逃げ切れるわけないし。
"""


def foo(t):
    a = Tokenizer.from_text(t, MODE_A)
    b = Tokenizer.from_text(t, MODE_B)
    c = Tokenizer.from_text(t, MODE_C)
    print(a)
    print(b)
    print(c)
    breakpoint()
