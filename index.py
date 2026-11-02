import math
import random
import sys
import tkinter as tk
from tkinter import font as tkfont

# ───────────── الإعدادات ─────────────
W, H = 860, 720          # حجم النافذة
CX, CY, SC = 430, 300, 21  # مركز القلب وحجمه
TICK = 16                # ms بين كل فريم
RATE = 0.55              # كم كلمة تظهر بكل فريم
FADE = 34                # عدد فريمات الظهور التدريجي
DRIFT = 10               # مسافة الحركة الخفيفة عند الظهور
BG = (0, 0, 0)
REDS = [(255, 72, 60), (240, 58, 50), (255, 98, 82), (225, 50, 46)]
WHITE_LOVE = (236, 222, 255)   # لون "I love you"
SHINE = (255, 232, 226)        # لون اللمعة

FAMILY = "Segoe UI" if sys.platform.startswith("win") else (
    "Helvetica Neue" if sys.platform == "darwin" else "DejaVu Sans")

PHRASES = [
    "I love you", "Je t'aime", "Te amo", "Ich liebe dich", "Ti amo",
    "Eu te amo", "Я тебя люблю", "Я тебе кохаю", "Обичам те", "Волим те",
    "Volim te", "Ljubim te", "Ľúbim ťa", "Kocham cię", "Miluji tě",
    "Szeretlek", "Te iubesc", "Mahal kita", "Aku cinta kamu", "Anh yêu em",
    "愛してる", "我爱你", "사랑해", "أحبك", "دوستت دارم",
    "میں تم سے پیار کرتا ہوں", "אני אוהב אותך", "Seni seviyorum",
    "मैं तुमसे प्यार करता हूँ", "म तिमीलाई माया गर्छु",
    "আমি তোমাকে ভালোবাসি", "நான் உன்னை காதலிக்கிறேன்",
    "నేను నిన్ను ప్రేమిస్తున్నాను", "ನಾನು ನಿನ್ನನ್ನು ಪ್ರೀತಿಸುತ್ತೇನೆ",
    "ഞാൻ നിന്നെ സ്നേഹിക്കുന്നു", "ฉันรักเธอ", "ខ្ញុំស្រលាញ់អ្នក",
    "ကျွန်တော် မင်းကို ချစ်တယ်", "მე შენ მიყვარხარ", "Σ' αγαπώ",
    "Ég elska þig", "Jeg elsker deg", "Jag älskar dig", "Minä rakastan sinua",
    "Ek is lief vir jou", "Ik hou van jou", "Të dua", "Te quiero", "T'estimo",
    "Mo nífẹ̀ rẹ", "Nakupenda", "Ngiyakuthanda", "Waan ku jeclahay",
    "Ndinokuda", "Maite zaitut", "Ma armastan sind", "Mīlu tevi",
    "Aš tave myliu", "Dw i'n dy garu di", "Tá grá agam duit", "Men seni sevaman",
    "Мен сені жақсы көремін", "Би чамд хайртай", "Səni sevirəm", "Quérote",
    "Hụrụ m gị n'anya", "Mwen renmen w", "Aloha au iā 'oe", "Ke a go rata",
    "ਮੈਂ ਤੈਨੂੰ ਪਿਆਰ ਕਰਦਾ ਹਾਂ", "હું તને પ્રેમ કરું છું", "මම ඔබට ආදරෙයි",
    "ຂ້ອຍຮັກເຈົ້າ", "Inħobbok", "Ech hunn dech gär", "Mi amas vin",
    "Ana behebak", "Ja te volim",
]
PHRASES = PHRASES[:75]


# ───────────── أدوات الألوان ─────────────
def hx(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in c)


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


# ───────────── شكل القلب ─────────────
def heart_pt(t, k=1.0):
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return CX + x * SC * k, CY - y * SC * k


POLY = [heart_pt(2 * math.pi * i / 600) for i in range(600)]


