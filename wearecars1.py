"""
WeAreCars - Car Rental Management System 
"""

import tkinter as tk
from tkinter import ttk
import json, os, re
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  DATA STORE
# ─────────────────────────────────────────────────────────────────────────────
BOOKINGS_FILE = "wearecars_bookings.json"

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return []

def save_bookings(data):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

bookings = load_bookings()

# ─────────────────────────────────────────────────────────────────────────────
#  PRICING
# ─────────────────────────────────────────────────────────────────────────────
BASE_RATE      = 25
CAR_PRICES     = {"City Car": 0, "Family Car": 50, "Sports Car": 75, "SUV": 65}
FUEL_PRICES    = {"Petrol": 0, "Diesel": 0, "Hybrid": 30, "Full Electric": 50}
MILEAGE_RATE   = 10
BREAKDOWN_RATE = 2

# ─────────────────────────────────────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg_dark":  "#1C2333",
    "bg_mid":   "#243044",
    "bg_card":  "#2C3A52",
    "bg_input": "#1E2D42",
    "bg_hover": "#344560",
    "teal":     "#2DD4BF",
    "teal_dim": "#1A9E8F",
    "blue":     "#60A5FA",
    "gold":     "#FBBF24",
    "success":  "#34D399",
    "danger":   "#F87171",
    "text":     "#E2E8F0",
    "text2":    "#94A3B8",
    "text3":    "#64748B",
    "border":   "#334155",
    "white":    "#FFFFFF",
}

FT  = ("Segoe UI", 22, "bold")   # title
FH  = ("Segoe UI", 14, "bold")   # heading
FSH = ("Segoe UI", 11, "bold")   # subheading
FB  = ("Segoe UI", 10)           # body
FSM = ("Segoe UI",  9)           # small
FM  = ("Courier New", 10)        # mono

# ─────────────────────────────────────────────────────────────────────────────
#  NUMERIC VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def _digits_only(P):
    """Allow only digit characters (or empty string for deletion)."""
    return P == "" or P.isdigit()

# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def entry(parent, var=None, width=28, show="", numeric=False):
    vcmd = None
    if numeric:
        vcmd = (parent.winfo_toplevel().register(_digits_only), "%P")
    return tk.Entry(
        parent, textvariable=var, width=width, show=show,
        bg=C["bg_input"], fg=C["text"], insertbackground=C["teal"],
        relief="flat", font=FB,
        highlightthickness=1,
        highlightbackground=C["border"],
        highlightcolor=C["teal"],
        **({"validate": "key", "validatecommand": vcmd} if vcmd else {})
    )

def btn(parent, text, cmd, bg=None, fg=None, width=16, pady=8):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=bg or C["teal"], fg=fg or C["bg_dark"],
        font=FSH, relief="flat",
        activebackground=C["teal_dim"],
        activeforeground=C["white"],
        cursor="hand2", width=width, pady=pady
    )

def hsep(parent, pady=8):
    tk.Frame(parent, height=1, bg=C["border"]).pack(fill="x", pady=pady)

# ─────────────────────────────────────────────────────────────────────────────
#  THEMED DIALOG  (replaces all messagebox calls)
# ─────────────────────────────────────────────────────────────────────────────

