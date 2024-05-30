"""가위바위보로 인하대 일짱 먹기
Made by B15
v 1.0.4
Made in 240504-240513
"""
# 파이썬 최신버전으로 실행시켜주세요 3.12+
import keyboard # keyboard 모듈이 없다면 'pip install keyboard' 를 해주세요
from random import randrange
from time import perf_counter,sleep
import os

SUPPRESS_KEY_EVENTS = True # 게임 중 키보드/마우스휠을 사용하고 싶으면, False로 바꿔주세요. // 게임몰입을 방해할 수 있습니다.

class Game:
    class FPS:
        target:int
        lstrec:int
        fps:int
        def __init__(self,tgt:int=60):
            self.target = tgt
            self.fps = self.target
            self.lstrec=perf_counter()
            pass
        def calcFps(self)->int:
            tm = perf_counter()-self.lstrec
            if tm<1/self.target:
                sleep(1/self.target-tm)
                self.fps = self.target
                self.lstrec=perf_counter()
                return self.fps
            self.fps = 1/tm
            self.lstrec=perf_counter()
            return self.fps
        pass
    class Controls:
        hookedKeys:dict
        keyPressed:set
        actkeys:set
        def __init__(self):
            self.hookedKeys = dict()
            pass
        def setToDefDict(st:set,bset=False)->dict:
            dct = dict()
            for key in list(st):
                dct[key]=bset
            return dct
        def _managePress(self,eve:keyboard.KeyboardEvent):
            if eve.name in self.actkeys and eve.name not in self.keyPressed:
                self.keyPressed.add(eve.name)
            pass
        def _manageReles(self,eve:keyboard.KeyboardEvent):
            if eve.name in self.actkeys:
                self.keyPressed.discard(eve.name)
            pass
        def iniWFI(self):
            self.keyPressed=set()
            self.actkeys={'up','w','down','s','left','a','right','d','enter','esc'}
            keyboard.on_press(self._managePress,suppress=SUPPRESS_KEY_EVENTS)
            keyboard.on_release(self._manageReles,suppress=SUPPRESS_KEY_EVENTS)
            pass
        def waitForInput(self)->str:
            self.keyPressed = set()
            while len(self.keyPressed)==0:
                pass
            return list(self.keyPressed)[0]
        def hookKeyboardEvent(self,key:str,func): #unused
            id = keyboard.on_press_key(key, func,suppress=SUPPRESS_KEY_EVENTS)
            self.hookedKeys[key]=id
            pass
        def hookKeyboardEvents(self,funcs:dict): #unused
            for key,func in funcs.items():
                id = keyboard.on_press_key(key, func,suppress=SUPPRESS_KEY_EVENTS)
                self.hookedKeys[key]=id
            pass
        def unhookKeyboardEvent(self,key:str): #unused
            if key in self.hookedKeys.keys():
                keyboard.unhook(self.hookedKeys[key])
                self.hookedKeys.pop(key)
            pass
        def unhookAllKeyboardEvents(self=None):
            keyboard.unhook_all()
            if self==None:
                return
            self.hookedKeys = dict()
            pass
        def hookKeysToFlags(flags:dict[str,bool]):
            Game.Controls.unhookAllKeyboardEvents()
            def togOn(k:keyboard.KeyboardEvent):
                flags[k.name]=True
            def togOff(k:keyboard.KeyboardEvent):
                flags[k.name]=False
                pass
            for key in flags.keys():
                keyboard.on_press_key(key,togOn,suppress=True)
                keyboard.on_release_key(key,togOff,suppress=True)
            pass
        pass
    class Assets:
        DEFAULTROW="""\
#                                        #\
"""
        MAIN="""\
##########################################
#                                        #
#                                        #
#                게임시작                #
#                                        #
#                                        #
#                게임설명                #
#                                        #
#                                        #
#                 나가기                 #
#                                        #
#                                        #
#       (wasd/방향키 + Enter 사용)       #
#                                        #
#                                        #
##########################################
"""
        MAIN2="""\
##########################################
#                                        #
#                                        #
#                게임시작                #
#                                        #
#                                        #
#               게임설명(new)            #
#                                        #
#                                        #
#                 나가기                 #
#                                        #
#                                        #
#       (wasd/방향키 + Enter 사용)       #
#                                        #
#                                        #
##########################################
"""
        MN_SEL_STRT="""\
\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\
#               >게임시작<               #
\n\n\n\n\n\n\n\n\n\n\n\n\
"""
        MN_SEL_EXPL="""\
\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\
#               >게임설명<               #
\n\n\n\n\n\n\n\n\n\
"""
        MN_SEL_EXIT="""\
\033[F\033[F\033[F\033[F\033[F\033[F\033[F\
#                >나가기<                #
\n\n\n\n\n\n\
"""
        EXPLANATION="""\
##########################################
#                                        #
#   당신은 오늘도 인하대 앞에 섰습니다.  #
#     오늘이야말로 인하대 가위바위보     #
#         일인자를 먹을것입니다.         #
#                                        #
#  23년 기준 인하대의 재학생(학부생)수는 #
#          총 17,798명 입니다.           #
#    즉 가위바위보를 9번 연속 이기면     #
#당신은 이 학교의 일인자가 되는 것입니다.#
#                                        #
#                                        #
#     자 그럼 가위바위보를 시작하죠.     #
#                                        #
#  ENTER를 눌러 메인화면으로 돌아가세요. #
##########################################\
"""
        EXPLANATION2="""\
##########################################
#                                        #
#   당신은 오늘도 인하대 앞에 섰습니다.  #
#     오늘이야말로 인하대 가위바위보     #
#         일인자를 먹을것입니다.         #
#                                        #
#  23년 기준 인하대의 재학생(학부생)수는 #
#          총 17,798명 입니다.           #
#    즉 가위바위보를 9번 연속 이기면     #
#당신은 이 학교의 일인자가 되는 것입니다.#
#         당신은 지난 패배로부터         #
#        새로운 스킬을 배웠습니다.       #
#     자 그럼 가위바위보를 시작하죠.     #
#                                        #
#  ENTER를 눌러 메인화면으로 돌아가세요. #
##########################################\
"""
        EXPLANATION3="""\
##########################################
#                                        #
#   당신은 오늘도 인하대 앞에 섰습니다.  #
#     오늘이야말로 인하대 가위바위보     #
#         일인자를 먹을것입니다.         #
#                                        #
#  23년 기준 인하대의 재학생(학부생)수는 #
#          총 17,798명 입니다.           #
#    즉 가위바위보를 9번 연속 이기면     #
#당신은 이 학교의 일인자가 되는 것입니다.#
#  당신은 이제 더 배울 스킬이 없습니다.  #
#                                        #
#     자 그럼 가위바위보를 시작하죠.     #
#                                        #
#  ENTER를 눌러 메인화면으로 돌아가세요. #
##########################################\
"""
        def NUMBERS(num):
            numstext = [
'''\
 _____ 
|  _  |
| |/' |
|  /| |
\ |_/ /
 \___/ \
''',
'''\
 __  
/  | 
`| | 
 | | 
_| |_
\___/\
''',
'''\
 _____ 
/ __  \\
`' / /'
  / /  
./ /___
\_____/\
''',
'''\
 _____ 
|____ |
    / /
    \ \\
.___/ /
\____/ \
''',
'''\
   ___ 
  /   |
 / /| |
/ /_| |
\___  |
    |_/\
''',
'''\
 _____ 
|  ___|
|___ \\ 
    \ \\
/\__/ /
\____/ \
''',
'''\
  ____ 
 / ___|
| /___ 
| ___ \\
| \_/ |
\_____/\
''',
'''\
 _____ 
|___  /
   / / 
  / /  
./ /   
\_/    \
''',
'''\
 _____ 
|  _  |
 \ V / 
 / _ \ 
| |_| |
\_____/\
''',
'''\
 _____ 
|  _  |
| |_| |
\____ |
.___/ /
\____/ \
''',
            ]
            fintxt = ""
            nums = list(map(int,str(num)))
            for h in range(6):
                for n in nums:
                    fintxt+=numstext[n].split('\n')[h]
                fintxt+='\n'
                pass
            return fintxt
        def CENTERNUMS(num):
            fintxt = ''
            txt = Game.Assets.NUMBERS(num)
            TOTLN = 40
            incln = TOTLN-len(txt.split('\n')[0])
            for t in txt.rstrip('\n').split('\n'):
                fintxt += '#'+' '*((incln+1)//2)+t+' '*(incln//2)+'#\n'
            return fintxt
        def LOADING_DAY(day):
            return f"""\
##########################################
#           ______  _____   __           #
#           |  _  \/ _ \ \ / /           #
#           | | | / /_\ \ V /            #
#           | | | |  _  |\ /             #
#           | |/ /| | | || |             #
#           |___/ \_| |_/\_/             #
#                                        #
{Game.Assets.CENTERNUMS(day)}\
#                                        #
##########################################
"""
        def LOADING_TURN(turn):
            return f"""\
##########################################
#                                        #
#       ______ __  __ ____   _   __      #
#      /_  __// / / // __ \ / | / /      #
#       / /  / / / // /_/ //  |/ /       #
#      / /  / /_/ // _, _// /|  /        #
#     /_/   \____//_/ |_|/_/ |_/         #
#                                        #
{Game.Assets.CENTERNUMS(turn)}\
#                                        #
##########################################
"""
        def GAME_INPUT(tm:int,orsp:str,sel:int,rspsel:int,seltm:int):
            tms = f"00{tm}"[-3:]
            rspt = (Game.Assets.OBAWI if orsp==0 else Game.Assets.OGAWI if orsp==1 else Game.Assets.OBOJA).split('\n')
            return f"""\
\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F\
##########################################
#{rspt[0]}          |             |#
#{rspt[1]}   TIME   |             |#
#{rspt[2]}  <{tms[0:2]}.{tms[2]}>  |             |#
#{rspt[3]}          |             |#
#{rspt[4]}          |             |#
#{rspt[5]}          |             |#
#{rspt[6]}          |             |#
#{rspt[7]}[{'⣿'*seltm+' '*(8-seltm)}]|             |#
#{rspt[8]}          |             |#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|          |             |#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿| {'>' if sel==0 else ' '}{'<' if rspsel==0 else '['}바위{'>' if rspsel==0 else ']'}{'<' if sel==0 else ' '} |             |#
#|⣿⣿⣿⣿⣿⣿⣿⣿ {'>' if sel==3 else ' '}{'<' if rspsel==3 else '['}가위{'>' if rspsel==3 else ']'}{'<' if sel==3 else ' '} (){'>' if sel==1 else ' '}{'<' if rspsel==1 else '['}보자기{'>' if rspsel==1 else ']'}{'<' if sel==1 else ' '}        |#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿| {'>' if sel==2 else ' '}[스킬]{'<' if sel==2 else ' '} |             |#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|          |             |#
##########################################\
"""
        def GAME_SKILLS(skillcnt:int,sel:int,cldn:list[int]=[0,0,0],will:int=0,rng:int=0):
            def SKIL1(cldn,seld):
                return f"# {'>' if seld else ' '}[표정검사]{'<' if seld else ' '}                           #" if cldn == 0 else f"# {'>' if seld else ' '}[표정검사]{'<' if seld else ' '}({cldn})                        #"
            def SKIL2(cldn,seld):
                return f"#  {'>' if seld else ' '}[야바위]{'<' if seld else ' '}                            #" if cldn == 0 else f"#  {'>' if seld else ' '}[야바위]{'<' if seld else ' '}({cldn})                         #"
            def SKIL3(cldn,seld):
                return f"#  {'>' if seld else ' '}[독심술]{'<' if seld else ' '}                            #" if cldn == 0 else f"#  {'>' if seld else ' '}[독심술]{'<' if seld else ' '}({cldn})                         #"
            EXPLS=[[
                '#               상대방의 표정을 토대로   #',
                '#            내지 않을 것을 확인합니다.  #'],
            [   '#           상대방을 속여 두 번 냅니다.  #',
                '#     (본인이 내지 않을 것을 선택합니다.)#'],
            [   '#                 상대방의 마음을 읽어   #',
                '#                   낼 것을 확인합니다.  #']]
            def RES1():
                re = [
                    "#            상대방을 보아하니           #",
                    "#           관심법으로 확인하니          #",
                    "#            자세히 관찰해보니           #",
                    "#               한번 봤더니              #",
                    "#              표정을 봤더니             #"]
                gbb = ["  가위","  바위","보자기"]
                willd=f"#       {gbb[(will+rng%2+1)%3]}를 내지 않을것 같다.       #"
                return f"""\
{re[rng%len(re)]}
{willd}\
"""
            def RES3():
                re = [
                    "#             기억을 살펴보니            #",
                    "#           관심법으로 확인하니          #",
                    "#       상대의 심연에 들여다봤더니       #",
                    "#           심리를 들여다봤더니          #",
                    "#              생각해 봤더니             #",
                    "#             뒷돈을 줘봤더니            #"] # ㅋㅋㅋ
                gbb = ["  가위","  바위","보자기"]
                willd=f"#          {gbb[will]}를 낼 것 같다.          #"
                return f"""\
{re[rng%len(re)]}
{willd}\
"""
            
            # 스킬3 이 스킬1 보다 우선
            return f"""\
##########################################
#                                        #
{Game.Assets.DEFAULTROW if skillcnt<1 else SKIL1(cldn[0],sel==1)}
{Game.Assets.DEFAULTROW if sel==0 else EXPLS[sel-1][0]}
{Game.Assets.DEFAULTROW if skillcnt<2 else SKIL2(cldn[1],sel==2)}
{Game.Assets.DEFAULTROW if sel==0 else EXPLS[sel-1][1]}
{Game.Assets.DEFAULTROW if skillcnt<3 else SKIL3(cldn[2],sel==3)}
#                                        #
{RES3() if cldn[2]==4 else RES1() if cldn[0]==2 else f"{Game.Assets.DEFAULTROW}\n{Game.Assets.DEFAULTROW}"}
#________________________________________#
#  |   스킬을 사용하면 피로하게 되어  |  #
#  |       쿨다운이 생기니 주의!      |  #
#  |    (wasd/방향키 + Enter 사용)    |  #
#  |         (Esc 로 나가기)          |  #
##########################################\
"""
        def GAME_RESULT(rsp:str,orsp:str):
            rspt = (Game.Assets.BAWI if rsp=="바위" else Game.Assets.GAWI if rsp=="가위" else Game.Assets.BOJA).split('\n')
            orspt = (Game.Assets.OBAWI if orsp=="바위" else Game.Assets.OGAWI if orsp=="가위" else Game.Assets.OBOJA).split('\n')
            lst = ["바위","보","가위"]
            p = lst.index(rsp);op = lst.index(orsp)
            wl = (p-op)%3
            return f"""\
##########################################
#{orspt[0]}          |             |#
#{orspt[1]}    {"   " if wl==0 else "YOU"}   |             |#
#{orspt[2]}   {"TIE!" if wl==0 else "Win!" if wl==1 else "Lose"}   |             |#
#{orspt[3]}          |             |#
#{orspt[4]}          |             |#
#{orspt[5]}          {rspt[0]}#
#{orspt[6]}          {rspt[1]}#
#{orspt[7]}          {rspt[2]}#
#{orspt[8]}          {rspt[3]}#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|          {rspt[4]}#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|          {rspt[5]}#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|          {rspt[6]}#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|  Enter을 {rspt[7]}#
#|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|눌러주세요{rspt[8].rstrip()}#
##########################################\
"""
        SCREEN="""\
##########################################
#                                        #
#                                        #
#            본 파일(게임)은             #
#  파이썬콘솔로 켜시는 것을 권장합니다.  #
#     IDE로 키는건 버그픽스나 디버깅     #
#      리메이킹 용으로 사용해주시길.     #
#                                        #
#     게임 중에는 키/마우스휠 입력이     #
#      씹힐 수 있으니, 조심해주세요.     #
# 이기능을 정지하려면, IDE에서 꺼주세요. #
#                                        #
#      화면을 이 테두리에 맞추시고       #
#    완료되셨다면 Enter을 눌러주세요.    #
#                                        #
##########################################
"""
        OGAWI="""\
|⣿⣿⣿⣿⣿⣭⣭⣭⣭⣽⣿⣿⣿|
|⣿⣿⣿⡏⢰⣶⣶⣶⣶⣶⢸⣿⣿|
|⣿⣿⡿⢃⣿⣿⡏⢹⣿⣿⡘⣿⣿|
|⣿⡏⣰⡟⠿⢯⣴⡿⠿⣿⣿⢸⣿|
|⣿⣇⠻⠿⠿⠆⡏⢰⣷⢠⣦⢸⣿|
|⣿⣿⡇⣿⡇⠸⡇⢸⣿⠸⣿⢸⣿|
|⣿⣿⡇⣿⡇⢀⢻⣌⠩⣶⣶⣾⣿|
|⣿⣿⡇⣿⡇⢸⠈⣿⡆⣿⣿⣿⣿|
|⣿⣿⣷⣮⣴⣿⣷⣬⣴⣿⣿⣿⣿|\
"""
        OBAWI="""\
|⣿⣿⣿⣿⣿⣭⣭⣭⣭⣽⣿⣿⣿|
|⣿⣿⣿⡏⢰⣶⣶⣶⣶⣶⠘⣿⣿|
|⣿⣿⣿⠇⣼⣿⣿⢹⣿⣿⡈⣿⣿|
|⣿⡟⣡⡿⣿⣿⣡⣿⣿⣿⣿⠈⣿|
|⣿⡇⣿⣷⣆⡀⣆⢁⣆⠹⠿⠀⣿|
|⣿⣧⡉⣉⡉⢁⣿⢸⣿⢰⣿⠀⣿|
|⣿⣿⡇⢿⠇⢸⣿⢸⣿⠸⠿⢀⣿|
|⣿⣿⣿⣶⣶⣦⣥⣦⣥⣶⣶⣿⣿|
|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|\
"""
        OBOJA="""\
|⣿⣿⣿⣿⣿⡯⠭⠭⠭⠽⣿⣿⣿|
|⣿⣿⣿⣿⡇⣾⣿⣿⣿⣷⢸⣿⣿|
|⣿⣿⣿⢟⣥⣿⡿⣸⣿⣿⡜⣿⣿|
|⣿⠟⣥⡾⢛⣿⣷⣿⣿⣿⡇⣾⣿|
|⣿⣦⣛⡁⣾⡟⣿⢛⣿⢻⡇⣻⣿|
|⣿⣿⣿⡇⣿⡇⣿⠸⣿⢸⡇⣻⣿|
|⣿⣿⣿⡇⢻⡇⣿⠘⡿⢰⣵⣿⣿|
|⣿⣿⣿⣿⣶⣶⣭⣴⣾⣿⣿⣿⣿|
|⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿|\
"""
        GAWI="""\
| ⠀⠀⠀⣀⣤⡀⠀⣠⣄⡀⠀ |
| ⠀⠀⠀⣧⠀⢿⢸⡇⠀⡇⠀ |
| ⠀⣀⣀⡼⢤⡘⣾⡇⠀⡇⠀ |
| ⢸⠁⢹⠀⢸⡇⢹⡇⠀⡇⠀ |
| ⢸⣄⣼⡀⢸⠇⣏⠉⠉⠙⡆ |
| ⢸⡀⠀⠉⠉⣠⠍⠉⠃⣠⠇ |
| ⠀⢳⠀⠀⠸⠇⠀⠀⡞⠁⠀ |
| ⠀⢸⡄⠀⠀⠀⠀⢠⡇⠀⠀ |
| ⠀⠀⠩⠭⠭⠭⠭⠉⠀⠀⠀ |\
        """
        BAWI="""\
|             |
| ⠀⣀⣀⡤⢄⡤⢤⣀⣀⠀⠀ |
| ⣾⠉⢹⠀⢸⡁⢸⡏⠈⡇⠀ |
| ⣿⠀⢸⠀⢸⠀⡾⠷⠶⠷⡄ |
| ⣿⠉⠹⣆⡾⢇⣷⣀⣀⠀⡇ |
| ⢻⡀⠀⠀⠀⡴⠂⠀⠉⣠⠃ |
| ⠀⢳⠀⠀⠘⠇⠀⢠⡞⠁⠀ |
| ⠀⠸⣄⣀⣀⣀⣀⣸⠇⠀⠀ |
| ⠀⠀⠠⠤⠤⠤⠤⠄⠀⠀⠀ |\
        """
        BOJA="""\
|             |
|  ⠀⠀⢀⣠⠤⣄⣀⠀⠀⠀ |
|  ⣠⢴⠃⢹⠀⡏⠈⡇⠀⠀ |
|  ⡇⢸⠀⢸⠀⡇⠀⡇⠀⠀ |
|  ⡇⠘⠀⠘⠀⠓⢀⡷⠒⢤ |
|  ⡇⠀⠀⠀⠀⠀⠚⠁⡠⠊ |
|  ⢣⡀⠀⢰⠉⠀⡠⠊⠀⠀ |
|  ⠀⡇⠀⠀⠀⠀⡇⠀⠀⠀ |
|  ⠀⠈⠭⠭⠭⠍⠀⠀⠀⠀ |\
        """
        RLYEXIT="""\
##########################################
#                                        #
#                                        #
#                                        #
#         게임을 나가시겠습니까?         #
#                                        #
#                                        #
#                                        #
#           게임종료  돌아가기           #
#            Enter  /   Esc              #
#                                        #
#                                        #
#                                        #
#                                        #
#                                        #
##########################################\
"""
        def TOMARROW():
            quotes=[
                "           하지만 괜찮습니다.           ",
                "   오늘의 패배로 배운것이 있을겁니다.   ",
                "  당신의 야망은 여기서 그치지 않습니다. ",
                " 당신은 도망친게 아닌 빛을 찾아 갔을뿐. ",
                "모든 원인은 하나 이상의 결과를 낳습니다.",
                "당신이 뿌린 일은 당신에게 되돌아 옵니다.",
                "        태만은 천천히 움직입니다.       ",
                "           (대충 멋있는 명언)           ",
                "     시작했으니 대충 살지 마십시오.     ",
                "               (대충 찔림)              ",
                "        당신은 오늘도 배웠습니다.       "
            ]
            tom=[
                "         내일은 또다른 날입니다.        ",
                "    오늘의 희망은 내일의 현실입니다.    ",
                "        어제를 후회하지 마십시오.       ",
                "      과거는 갔고 미래는 모릅니다.      ",
                "          실패를 두려워 마세요.         "
            ]
            dq = []
            for _ in range(3):
                dq.append(quotes.pop(randrange(len(quotes))))
            dt = tom[randrange(len(tom))]
            return f"""\
##########################################
#                                        #
#                                        #
#          당신은 패배했습니다.          #
#                                        #
#                                        #
#{dq[0]}#
#{dq[1]}#
#{dq[2]}#
#                                        #
#{dt}#
#                                        #
#                                        #
#  ENTER를 눌러 메인화면으로 돌아가세요. #
#                                        #
##########################################\
"""
        pass
        def GAME_RESULT2(wins:int,wonplyrs:int):
            st = '총 '+str(wonplyrs)+' 명을 제쳤습니다.'
            fst = '               ' + st + '               '
            fst = fst[len(fst)//2-13:len(fst)//2+13]
            return f"""\
##########################################
#                                        #
{Game.Assets.CENTERNUMS(wins)}\
#                                        #
#         명을 상대로 이겼습니다.        # 
#________________________________________#
#  |                                  |  #
#  |{fst}|  #
#  |        Enter을 눌러주세요        |  #
#  |                                  |  #
##########################################\
"""
    
    FLAGS:dict
    cntr:Controls
    gamefps:FPS
    def __init__(self):
        self.FLAGS={
            "playing":1,
            "skills":0,
            "days":1,
        }
        self.cntr = Game.Controls()
        self.gamefps = self.FPS()
        self._redrawScrn(Game.Assets.SCREEN)
        input()
        while self.FLAGS["playing"]:
            self._mainScrn()
            pass
        self._redrawScrn('')
        pass
    def _mainScrn(self):
        self.cntr.iniWFI()
        sel = 0
        while True:
            if self.FLAGS["days"] in {2,5}:
                self._redrawScrn(Game.Assets.MAIN2)
            else:
                self._redrawScrn(Game.Assets.MAIN)
            if sel==0:
                self._drawScrn(Game.Assets.MN_SEL_STRT)
            elif sel==1:
                self._drawScrn(Game.Assets.MN_SEL_EXPL)
            elif sel==2:
                self._drawScrn(Game.Assets.MN_SEL_EXIT)
                pass
            inp = self.cntr.waitForInput()
            if inp in {'w','a','up','left'}:
                sel=sel if sel==0 else sel-1
            elif inp in {'s','d','down','right'}:
                sel=sel if sel==2 else sel+1
            elif inp == 'enter':
                if sel==0:
                    self._startGame()
                    pass
                elif sel==1:
                    self._gameExpl()
                    while self.cntr.waitForInput() != 'enter':
                        pass
                    pass
                elif sel==2:
                    self._exit()
                    return
                pass
            pass
        ...
    def _redrawScrn(self,todraw:str=""):
        os.system('cls')
        self._drawScrn(todraw)
    def _drawScrn(self,todraw:str):
        print(todraw,end='')
        pass
    def _startGame(self):
        OPENINGTIME = 0.8
        turn = 0
        wins = 0
        wnplyr = 0
        sklcdns = [0,0,2] #스킬 쿨다운
        self._redrawScrn(Game.Assets.LOADING_DAY(self.FLAGS["days"]))
        sleep(OPENINGTIME)
        while True:
            turn+=1
            self._redrawScrn(Game.Assets.LOADING_TURN(turn))
            sleep(OPENINGTIME)
            self._redrawScrn()
            stt = perf_counter()
            sel = 0
            rspsel = sel
            orspn = randrange(3)
            orsp = randrange(3)
            state = 0
            sklcdns = list(map(lambda x:0 if x<2 else x-1,sklcdns))
            seltm = 0
            seld = False
            rng1000 = randrange(1000)
            
            KEYS = Game.Controls.setToDefDict({'w','a','s','d','up','left','down','right','enter','esc'})
            Game.Controls.hookKeysToFlags(KEYS)
            while True: # 가위바위보
                tm = perf_counter()-stt
                seltm = seltm+2 if seld else 0
                if tm>60 or seltm>230:
                    break
                if state == 0:
                    self._drawScrn(Game.Assets.GAME_INPUT(int((60-tm)*10),orspn,sel,rspsel,(seltm+29)//30))
                    if int(tm)%2:
                        orspn = randrange(3)
                    seld = False
                    if KEYS['enter']:
                        if sel == 2:
                            state=1
                            sel = 0 if self.FLAGS["skills"] == 0 else 1 #스킬 있으면 1로 없으면 0으로
                            self._redrawScrn(Game.Assets.GAME_SKILLS(self.FLAGS["skills"],sel,sklcdns,orsp,rng1000))
                            KEYS['enter'] = False
                        else:
                            seld = True
                            rspsel = sel
                        pass
                    elif KEYS['w'] or KEYS['up']:
                        if seltm==0:
                            sel = 0
                    elif KEYS['a'] or KEYS['left']:
                        if seltm==0:
                            sel = 3
                    elif KEYS['s'] or KEYS['down']:
                        if seltm==0:
                            sel = 2
                    elif KEYS['d'] or KEYS['right']:
                        if seltm==0:
                            sel = 1
                    elif KEYS['esc']:
                        pass
                elif state == 1:
                    if KEYS['w'] or KEYS['up']:
                        if self.FLAGS["skills"]!=0:
                            sel = 1 if sel==1 else sel-1
                            self._redrawScrn(Game.Assets.GAME_SKILLS(self.FLAGS["skills"],sel,sklcdns,orsp,rng1000))
                            KEYS['w']=False
                            KEYS['up']=False
                    elif KEYS['s'] or KEYS['down']:
                        if self.FLAGS["skills"]!=0:
                            sel = self.FLAGS["skills"] if sel==self.FLAGS["skills"] else sel+1
                            self._redrawScrn(Game.Assets.GAME_SKILLS(self.FLAGS["skills"],sel,sklcdns,orsp,rng1000))
                            KEYS['s']=False
                            KEYS['down']=False
                    elif KEYS['enter']:
                        if sel==1 and sklcdns[0]==0:
                            sklcdns[0]=2
                            pass
                        elif sel==2 and sklcdns[1]==0:
                            sklcdns[1]=3
                            pass
                        elif sel==3 and sklcdns[2]==0:
                            sklcdns[2]=4
                            pass
                        self._redrawScrn(Game.Assets.GAME_SKILLS(self.FLAGS["skills"],sel,sklcdns,orsp,rng1000))
                        pass
                    elif KEYS['esc']:
                        state=0
                        pass
                self.gamefps.calcFps()
                pass
            rsp = ["바위","보","ㅋㅋ","가위"][rspsel]
            orsp = ["가위","바위","보"][orsp]
            dct = self._whoWon(rsp,orsp,sklcdns)
            
            self._redrawScrn(Game.Assets.GAME_RESULT(dct["rsp"],dct["orsp"]))
            while KEYS['enter']==True:
                self.gamefps.calcFps()
            Game.Controls.unhookAllKeyboardEvents()
            self.cntr.iniWFI()
            self.cntr.waitForInput()
            
            if dct['win']:
                wins += 1
                wnplyr = 3 if wnplyr==0 else wnplyr*3
            elif not dct['lose']:
                wnplyr += 2 if wnplyr==0 else wnplyr//3
            self._redrawScrn(self.Assets.GAME_RESULT2(wins,wnplyr))
            self.cntr.waitForInput()
            
            if dct['lose']:
                break
            pass
        self.FLAGS['skills'] = 3 if self.FLAGS['skills']==3 else self.FLAGS['skills']+1
        self.FLAGS['days']+=1
        self._redrawScrn(self.Assets.TOMARROW())
        self.cntr.waitForInput()
        pass
    def _whoWon(self,rsp:str,orsp:str,sklcdns:list[int])->dict:
        dct = {'win':False,'rsp':rsp,'orsp':orsp,'lose':False}
        lst = ["바위","보","가위"]
        wl:int
        if sklcdns[1]==3:
            p = lst.index(rsp);op = lst.index(orsp)
            wl = ~((p-op)%3==1)
            if wl:
                dct['rsp'] = lst[(op+1)%3]
            else:
                dct['rsp'] = lst[(p+1)%3]
                dct['lose']=True
        else:
            p = lst.index(rsp);op = lst.index(orsp)
            wl = (p-op)%3==1
            dct['lose'] = (p-op)%3==2
            pass
        dct['win'] = wl
        return dct
    def _gameExpl(self):
        if self.FLAGS['days']==1:
            self._redrawScrn(Game.Assets.EXPLANATION)
        elif 1<self.FLAGS['days']<5:
            self._redrawScrn(Game.Assets.EXPLANATION2)
        else:
            self._redrawScrn(Game.Assets.EXPLANATION3)
        pass
    def _exit(self):
        self._redrawScrn(Game.Assets.RLYEXIT)
        while True:
            inp = self.cntr.waitForInput()
            if inp=='enter':
                self.FLAGS["playing"] = 0
                break
            elif inp=='esc':
                break
        pass
    pass

if __name__ == "__main__":
    Game()
    pass