def inside(px, py):
    n, ok, j = len(POLY), False, len(POLY) - 1
    for i in range(n):
        xi, yi = POLY[i]
        xj, yj = POLY[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            ok = not ok
        j = i
    return ok


# ───────────── النافذة ─────────────
root = tk.Tk()
root.title("Love Heart")
root.geometry(f"{W}x{H}")
root.configure(bg="black")
cv = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
cv.pack(fill="both", expand=True)


# ───────────── توزيع الكلمات داخل القلب ─────────────
def build_layout():
    placed_rects, layout = [], []
    cycle = []

    def next_phrase():
        nonlocal cycle
        if not cycle:
            cycle = PHRASES[:]
            random.shuffle(cycle)
        return cycle.pop()

    def fits(x, y, w, h):
        x0, y0, x1, y1 = x - w / 2 - 2, y - h / 2 - 1, x + w / 2 + 2, y + h / 2 + 1
        for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            if not inside(cx, cy):
                return False
        for a0, b0, a1, b1 in placed_rects:
            if x0 < a1 and x1 > a0 and y0 < b1 and y1 > b0:
                return False
        placed_rects.append((x0, y0, x1, y1))
        return True

    def try_place(x, y, size_range):
        text = next_phrase()
        size = random.randint(*size_range)
        for s in (size, max(6, size - 2)):
            f = tkfont.Font(family=FAMILY, size=s, weight="bold")
            w, h = f.measure(text), f.metrics("linespace")
            if fits(x, y, w, h):
                return (x, y, text, (FAMILY, s, "bold"))
        return None

    # حلقات من الخارج للداخل، تبدأ من أعلى القلب وتمشي مع عقارب الساعة
    k = 0.95
    while k > 0.07:
        for i in range(420):
            t = 2 * math.pi * i / 420
            x, y = heart_pt(t, k)
            r = try_place(x, y, (8, 12))
            if r:
                layout.append(r)
        k -= 0.05

    # سد الفراغات الصغيرة
    pts = [(x, y) for y in range(40, 680, 9) for x in range(60, 800, 9) if inside(x, y)]
    random.shuffle(pts)
    for x, y in pts:
        r = try_place(x, y, (6, 8))
        if r:
            layout.append(r)

    # "I love you" الأبيض بالنص
    layout.append(try_place(CX, CY + 10, (13, 13)) or (CX, CY + 10, "I love you", (FAMILY, 13, "bold")))
    return layout


LAYOUT = build_layout()
items = iter(LAYOUT)

# ───────────── الحركة ─────────────
active = []        # الكلمات الي لسا عم تظهر
settled = {}       # id -> (x, لونها الأساسي)
spawning = True
acc = 0.0
phase = 0


def spawn(entry):
    x, y, text, fnt = entry
    base = WHITE_LOVE if text == "I love you" else random.choice(REDS)
    i = cv.create_text(x, y + DRIFT, text=text, font=fnt, fill=hx(BG))
    active.append({"id": i, "x": x, "y": y, "t": 0, "c": base})


def _safe(i, c):
    try:
        cv.itemconfig(i, fill=hx(c))
    except Exception:
        pass


def animate(p):
    p["t"] += 1
    a = min(1.0, p["t"] / FADE)
    e = 1 - (1 - a) ** 3                      # easing
    _safe(p["id"], lerp(BG, p["c"], e))
    try:
        cv.coords(p["id"], p["x"], p["y"] + (1 - e) * DRIFT)
    except Exception:
        pass
    if a >= 1.0:
        settled[p["id"]] = (p["x"], p["c"])
        return False
    return True


def shimmer():
    global phase
    phase += 7
    pos = (phase % (W + 500)) - 250
    for i, (x, base) in settled.items():
        d = abs(x - pos) / 110
        k = max(0.0, 1 - d)
        _safe(i, lerp(base, SHINE, k * 0.85))
    cv.after(TICK, shimmer)


def step():
    global acc, spawning
    if spawning:
        acc += RATE
        try:
            while acc >= 1:
                acc -= 1
                spawn(next(items))
        except StopIteration:
            spawning = False

    active[:] = [p for p in active if animate(p)]

    if not spawning and not active:
        shimmer()
        return
    cv.after(TICK, step)


step()
root.mainloop()