class Dialog(tk.Toplevel):
    """Dark-themed modal dialog matching the app palette."""

    def __init__(self, parent, title, message, mode="ok", icon="i", icolor=None):
        super().__init__(parent)
        self.result = False
        self.title(title)
        self.configure(bg=C["bg_dark"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        tk.Frame(self, bg=C["teal"], height=4).pack(fill="x")

        body = tk.Frame(self, bg=C["bg_mid"], padx=26, pady=20)
        body.pack(fill="both", expand=True)

        # Header row
        hdr = tk.Frame(body, bg=C["bg_mid"])
        hdr.pack(fill="x", pady=(0, 12))
        tk.Label(hdr, text=icon, font=("Segoe UI Emoji", 20),
                 fg=icolor or C["teal"], bg=C["bg_mid"]).pack(side="left", padx=(0, 10))
        tk.Label(hdr, text=title, font=FH,
                 fg=C["text"], bg=C["bg_mid"]).pack(side="left")

        hsep(body, pady=4)

        # Message box
        tk.Label(body, text=message, font=FM,
                 fg=C["text"], bg=C["bg_card"],
                 justify="left", padx=14, pady=12,
                 relief="flat").pack(fill="x", pady=(8, 16))

        # Buttons
        br = tk.Frame(body, bg=C["bg_mid"])
        br.pack(anchor="e")

        if mode == "yesno":
            btn(br, "  Yes  ", self._yes,
                bg=C["teal"], fg=C["bg_dark"], width=8).pack(side="left", padx=(0, 8))
            btn(br, "  No   ", self._no,
                bg=C["bg_card"], fg=C["text2"], width=8).pack(side="left")
        elif mode == "error":
            btn(br, "   OK  ", self._yes,
                bg=C["danger"], fg=C["white"], width=8).pack(side="left")
        else:
            btn(br, "   OK  ", self._yes,
                bg=C["teal"], fg=C["bg_dark"], width=8).pack(side="left")

        tk.Frame(self, bg=C["bg_dark"], height=4).pack(fill="x")

        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width()  // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w  = self.winfo_width()
        h  = self.winfo_height()
        self.geometry(f"+{pw - w//2}+{ph - h//2}")
        self.bind("<Return>", lambda e: self._yes())
        self.bind("<Escape>", lambda e: self._no())
        self.wait_window()

    def _yes(self): self.result = True;  self.destroy()
    def _no(self):  self.result = False; self.destroy()


def ask(parent, title, msg, icon="?", icolor=None):
    d = Dialog(parent, title, msg, mode="yesno", icon=icon, icolor=icolor)
    return d.result

def info(parent, title, msg, icon="v"):
    Dialog(parent, title, msg, mode="ok", icon=icon, icolor=C["success"])

def err(parent, title, msg):
    Dialog(parent, title, msg, mode="error", icon="!", icolor=C["danger"])


# ─────────────────────────────────────────────────────────────────────────────
#  SPLASH
# ─────────────────────────────────────────────────────────────────────────────

class Splash(tk.Toplevel):
    def __init__(self, root, on_done):
        super().__init__(root)
        self.on_done = on_done
        self.overrideredirect(True)
        self.configure(bg=C["bg_dark"])
        W, H = 600, 380
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.lift()
        self.attributes("-topmost", True)
        tk.Frame(self, bg=C["teal"], height=5).pack(fill="x")
        body = tk.Frame(self, bg=C["bg_dark"])
        body.pack(fill="both", expand=True)
        c = tk.Frame(body, bg=C["bg_dark"])
        c.place(relx=0.5, rely=0.46, anchor="center")
        tk.Label(c, text="🚗", font=("Segoe UI Emoji", 48),
                 bg=C["bg_dark"]).pack()
        tk.Label(c, text="WeAreCars",
                 font=("Segoe UI", 34, "bold"),
                 fg=C["teal"], bg=C["bg_dark"]).pack(pady=(4, 2))
        tk.Label(c, text="Car Rental Management System",
                 font=("Segoe UI", 12), fg=C["text2"],
                 bg=C["bg_dark"]).pack()
        tk.Frame(c, height=1, bg=C["border"]).pack(fill="x", pady=16)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("S.Horizontal.TProgressbar",
                        troughcolor=C["bg_mid"],
                        background=C["teal"], thickness=8)
        self.pv = tk.IntVar(value=0)
        ttk.Progressbar(c, variable=self.pv, maximum=100,
                        style="S.Horizontal.TProgressbar",
                        length=380).pack()
        self.lbl = tk.Label(c, text="Starting...",
                            font=FSM, fg=C["text3"], bg=C["bg_dark"])
        self.lbl.pack(pady=6)
        tk.Frame(self, bg=C["teal"], height=5).pack(fill="x", side="bottom")
        self._step(0)
    def _step(self, n):
        if n <= 100:
            self.pv.set(n)
            msgs = {0: "Starting...", 25: "Loading data...",
                    55: "Building interface...", 85: "Almost ready...", 100: "Done!"}
            if n in msgs:
                self.lbl.config(text=msgs[n])
            self.after(22, self._step, n + 1)
        else:
            self.after(120, lambda: (self.destroy(), self.on_done()))


# ─────────────────────────────────────────────────────────────────────────────
#  SCROLLABLE CANVAS HELPER
# ─────────────────────────────────────────────────────────────────────────────

def scrollable(parent):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("V.TScrollbar",
                    troughcolor=C["bg_dark"],
                    background=C["border"],
                    arrowcolor=C["text2"])
    outer = tk.Frame(parent, bg=C["bg_dark"])
    outer.pack(fill="both", expand=True)
    cv  = tk.Canvas(outer, bg=C["bg_dark"], highlightthickness=0)
    vsb = ttk.Scrollbar(outer, orient="vertical",
                        command=cv.yview, style="Vertical.TScrollbar")
    inner = tk.Frame(cv, bg=C["bg_dark"])
    inner.bind("<Configure>",
               lambda e: cv.configure(scrollregion=cv.bbox("all")))
    cv.create_window((0, 0), window=inner, anchor="nw")
    cv.configure(yscrollcommand=vsb.set)
    cv.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    cv.bind_all("<MouseWheel>",
                lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))
    return inner

# ─────────────────────────────────────────────────────────────────────────────
#  TREEVIEW STYLE
# ─────────────────────────────────────────────────────────────────────────────

def tree_style():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("W.Treeview",
                background=C["bg_card"], foreground=C["text"],
                fieldbackground=C["bg_card"], rowheight=30,
                font=FB, borderwidth=0)
    s.configure("W.Treeview.Heading",
                background=C["bg_mid"], foreground=C["teal"],
                font=("Segoe UI", 10, "bold"), relief="flat")
    s.map("W.Treeview",
          background=[("selected", C["teal"])],
          foreground=[("selected", C["bg_dark"])])

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

class Sidebar(tk.Frame):
    def __init__(self, parent, ctrl, active="dashboard"):
        super().__init__(parent, bg=C["bg_mid"], width=210)
        self.pack_propagate(False)
        self.ctrl   = ctrl
        self.active = active
        self._build()

    def _build(self):
        tk.Frame(self, bg=C["teal"], width=3).pack(side="right", fill="y")
        inner = tk.Frame(self, bg=C["bg_mid"])
        inner.pack(fill="both", expand=True)

        brand = tk.Frame(inner, bg=C["bg_mid"], pady=16)
        brand.pack(fill="x")
        tk.Label(brand, text="🚗", font=("Segoe UI Emoji", 24),
                 bg=C["bg_mid"]).pack()
        tk.Label(brand, text="WeAreCars",
                 font=("Segoe UI", 13, "bold"),
                 fg=C["teal"], bg=C["bg_mid"]).pack()

        tk.Frame(inner, height=1, bg=C["border"]).pack(fill="x", padx=10, pady=4)

        nav = [
            ("🏠", "Dashboard",      "dashboard", self.ctrl.show_dashboard),
            ("➕", "Add Booking",    "add",       self.ctrl.show_add_booking),
            ("📋", "View Bookings",  "view",      self.ctrl.show_view_bookings),
            ("✏", "Update Booking", "update",    self.ctrl.show_update_booking),
            ("🗑", "Delete Booking", "delete",    self.ctrl.show_delete_booking),
            ("i", "About",          "about",     self.ctrl.show_about),
        ]

        for icon, label, key, cmd in nav:
            active = (key == self.active)
            bg = C["teal"]    if active else C["bg_mid"]
            fg = C["bg_dark"] if active else C["text"]
            f  = tk.Frame(inner, bg=bg)
            f.pack(fill="x", padx=8, pady=2)
            tk.Button(f, text=f"  {icon}  {label}",
                      command=cmd, anchor="w",
                      bg=bg, fg=fg, font=FB, relief="flat",
                      activebackground=C["bg_hover"],
                      activeforeground=C["text"],
                      cursor="hand2", pady=10, padx=8
                      ).pack(fill="x")

        tk.Frame(inner, bg=C["bg_mid"]).pack(fill="both", expand=True)
        tk.Frame(inner, height=1, bg=C["border"]).pack(fill="x", padx=10)
        tk.Label(inner, text="Logged in: sta001",
                 font=FSM, fg=C["text3"], bg=C["bg_mid"]).pack(pady=(6, 2))
        tk.Button(inner, text="  < Logout",
                  command=self.ctrl.show_login,
                  anchor="w", bg=C["bg_mid"], fg=C["danger"],
                  font=FB, relief="flat",
                  activebackground=C["bg_card"],
                  activeforeground=C["danger"],
                  cursor="hand2", pady=10, padx=14
                  ).pack(fill="x", padx=8, pady=(2, 12))

# ─────────────────────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────────────────────

class LoginFrame(tk.Frame):
    USER = "sta001"
    PASS = "givemethekeys123"

    def __init__(self, parent, on_success):
        super().__init__(parent, bg=C["bg_dark"])
        self.on_success = on_success
        self._build()

    def _build(self):
        # Left panel
        left = tk.Frame(self, bg=C["bg_mid"], width=370)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Frame(left, bg=C["teal"], width=4).pack(side="right", fill="y")

        cl = tk.Frame(left, bg=C["bg_mid"])
        cl.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(cl, text="🚗", font=("Segoe UI Emoji", 56),
                 bg=C["bg_mid"]).pack()
        tk.Label(cl, text="WeAreCars",
                 font=("Segoe UI", 28, "bold"),
                 fg=C["teal"], bg=C["bg_mid"]).pack(pady=(6, 2))
        tk.Label(cl, text="Car Rental Management System",
                 font=FB, fg=C["text2"], bg=C["bg_mid"]).pack()

        tk.Frame(cl, height=1, bg=C["border"]).pack(fill="x", pady=18)

        features = [
            ("🚘", "Manage car rental bookings"),
            ("£",  "Real-time pricing calculator"),
            ("📋", "Full booking history & search"),
            ("📊", "Live analytics dashboard"),
            ("🔄", "Update & cancel bookings"),
        ]
        for icon, text in features:
            r = tk.Frame(cl, bg=C["bg_mid"])
            r.pack(fill="x", pady=3)
            tk.Label(r, text=icon, font=("Segoe UI Emoji", 12),
                     bg=C["bg_mid"]).pack(side="left", padx=(0, 8))
            tk.Label(r, text=text, font=FB,
                     fg=C["text"], bg=C["bg_mid"]).pack(side="left")



        # Right form
        right = tk.Frame(self, bg=C["bg_dark"])
        right.pack(side="right", fill="both", expand=True)

        card = tk.Frame(right, bg=C["bg_mid"], padx=48, pady=44)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Staff Login Portal",
                 font=("Segoe UI", 20, "bold"),
                 fg=C["text"], bg=C["bg_mid"]).pack(pady=(0, 4))
        tk.Label(card, text="Enter your credentials to continue",
                 font=FB, fg=C["text2"], bg=C["bg_mid"]).pack(pady=(0, 26))

        tk.Label(card, text="USERNAME",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["teal"], bg=C["bg_mid"],
                 anchor="w").pack(fill="x")
        self.uvar = tk.StringVar()
        ue = entry(card, var=self.uvar, width=32)
        ue.pack(pady=(4, 14), ipady=6)
        ue.bind("<Return>", lambda e: self.pe.focus())
        ue.focus()

        tk.Label(card, text="PASSWORD",
                 font=("Segoe UI", 8, "bold"),
                 fg=C["teal"], bg=C["bg_mid"],
                 anchor="w").pack(fill="x")

        pr = tk.Frame(card, bg=C["bg_mid"])
        pr.pack(pady=(4, 6))
        self.pvar  = tk.StringVar()
        self._show = False
        self.pe    = entry(pr, var=self.pvar, width=27, show="*")
        self.pe.pack(side="left", ipady=6)
        self.pe.bind("<Return>", lambda e: self._login())

        tk.Button(pr, text="show", font=FSM,
                  bg=C["bg_input"], fg=C["text2"], relief="flat",
                  cursor="hand2", activebackground=C["bg_card"],
                  command=self._toggle, pady=6, padx=6
                  ).pack(side="left", padx=(6, 0))

        self.errlbl = tk.Label(card, text="", font=FSM,
                               fg=C["danger"], bg=C["bg_mid"])
        self.errlbl.pack(pady=(4, 12))

        btn(card, "  Login", self._login,
            bg=C["teal"], fg=C["bg_dark"], width=30, pady=10).pack()

        tk.Label(card, text="Hint:  sta001  /  givemethekeys123",
                 font=FSM, fg=C["text3"], bg=C["bg_mid"]).pack(pady=(12, 0))

    def _toggle(self):
        self._show = not self._show
        self.pe.config(show="" if self._show else "*")

    def _login(self):
        u = self.uvar.get().strip()
        p = self.pvar.get().strip()
        if not u or not p:
            self.errlbl.config(text="Please enter both fields.")
            return
        if u == self.USER and p == self.PASS:
            self.errlbl.config(text="")
            self.on_success()
        else:
            self.errlbl.config(text="Incorrect username or password.")
            self.pvar.set("")
            self.pe.focus()


# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

class DashboardFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=C["bg_dark"])
        self.ctrl = ctrl
        self._build()

    def _build(self):
        Sidebar(self, self.ctrl, "dashboard").pack(side="left", fill="y")
        self.main = tk.Frame(self, bg=C["bg_dark"])
        self.main.pack(side="right", fill="both", expand=True)

        # Top bar
        top = tk.Frame(self.main, bg=C["bg_mid"], padx=22, pady=13)
        top.pack(fill="x")
        tk.Label(top, text="Dashboard",
                 font=FT, fg=C["teal"], bg=C["bg_mid"]).pack(side="left")
        self.clock_lbl = tk.Label(top, text="",
                                  font=("Segoe UI", 11),
                                  fg=C["text2"], bg=C["bg_mid"])
        self.clock_lbl.pack(side="right")
        self._tick()

        # Two-column content
        content = tk.Frame(self.main, bg=C["bg_dark"])
        content.pack(fill="both", expand=True)

        # Left scrollable
        left_wrap = tk.Frame(content, bg=C["bg_dark"])
        left_wrap.pack(side="left", fill="both", expand=True)
        self.left = scrollable(left_wrap)

        # Right fixed panel
        tk.Frame(content, bg=C["border"], width=1).pack(side="right", fill="y")
        self.right = tk.Frame(content, bg=C["bg_mid"], width=268)
        self.right.pack(side="right", fill="y")
        self.right.pack_propagate(False)

    def _tick(self):
        now = datetime.now().strftime("%a %d %b %Y   %H:%M:%S")
        if self.clock_lbl.winfo_exists():
            self.clock_lbl.config(text=now)
            self.after(1000, self._tick)

    def refresh(self):
        for w in self.left.winfo_children():  w.destroy()
        for w in self.right.winfo_children(): w.destroy()
        self._left()
        self._right()

    # ── LEFT ─────────────────────────────────────────────────────────────────

    def _left(self):
        pad = dict(padx=20, pady=8)
        total   = len(bookings)
        revenue = sum(b.get("total_price", 0) for b in bookings)
        active  = sum(1 for b in bookings if b.get("status") == "Active")
        done    = sum(1 for b in bookings if b.get("status") == "Completed")

        # KPI cards
        kr = tk.Frame(self.left, bg=C["bg_dark"])
        kr.pack(fill="x", **pad)
        for label, val, color in [
            ("Total Bookings", str(total),          C["blue"]),
            ("Total Revenue",  f"£{revenue:,.2f}",  C["success"]),
            ("Active Rentals", str(active),         C["teal"]),
            ("Completed",      str(done),           C["text2"]),
        ]:
            card = tk.Frame(kr, bg=C["bg_card"], padx=16, pady=14)
            card.pack(side="left", expand=True, fill="both", padx=5)
            tk.Frame(card, bg=color, height=3).pack(fill="x", pady=(0, 8))
            tk.Label(card, text=label, font=FSM,
                     fg=C["text2"], bg=C["bg_card"]).pack(anchor="w")
            tk.Label(card, text=val, font=("Segoe UI", 20, "bold"),
                     fg=color, bg=C["bg_card"]).pack(anchor="w", pady=(2, 0))

        # Chart
        tk.Label(self.left, text="Bookings by Car Type",
                 font=FH, fg=C["text"], bg=C["bg_dark"]
                 ).pack(anchor="w", **pad)
        cf = tk.Frame(self.left, bg=C["bg_card"], padx=14, pady=14)
        cf.pack(fill="x", padx=20, pady=(0, 8))
        self._chart(cf)

        # Quick actions
        tk.Label(self.left, text="Quick Actions",
                 font=FH, fg=C["text"], bg=C["bg_dark"]
                 ).pack(anchor="w", **pad)
        ar = tk.Frame(self.left, bg=C["bg_dark"])
        ar.pack(fill="x", padx=20, pady=(0, 8))
        for text, cmd, color, fgc in [
            ("+ Add Booking",   self.ctrl.show_add_booking,   C["success"], C["bg_dark"]),
            ("= View Bookings", self.ctrl.show_view_bookings, C["blue"],    C["white"]),
            ("/ Update",        self.ctrl.show_update_booking,C["gold"],    C["bg_dark"]),
            ("x Delete",        self.ctrl.show_delete_booking,C["danger"],  C["white"]),
        ]:
            btn(ar, text, cmd, bg=color, fg=fgc, width=14, pady=9
                ).pack(side="left", padx=5, pady=4)

        # Recent bookings
        tk.Label(self.left, text="Recent Bookings  (double-click for detail)",
                 font=FH, fg=C["text"], bg=C["bg_dark"]
                 ).pack(anchor="w", **pad)

        tree_style()
        cols = ("ID", "Name", "Car Type", "Days", "Total", "Status", "Date")
        tree = ttk.Treeview(self.left, columns=cols,
                            show="headings", height=6, style="W.Treeview")
        for col, w in zip(cols, [85, 160, 120, 55, 85, 90, 148]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        for b in reversed(bookings[-8:]):
            name = f"{b.get('first_name','')} {b.get('surname','')}"
            tree.insert("", "end", values=(
                b.get("id",""), name, b.get("car_type",""),
                b.get("days",""), f"£{b.get('total_price',0):.2f}",
                b.get("status","Active"), b.get("created_at",""),
            ))
        tree.pack(fill="x", padx=20, pady=(0, 22))

        def _detail(e):
            sel = tree.focus()
            if not sel: return
            vals = tree.item(sel, "values")
            if not vals: return
            b = next((x for x in bookings if x.get("id") == vals[0]), None)
            if not b: return
            msg = (
                f"  Booking ID  : {b['id']}\n"
                f"  Name        : {b['first_name']} {b['surname']}\n"
                f"  Address     : {b['address']}\n"
                f"  Age         : {b['age']}\n"
                f"  Licence     : {b['licence']}\n"
                f"  {'─'*36}\n"
                f"  Car Type    : {b['car_type']}\n"
                f"  Fuel Type   : {b['fuel_type']}\n"
                f"  Days        : {b['days']}\n"
                f"  Mileage     : {'Yes' if b.get('mileage') else 'No'}\n"
                f"  Breakdown   : {'Yes' if b.get('breakdown') else 'No'}\n"
                f"  {'─'*36}\n"
                f"  Total Price : £{b['total_price']:.2f}\n"
                f"  Status      : {b['status']}\n"
                f"  Created     : {b['created_at']}"
            )
            info(self, f"Booking — {vals[0]}", msg, icon="📋")

        tree.bind("<Double-1>", _detail)

    def _chart(self, parent):
        counts = {ct: 0 for ct in CAR_PRICES}
        for b in bookings:
            ct = b.get("car_type","")
            if ct in counts: counts[ct] += 1
        mx     = max(counts.values(), default=1) or 1
        colors = [C["teal"], C["blue"], C["gold"], C["success"]]
        W, H   = 620, 150
        cv = tk.Canvas(parent, width=W, height=H,
                       bg=C["bg_card"], highlightthickness=0)
        cv.pack()
        bw, gap, sx = 105, 40, 44
        for i, ct in enumerate(CAR_PRICES):
            cnt = counts[ct]
            x0  = sx + i*(bw+gap)
            x1  = x0 + bw
            bh  = int((cnt/mx)*100) if mx else 0
            y0  = H - 34 - bh
            y1  = H - 34
            cv.create_rectangle(x0, y0, x1, y1, fill=colors[i], outline="")
            cv.create_text((x0+x1)//2, max(y0-12,4),
                           text=str(cnt), fill=C["text"], font=FB)
            cv.create_text((x0+x1)//2, H-14,
                           text=ct, fill=C["text2"], font=FSM)

    # ── RIGHT PANEL ──────────────────────────────────────────────────────────

    def _right(self):
        rp  = self.right
        pad = dict(padx=14, pady=6)

        def sec(title):
            tk.Label(rp, text=title, font=FSH,
                     fg=C["teal"], bg=C["bg_mid"]).pack(anchor="w", **pad)

        def card_frame():
            f = tk.Frame(rp, bg=C["bg_card"], padx=12, pady=10)
            f.pack(fill="x", padx=12, pady=(0, 4))
            return f

        def row2(parent, k, v, vcolor=None):
            r = tk.Frame(parent, bg=C["bg_card"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=k + ":", font=FSM,
                     fg=C["text2"], bg=C["bg_card"],
                     width=10, anchor="w").pack(side="left")
            tk.Label(r, text=v, font=("Segoe UI", 9, "bold"),
                     fg=vcolor or C["text"],
                     bg=C["bg_card"]).pack(side="left")

        # Staff card
        sec("Staff Info")
        sc = card_frame()
        for k, v in [("Name","Staff Member"),("ID","sta001"),
                     ("Role","Rental Agent"),("Branch","London HQ"),
                     ("Session", datetime.now().strftime("%H:%M"))]:
            row2(sc, k, v)

        tk.Frame(rp, height=1, bg=C["border"]).pack(fill="x", padx=12, pady=4)

        # Pricing guide
        sec("Pricing Guide")
        pc = card_frame()
        tk.Label(pc, text=f"Base rate: £{BASE_RATE}/day",
                 font=("Segoe UI", 9, "bold"), fg=C["gold"],
                 bg=C["bg_card"]).pack(anchor="w", pady=(0, 6))
        tk.Label(pc, text="Car Type Surcharges:",
                 font=FSM, fg=C["text2"],
                 bg=C["bg_card"]).pack(anchor="w")
        for ct, p in CAR_PRICES.items():
            r = tk.Frame(pc, bg=C["bg_card"])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=f"  {ct}", font=FSM, fg=C["text"],
                     bg=C["bg_card"], width=14, anchor="w").pack(side="left")
            tk.Label(r, text=f"+£{p}", font=FSM, fg=C["teal"],
                     bg=C["bg_card"]).pack(side="right")
        tk.Frame(pc, height=1, bg=C["border"]).pack(fill="x", pady=5)
        tk.Label(pc, text="Fuel Surcharges:",
                 font=FSM, fg=C["text2"],
                 bg=C["bg_card"]).pack(anchor="w")
        for ft, p in FUEL_PRICES.items():
            r = tk.Frame(pc, bg=C["bg_card"])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=f"  {ft}", font=FSM, fg=C["text"],
                     bg=C["bg_card"], width=14, anchor="w").pack(side="left")
            tk.Label(r, text=f"+£{p}", font=FSM, fg=C["teal"],
                     bg=C["bg_card"]).pack(side="right")
        tk.Frame(pc, height=1, bg=C["border"]).pack(fill="x", pady=5)
        for label, val in [("Unltd Mileage", f"+£{MILEAGE_RATE}/day"),
                            ("Breakdown",     f"+£{BREAKDOWN_RATE}/day")]:
            r = tk.Frame(pc, bg=C["bg_card"])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=f"  {label}", font=FSM, fg=C["text"],
                     bg=C["bg_card"], width=14, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=FSM, fg=C["gold"],
                     bg=C["bg_card"]).pack(side="right")

        tk.Frame(rp, height=1, bg=C["border"]).pack(fill="x", padx=12, pady=4)

        # Shortcuts
        sec("Shortcuts")
        sc2 = card_frame()
        for key, desc in [("F11","Toggle fullscreen"),
                           ("Esc","Exit fullscreen"),
                           ("Enter","Confirm / submit")]:
            r = tk.Frame(sc2, bg=C["bg_card"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=key, font=("Courier New", 9, "bold"),
                     fg=C["bg_dark"], bg=C["teal"],
                     padx=3, pady=1).pack(side="left")
            tk.Label(r, text="  " + desc, font=FSM,
                     fg=C["text2"], bg=C["bg_card"]).pack(side="left")

        # Date
        tk.Frame(rp, height=1, bg=C["border"]).pack(fill="x", padx=12, pady=4)
        tk.Label(rp, text=datetime.now().strftime("%A\n%d %B %Y"),
                 font=("Segoe UI", 10), fg=C["text2"],
                 bg=C["bg_mid"], justify="center").pack(pady=8)


# ─────────────────────────────────────────────────────────────────────────────
#  ADD BOOKING
# ─────────────────────────────────────────────────────────────────────────────

class AddBookingFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=C["bg_dark"])
        self.ctrl = ctrl
        self._build()

    def _build(self):
        Sidebar(self, self.ctrl, "add").pack(side="left", fill="y")
        main = tk.Frame(self, bg=C["bg_dark"])
        main.pack(side="right", fill="both", expand=True)

        top = tk.Frame(main, bg=C["bg_mid"], padx=22, pady=13)
        top.pack(fill="x")
        tk.Label(top, text="Add New Booking",
                 font=FT, fg=C["teal"], bg=C["bg_mid"]).pack(side="left")

        inner = scrollable(main)
        self._form(inner)

    def _sec(self, parent, text):
        tk.Label(parent, text=text, font=FH,
                 fg=C["blue"], bg=C["bg_dark"]
                 ).pack(anchor="w", pady=(10, 4))

    def _form(self, parent):
        cols = tk.Frame(parent, bg=C["bg_dark"])
        cols.pack(fill="x", padx=20, pady=10)
        lc = tk.Frame(cols, bg=C["bg_dark"])
        lc.pack(side="left", fill="both", expand=True, padx=(0, 10))
        rc = tk.Frame(cols, bg=C["bg_dark"])
        rc.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Customer details
        self._sec(lc, "Customer Details")
        cust = tk.Frame(lc, bg=C["bg_card"], padx=18, pady=16)
        cust.pack(fill="x", pady=(0, 10))

        self.vfn  = tk.StringVar()
        self.vsn  = tk.StringVar()
        self.vadr = tk.StringVar()
        self.vage = tk.StringVar()
        self.vlic = tk.StringVar(value="Yes")

        # Non-numeric fields
        for lbl, var, w in [
            ("First Name *",  self.vfn,  26),
            ("Surname *",     self.vsn,  26),
            ("Address *",     self.vadr, 34),
        ]:
            r = tk.Frame(cust, bg=C["bg_card"])
            r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, font=FB, fg=C["text"],
                     bg=C["bg_card"], width=18, anchor="w").pack(side="left")
            entry(r, var=var, width=w).pack(side="left", padx=8, ipady=4)

        # Age — numeric only
        r = tk.Frame(cust, bg=C["bg_card"])
        r.pack(fill="x", pady=4)
        tk.Label(r, text="Age *", font=FB, fg=C["text"],
                 bg=C["bg_card"], width=18, anchor="w").pack(side="left")
        entry(r, var=self.vage, width=12, numeric=True).pack(side="left", padx=8, ipady=4)

        lr = tk.Frame(cust, bg=C["bg_card"])
        lr.pack(fill="x", pady=4)
        tk.Label(lr, text="Driving Licence *", font=FB, fg=C["text"],
                 bg=C["bg_card"], width=18, anchor="w").pack(side="left")
        for val in ("Yes", "No"):
            tk.Radiobutton(lr, text=val, variable=self.vlic, value=val,
                           bg=C["bg_card"], fg=C["text"],
                           selectcolor=C["bg_input"],
                           activebackground=C["bg_card"],
                           font=FB).pack(side="left", padx=8)

        # Rental options
        self._sec(rc, "Rental Options")
        rent = tk.Frame(rc, bg=C["bg_card"], padx=18, pady=16)
        rent.pack(fill="x", pady=(0, 10))

        # Days — Spinbox already numeric by nature, no extra change needed
        dr = tk.Frame(rent, bg=C["bg_card"])
        dr.pack(fill="x", pady=4)
        tk.Label(dr, text="Days * (1-28)", font=FB, fg=C["text"],
                 bg=C["bg_card"], width=18, anchor="w").pack(side="left")
        self.vdays = tk.IntVar(value=1)

        # Validate Spinbox input to digits only
        vcmd_days = (self.winfo_toplevel().register(_digits_only), "%P")
        tk.Spinbox(dr, from_=1, to=28, textvariable=self.vdays,
                   width=8, bg=C["bg_input"], fg=C["text"],
                   relief="flat", font=FB,
                   validate="key", validatecommand=vcmd_days,
                   command=self._preview).pack(side="left", padx=8)

        self.vcar  = tk.StringVar(value="City Car")
        self.vfuel = tk.StringVar(value="Petrol")

        for lbl, var, opts in [
            ("Car Type *",  self.vcar,  list(CAR_PRICES.keys())),
            ("Fuel Type *", self.vfuel, list(FUEL_PRICES.keys())),
        ]:
            r = tk.Frame(rent, bg=C["bg_card"])
            r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, font=FB, fg=C["text"],
                     bg=C["bg_card"], width=18, anchor="w").pack(side="left")
            m = tk.OptionMenu(r, var, *opts, command=lambda _: self._preview())
            m.config(bg=C["bg_input"], fg=C["text"], relief="flat",
                     font=FB, highlightthickness=0, width=18)
            m["menu"].config(bg=C["bg_card"], fg=C["text"], font=FB)
            m.pack(side="left", padx=8)

        # Extras
        self._sec(rc, "Optional Extras")
        ext = tk.Frame(rc, bg=C["bg_card"], padx=18, pady=16)
        ext.pack(fill="x", pady=(0, 10))
        self.vmil = tk.BooleanVar(value=False)
        self.vbrk = tk.BooleanVar(value=False)
        for lbl, var in [
            ("Unlimited Mileage  (+£10/day)", self.vmil),
            ("Breakdown Cover  (+£2/day)",    self.vbrk),
        ]:
            tk.Checkbutton(ext, text=lbl, variable=var,
                           bg=C["bg_card"], fg=C["text"],
                           selectcolor=C["bg_input"],
                           activebackground=C["bg_card"],
                           font=FB).pack(anchor="w", pady=3)

        for v in (self.vmil, self.vbrk, self.vdays):
            v.trace_add("write", lambda *_: self._preview())
        self.vcar.trace_add("write",  lambda *_: self._preview())
        self.vfuel.trace_add("write", lambda *_: self._preview())

        # Price bar
        pf = tk.Frame(parent, bg=C["teal"], padx=22, pady=14)
        pf.pack(fill="x", padx=20, pady=(4, 10))
        tk.Label(pf, text="Estimated Total",
                 font=FH, fg=C["bg_dark"], bg=C["teal"]).pack(side="left")
        self.prev_lbl = tk.Label(pf, text="£25.00",
                                 font=("Segoe UI", 24, "bold"),
                                 fg=C["bg_dark"], bg=C["teal"])
        self.prev_lbl.pack(side="right")
        self._preview()

        # Buttons
        br = tk.Frame(parent, bg=C["bg_dark"])
        br.pack(padx=20, pady=10)
        btn(br, "Preview & Confirm", self._confirm,
            bg=C["teal"], fg=C["bg_dark"], width=22).pack(side="left", padx=8)
        btn(br, "Clear Form", self._clear,
            bg=C["bg_card"], fg=C["text2"], width=14).pack(side="left", padx=8)

    def _calc(self):
        try:    d = max(1, min(28, int(self.vdays.get())))
        except: d = 1
        base  = d * BASE_RATE
        car   = CAR_PRICES.get(self.vcar.get(), 0)
        fuel  = FUEL_PRICES.get(self.vfuel.get(), 0)
        mil   = d * MILEAGE_RATE   if self.vmil.get() else 0
        brk   = d * BREAKDOWN_RATE if self.vbrk.get() else 0
        total = base + car + fuel + mil + brk
        bd = {
            "Base rate":        f"£{BASE_RATE}/day x {d} = £{base}",
            "Car type":         f"+£{car} ({self.vcar.get()})",
            "Fuel type":        f"+£{fuel} ({self.vfuel.get()})",
            "Unlimited mileage":f"+£{mil}" if mil else "Not selected",
            "Breakdown cover":  f"+£{brk}" if brk else "Not selected",
        }
        return d, bd, total

    def _preview(self, *_):
        _, _, total = self._calc()
        if hasattr(self, "prev_lbl") and self.prev_lbl.winfo_exists():
            self.prev_lbl.config(text=f"£{total:.2f}")

    def _validate(self):
        fn  = self.vfn.get().strip()
        sn  = self.vsn.get().strip()
        adr = self.vadr.get().strip()
        age = self.vage.get().strip()
        if not fn:  return False, "First Name is required."
        if not re.match(r"^[A-Za-z\-']{1,50}$", fn):
            return False, "First name: letters only."
        if not sn:  return False, "Surname is required."
        if not re.match(r"^[A-Za-z\-']{1,50}$", sn):
            return False, "Surname: letters only."
        if not adr or len(adr) < 5:
            return False, "Please enter a valid address (min 5 chars)."
        if not age: return False, "Age is required."
        try:
            a = int(age)
            if not (18 <= a <= 100):
                return False, "Customer must be aged 18-100."
        except ValueError:
            return False, "Age must be a whole number."
        if self.vlic.get() == "No":
            return False, "Cannot book without a valid driving licence."
        try:
            d = int(self.vdays.get())
            if not (1 <= d <= 28):
                return False, "Days must be between 1 and 28."
        except:
            return False, "Days must be a valid number."
        return True, None

    def _confirm(self):
        ok, e = self._validate()
        if not ok:
            err(self, "Validation Error", f"\n  {e}\n")
            return
        d, bd, total = self._calc()
        lines = [
            f"  Customer    : {self.vfn.get().strip()} {self.vsn.get().strip()}",
            f"  Address     : {self.vadr.get().strip()}",
            f"  Age         : {self.vage.get().strip()}",
            f"  Licence     : {self.vlic.get()}",
            f"  {'─'*38}",
            f"  Car Type    : {self.vcar.get()}",
            f"  Fuel        : {self.vfuel.get()}",
            f"  Days        : {d}",
            f"  {'─'*38}",
            "  PRICE BREAKDOWN:",
        ]
        for k, v in bd.items():
            lines.append(f"    {k:<22}: {v}")
        lines += [f"  {'─'*38}", f"  TOTAL PRICE : £{total:.2f}"]
        if ask(self, "Confirm Booking", "\n".join(lines), icon="?", icolor=C["teal"]):
            self._save(d, total)

    def _save(self, days, total):
        nid = f"WC{len(bookings)+1:04d}"
        rec = {
            "id": nid,
            "first_name":  self.vfn.get().strip(),
            "surname":     self.vsn.get().strip(),
            "address":     self.vadr.get().strip(),
            "age":         int(self.vage.get().strip()),
            "licence":     self.vlic.get(),
            "days":        days,
            "car_type":    self.vcar.get(),
            "fuel_type":   self.vfuel.get(),
            "mileage":     self.vmil.get(),
            "breakdown":   self.vbrk.get(),
            "total_price": total,
            "status":      "Active",
            "created_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        bookings.append(rec)
        save_bookings(bookings)
        info(self, "Booking Saved",
             f"\n  Booking {nid} saved!\n\n"
             f"  Customer : {rec['first_name']} {rec['surname']}\n"
             f"  Total    : £{total:.2f}\n")
        self._clear()
        self.ctrl.show_dashboard()

    def _clear(self):
        self.vfn.set(""); self.vsn.set("")
        self.vadr.set(""); self.vage.set("")
        self.vlic.set("Yes"); self.vdays.set(1)
        self.vcar.set("City Car"); self.vfuel.set("Petrol")
        self.vmil.set(False); self.vbrk.set(False)
        self._preview()


# ─────────────────────────────────────────────────────────────────────────────
#  VIEW BOOKINGS
# ─────────────────────────────────────────────────────────────────────────────

class ViewBookingsFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=C["bg_dark"])
        self.ctrl = ctrl
        self._sort_col = None
        self._sort_asc = True
        self._build()

    def _build(self):
        Sidebar(self, self.ctrl, "view").pack(side="left", fill="y")
        main = tk.Frame(self, bg=C["bg_dark"])
        main.pack(side="right", fill="both", expand=True)

        top = tk.Frame(main, bg=C["bg_mid"], padx=22, pady=13)
        top.pack(fill="x")
        tk.Label(top, text="All Bookings",
                 font=FT, fg=C["teal"], bg=C["bg_mid"]).pack(side="left")

        fb = tk.Frame(main, bg=C["bg_dark"], padx=20, pady=10)
        fb.pack(fill="x")
        tk.Label(fb, text="Search:", font=FB,
                 fg=C["text2"], bg=C["bg_dark"]).pack(side="left")
        self.sv = tk.StringVar()
        self.sv.trace_add("write", lambda *_: self.refresh())
        entry(fb, var=self.sv, width=30).pack(side="left", padx=10, ipady=4)

        tk.Label(fb, text="Status:", font=FB,
                 fg=C["text2"], bg=C["bg_dark"]).pack(side="left", padx=(16,4))
        self.fstat = tk.StringVar(value="All")
        m = tk.OptionMenu(fb, self.fstat, "All","Active","Completed","Cancelled",
                          command=lambda _: self.refresh())
        m.config(bg=C["bg_input"], fg=C["text"], relief="flat",
                 font=FB, width=10, highlightthickness=0)
        m["menu"].config(bg=C["bg_card"], fg=C["text"], font=FB)
        m.pack(side="left")

        tree_style()
        cols = ("ID","Name","Car Type","Fuel","Days","Total","Status","Date")
        self.tree = ttk.Treeview(main, columns=cols,
                                 show="headings", style="W.Treeview")
        for col, w in zip(cols, [85,160,120,110,55,85,90,148]):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=4)
        self.tree.bind("<Double-1>", self._detail)

        self.cnt = tk.Label(main, text="", font=FSM,
                            fg=C["text3"], bg=C["bg_dark"])
        self.cnt.pack(anchor="e", padx=20, pady=4)
        self.refresh()

    def refresh(self):
        q  = self.sv.get().lower()
        fs = self.fstat.get()
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for b in reversed(bookings):
            name = f"{b.get('first_name','')} {b.get('surname','')}".lower()
            if q and q not in name and q not in b.get("id","").lower():
                continue
            if fs != "All" and b.get("status","Active") != fs:
                continue
            fn = f"{b.get('first_name','')} {b.get('surname','')}"
            self.tree.insert("", "end", iid=b["id"], values=(
                b.get("id",""), fn, b.get("car_type",""),
                b.get("fuel_type",""), b.get("days",""),
                f"£{b.get('total_price',0):.2f}",
                b.get("status","Active"), b.get("created_at",""),
            ))
            shown += 1
        self.cnt.config(text=f"Showing {shown} of {len(bookings)} bookings")

    def _sort(self, col):
        self._sort_asc = not self._sort_asc if self._sort_col == col else True
        self._sort_col = col
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort(reverse=not self._sort_asc)
        for i, (_, k) in enumerate(items):
            self.tree.move(k, "", i)

    def _detail(self, e):
        sel = self.tree.focus()
        if not sel: return
        b = next((x for x in bookings if x.get("id") == sel), None)
        if not b: return
        msg = (
            f"  Booking ID  : {b['id']}\n"
            f"  Name        : {b['first_name']} {b['surname']}\n"
            f"  Address     : {b['address']}\n"
            f"  Age         : {b['age']}\n"
            f"  Licence     : {b['licence']}\n"
            f"  {'─'*36}\n"
            f"  Car Type    : {b['car_type']}\n"
            f"  Fuel Type   : {b['fuel_type']}\n"
            f"  Days        : {b['days']}\n"
            f"  Mileage     : {'Yes' if b.get('mileage') else 'No'}\n"
            f"  Breakdown   : {'Yes' if b.get('breakdown') else 'No'}\n"
            f"  {'─'*36}\n"
            f"  Total Price : £{b['total_price']:.2f}\n"
            f"  Status      : {b['status']}\n"
            f"  Created     : {b['created_at']}"
        )
        info(self, f"Booking — {sel}", msg, icon="📋")


# ─────────────────────────────────────────────────────────────────────────────
#  UPDATE BOOKING
# ─────────────────────────────────────────────────────────────────────────────

class UpdateBookingFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=C["bg_dark"])
        self.ctrl    = ctrl
        self.current = None
        self._build()

    def _build(self):
        Sidebar(self, self.ctrl, "update").pack(side="left", fill="y")
        main = tk.Frame(self, bg=C["bg_dark"])
        main.pack(side="right", fill="both", expand=True)

        top = tk.Frame(main, bg=C["bg_mid"], padx=22, pady=13)
        top.pack(fill="x")
        tk.Label(top, text="Update Booking",
                 font=FT, fg=C["teal"], bg=C["bg_mid"]).pack(side="left")

        panel = tk.Frame(main, bg=C["bg_card"], padx=26, pady=20)
        panel.pack(fill="x", padx=20, pady=18)
        tk.Label(panel, text="Enter Booking ID:", font=FSH,
                 fg=C["text"], bg=C["bg_card"]).pack(anchor="w")
        row = tk.Frame(panel, bg=C["bg_card"])
        row.pack(fill="x", pady=8)
        self.sid = tk.StringVar()
        entry(row, var=self.sid, width=18).pack(side="left", ipady=5)
        btn(row, "Find", self._find, width=10).pack(side="left", padx=10)
        self.ferr = tk.Label(panel, text="", font=FSM,
                             fg=C["danger"], bg=C["bg_card"])
        self.ferr.pack(anchor="w")

        self.edit = tk.Frame(main, bg=C["bg_card"], padx=26, pady=20)
        self.ud   = tk.IntVar(value=1)
        self.uc   = tk.StringVar(value="City Car")
        self.uf   = tk.StringVar(value="Petrol")
        self.um   = tk.BooleanVar(value=False)
        self.ub   = tk.BooleanVar(value=False)
        self.us   = tk.StringVar(value="Active")

        tk.Label(self.edit, text="Edit Details:", font=FSH,
                 fg=C["teal"], bg=C["bg_card"]).pack(anchor="w", pady=(0,10))

        r1 = tk.Frame(self.edit, bg=C["bg_card"])
        r1.pack(fill="x", pady=4)
        tk.Label(r1, text="Days (1-28)", font=FB, fg=C["text"],
                 bg=C["bg_card"], width=24, anchor="w").pack(side="left")

        # Days Spinbox — numeric only
        vcmd_ud = (self.winfo_toplevel().register(_digits_only), "%P")
        tk.Spinbox(r1, from_=1, to=28, textvariable=self.ud,
                   width=8, bg=C["bg_input"], fg=C["text"],
                   relief="flat", font=FB,
                   validate="key", validatecommand=vcmd_ud
                   ).pack(side="left", padx=8)

        for lbl, var, opts in [
            ("Car Type",  self.uc, list(CAR_PRICES.keys())),
            ("Fuel Type", self.uf, list(FUEL_PRICES.keys())),
            ("Status",    self.us, ["Active","Completed","Cancelled"]),
        ]:
            r = tk.Frame(self.edit, bg=C["bg_card"])
            r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, font=FB, fg=C["text"],
                     bg=C["bg_card"], width=24, anchor="w").pack(side="left")
            m = tk.OptionMenu(r, var, *opts)
            m.config(bg=C["bg_input"], fg=C["text"], relief="flat",
                     font=FB, width=18, highlightthickness=0)
            m["menu"].config(bg=C["bg_dark"], fg=C["text"], font=FB)
            m.pack(side="left", padx=8)

        er = tk.Frame(self.edit, bg=C["bg_card"])
        er.pack(fill="x", pady=4)
        for lbl, var in [("Unlimited Mileage (+10/day)", self.um),
                          ("Breakdown Cover (+2/day)",    self.ub)]:
            tk.Checkbutton(er, text=lbl, variable=var,
                           bg=C["bg_card"], fg=C["text"],
                           selectcolor=C["bg_input"],
                           activebackground=C["bg_card"],
                           font=FB).pack(side="left", padx=(0,20))

        btn(self.edit, "Save Changes", self._save,
            bg=C["success"], fg=C["bg_dark"], width=20).pack(pady=16)

    def _find(self):
        bid = self.sid.get().strip().upper()
        b   = next((x for x in bookings if x["id"] == bid), None)
        if not b:
            self.ferr.config(text=f"Booking '{bid}' not found.")
            self.edit.pack_forget()
            self.current = None
            return
        self.ferr.config(text="")
        self.current = b
        self.ud.set(b["days"]); self.uc.set(b["car_type"])
        self.uf.set(b["fuel_type"]); self.um.set(b.get("mileage",False))
        self.ub.set(b.get("breakdown",False)); self.us.set(b.get("status","Active"))
        self.edit.pack(fill="x", padx=20, pady=4)

    def _save(self):
        if not self.current: return
        d = int(self.ud.get())
        if not (1 <= d <= 28):
            err(self, "Validation", "\n  Days must be between 1 and 28.\n")
            return
        base  = d * BASE_RATE
        car   = CAR_PRICES.get(self.uc.get(), 0)
        fuel  = FUEL_PRICES.get(self.uf.get(), 0)
        mil   = d * MILEAGE_RATE   if self.um.get() else 0
        brk   = d * BREAKDOWN_RATE if self.ub.get() else 0
        total = base + car + fuel + mil + brk
        self.current.update({
            "days": d, "car_type": self.uc.get(),
            "fuel_type": self.uf.get(), "mileage": self.um.get(),
            "breakdown": self.ub.get(), "status": self.us.get(),
            "total_price": total,
        })
        save_bookings(bookings)
        info(self, "Updated",
             f"\n  Booking {self.current['id']} updated.\n\n"
             f"  New status : {self.us.get()}\n"
             f"  New total  : £{total:.2f}\n")
        self.edit.pack_forget()
        self.sid.set(""); self.current = None
        self.ctrl.show_dashboard()

    def refresh(self):
        self.sid.set(""); self.ferr.config(text="")
        self.current = None; self.edit.pack_forget()


# ─────────────────────────────────────────────────────────────────────────────
#  DELETE BOOKING
# ─────────────────────────────────────────────────────────────────────────────

class DeleteBookingFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=C["bg_dark"])
        self.ctrl  = ctrl
        self.found = None
        self._build()

    def _build(self):
        Sidebar(self, self.ctrl, "delete").pack(side="left", fill="y")
        main = tk.Frame(self, bg=C["bg_dark"])
        main.pack(side="right", fill="both", expand=True)

        top = tk.Frame(main, bg=C["bg_mid"], padx=22, pady=13)
        top.pack(fill="x")
        tk.Label(top, text="Delete Booking",
                 font=FT, fg=C["danger"], bg=C["bg_mid"]).pack(side="left")

        panel = tk.Frame(main, bg=C["bg_card"], padx=26, pady=20)
        panel.pack(fill="x", padx=20, pady=18)
        tk.Label(panel, text="Enter Booking ID to delete:", font=FSH,
                 fg=C["text"], bg=C["bg_card"]).pack(anchor="w")
        row = tk.Frame(panel, bg=C["bg_card"])
        row.pack(fill="x", pady=8)
        self.did = tk.StringVar()
        entry(row, var=self.did, width=18).pack(side="left", ipady=5)
        btn(row, "Find", self._find, width=10).pack(side="left", padx=10)
        self.ferr = tk.Label(panel, text="", font=FSM,
                             fg=C["danger"], bg=C["bg_card"])
        self.ferr.pack(anchor="w")
        self.prev = tk.Label(panel, text="", font=FM,
                             fg=C["text"], bg=C["bg_dark"],
                             justify="left", padx=12, pady=10)
        self.dbtn = btn(panel, "Confirm Delete", self._delete,
                        bg=C["danger"], fg=C["white"], width=20)

    def _find(self):
        bid = self.did.get().strip().upper()
        b   = next((x for x in bookings if x["id"] == bid), None)
        if not b:
            self.ferr.config(text=f"Booking '{bid}' not found.")
            self.prev.pack_forget(); self.dbtn.pack_forget()
            self.found = None; return
        self.ferr.config(text="")
        self.found = b
        self.prev.config(text=(
            f"  ID     : {b['id']}\n"
            f"  Name   : {b['first_name']} {b['surname']}\n"
            f"  Car    : {b['car_type']}  |  Fuel : {b['fuel_type']}\n"
            f"  Days   : {b['days']}  |  Total : £{b['total_price']:.2f}\n"
            f"  Status : {b.get('status','Active')}"
        ))
        self.prev.pack(fill="x", pady=(10,6))
        self.dbtn.pack(pady=4)

    def _delete(self):
        if not self.found: return
        bid  = self.found["id"]
        name = f"{self.found['first_name']} {self.found['surname']}"
        if not ask(self, "Confirm Deletion",
                   f"\n  Permanently delete booking {bid}?\n\n"
                   f"  Customer : {name}\n"
                   f"  This cannot be undone.\n",
                   icon="!", icolor=C["danger"]):
            return
        bookings.remove(self.found)
        save_bookings(bookings)
        info(self, "Deleted", f"\n  Booking {bid} has been deleted.\n")
        self.prev.pack_forget(); self.dbtn.pack_forget()
        self.did.set(""); self.found = None
        self.ctrl.show_dashboard()

    def refresh(self):
        self.did.set(""); self.ferr.config(text="")
        self.prev.pack_forget(); self.dbtn.pack_forget()
        self.found = None


# ─────────────────────────────────────────────────────────────────────────────
#  ABOUT
# ─────────────────────────────────────────────────────────────────────────────
class AboutFrame(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=C["bg_dark"])
        self.ctrl = ctrl
        self._build()

    def _build(self):
        Sidebar(self, self.ctrl, "about").pack(side="left", fill="y")
        main = tk.Frame(self, bg=C["bg_dark"])
        main.pack(side="right", fill="both", expand=True)

        top = tk.Frame(main, bg=C["bg_mid"], padx=22, pady=13)
        top.pack(fill="x")
        tk.Label(top, text="About WeAreCars",
                 font=FT, fg=C["teal"], bg=C["bg_mid"]).pack(side="left")

        inner = scrollable(main)

        banner = tk.Frame(inner, bg=C["teal"], padx=28, pady=28)
        banner.pack(fill="x", padx=20, pady=16)
        tk.Label(banner, text="WeAreCars",
                 font=("Segoe UI", 30, "bold"),
                 fg=C["bg_dark"], bg=C["teal"]).pack()
        tk.Label(banner, text="Car Rental Management System  -  Staff",
                 font=("Segoe UI", 11),
                 fg=C["bg_dark"], bg=C["teal"]).pack(pady=(4,0))

        def section(title, items):
            tk.Label(inner, text=title, font=FH,
                     fg=C["blue"], bg=C["bg_dark"]
                     ).pack(anchor="w", padx=20, pady=(14,4))
            card = tk.Frame(inner, bg=C["bg_card"], padx=20, pady=14)
            card.pack(fill="x", padx=20, pady=(0,4))
            for line in items:
                tk.Label(card, text=line, font=FB,
                         fg=C["text"], bg=C["bg_card"],
                         anchor="w", justify="left").pack(anchor="w", pady=2)

        section("System Features", [
            "  Staff login with credential validation",
            "  Add new rental bookings with full validation",
            "  Real-time pricing calculator with breakdown",
            "  View all bookings with search and status filter",
            "  Double-click any booking to view full details",
            "  Sortable columns in the bookings table",
            "  Update booking details and rental status",
            "  Delete bookings with themed confirmation dialog",
            "  Live analytics dashboard with bar chart",
            "  Right-panel: staff info, pricing guide, shortcuts",
            "  Persistent JSON data storage",
        ])

        section("Pricing Structure", [
            f"  Base Rate           : £{BASE_RATE} per day",
            "",
            "  Car Type Surcharges:",
        ] + [f"    {ct:<20} : +£{p}" for ct, p in CAR_PRICES.items()] + [
            "",
            "  Fuel Type Surcharges:",
        ] + [f"    {ft:<20} : +£{p}" for ft, p in FUEL_PRICES.items()] + [
            "",
            f"  Unlimited Mileage   : +£{MILEAGE_RATE} per day",
            f"  Breakdown Cover     : +£{BREAKDOWN_RATE} per day",
        ])

        section("Keyboard Shortcuts", [
            "  F11    ->  Toggle fullscreen / windowed mode",
            "  Escape ->  Exit fullscreen",
            "  Enter  ->  Confirm / submit form",
        ])

        section("Technical Information", [
            "  Language   : Python 3",
            "  Framework  : Tkinter (standard library)",
            "  Storage    : JSON flat-file (wearecars_bookings.json)",
            "  Platform   : Windows / macOS / Linux",
        ])

        tk.Label(inner, text="(c) 2026 WeAreCars  -  For staff use only",
                 font=FSM, fg=C["text3"],
                 bg=C["bg_dark"]).pack(pady=18)


# ─────────────────────────────────────────────────────────────────────────────
#  APP CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WeAreCars - Car Rental Management System")

        self.geometry("1280x800")
        self.minsize(1050, 660)
        self._fs = False
        self.bind("<F11>",    self._toggle_fs)
        self.bind("<Escape>", self._exit_fs)

        self.configure(bg=C["bg_dark"])
        self.withdraw()

        try:
            self.iconbitmap("wearecars.ico")
        except Exception:
            pass

        self.cnt = tk.Frame(self, bg=C["bg_dark"])
        self.cnt.pack(fill="both", expand=True)

        self.frames = {}
        self._init()
        Splash(self, self._ready)

    def _init(self):
        self.frames = {
            "login":    LoginFrame(self.cnt, self.show_dashboard),
            "dashboard":DashboardFrame(self.cnt, self),
            "add":      AddBookingFrame(self.cnt, self),
            "view":     ViewBookingsFrame(self.cnt, self),
            "update":   UpdateBookingFrame(self.cnt, self),
            "delete":   DeleteBookingFrame(self.cnt, self),
            "about":    AboutFrame(self.cnt, self),
        }
        for f in self.frames.values():
            f.place(relwidth=1, relheight=1)

    def _show(self, name):
        f = self.frames[name]
        f.tkraise()
        if hasattr(f, "refresh"):
            f.refresh()

    def _ready(self):
        self.deiconify()
        self._show("login")

    def _toggle_fs(self, e=None):
        self._fs = not self._fs
        self.attributes("-fullscreen", self._fs)
        if not self._fs: self.geometry("1280x800")

    def _exit_fs(self, e=None):
        if self._fs:
            self._fs = False
            self.attributes("-fullscreen", False)
            self.geometry("1280x800")

    def show_login(self):          self._show("login")
    def show_dashboard(self):      self._show("dashboard")
    def show_add_booking(self):    self._show("add")
    def show_view_bookings(self):  self._show("view")
    def show_update_booking(self): self._show("update")
    def show_delete_booking(self): self._show("delete")
    def show_about(self):          self._show("about")


if __name__ == "__main__":
    App().mainloop()
