"""
╔══════════════════════════════════════════════════════════════╗
║              PROJECT 3: Chatbot App (Local AI)               ║
║──────────────────────────────────────────────────────────────║
║  INSTALLATION (Option A — API placeholder, no GPU needed):   ║
║    pip install requests                                       ║
║                                                              ║
║  INSTALLATION (Option B — local transformers):               ║
║    pip install transformers torch                            ║
║                                                              ║
║  RUN:                                                        ║
║    python project3_chatbot.py                               ║
║                                                              ║
║  NOTE: By default uses a simple rule-based engine so the    ║
║  app works offline with no GPU. Set USE_TRANSFORMERS=True   ║
║  below and choose a model to switch to a real LLM.          ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import datetime
import random

USE_TRANSFORMERS = False          # Set True + pick model for real LLM
TRANSFORMERS_MODEL = "facebook/blenderbot-400M-distill"


# ── Backend ──────────────────────────────────────────────────
class ChatBackend:
    def __init__(self):
        self.history = []
        self.pipe = None
        if USE_TRANSFORMERS:
            self._load_transformers()

    def _load_transformers(self):
        from transformers import pipeline
        self.pipe = pipeline("text2text-generation", model=TRANSFORMERS_MODEL)

    def respond(self, user_msg: str) -> str:
        self.history.append({"role": "user", "content": user_msg})
        if self.pipe:
            context = " ".join(m["content"] for m in self.history[-6:])
            out = self.pipe(context, max_new_tokens=128)[0]["generated_text"]
            reply = out.strip()
        else:
            reply = self._rule_based(user_msg)
        self.history.append({"role": "assistant", "content": reply})
        return reply

    _RULES = [
        (["hello", "hi", "hey"], ["Hey there! 👋", "Hello! How can I help?", "Hi! What's on your mind?"]),
        (["how are you", "how r u"], ["I'm running great, thanks for asking!", "All good on my end — you?"]),
        (["your name", "who are you"], ["I'm ChatBot 3000 — your local AI assistant."]),
        (["bye", "goodbye", "quit"], ["Goodbye! Come back soon 👋", "See you later!"]),
        (["thanks", "thank you"], ["You're welcome! 😊", "Happy to help!"]),
        (["help"], ["I can chat, answer questions, or just keep you company. Ask away!"]),
        (["weather"], ["I don't have live data, but I hope it's sunny wherever you are ☀️"]),
        (["time", "date"], [f"It's {datetime.datetime.now().strftime('%H:%M on %A, %B %d, %Y')}"]),
    ]
    _FALLBACKS = [
        "Interesting! Tell me more.",
        "I'm not sure about that, but I'm listening 🙂",
        "Could you elaborate? I want to understand better.",
        "That's a great point! What do you think about it?",
        "Hmm, let me think… what makes you ask that?",
    ]

    def _rule_based(self, msg: str) -> str:
        low = msg.lower()
        for keywords, replies in self._RULES:
            if any(k in low for k in keywords):
                return random.choice(replies)
        return random.choice(self._FALLBACKS)


# ── UI ────────────────────────────────────────────────────────
class ChatbotApp:
    BG      = "#111827"
    SURFACE = "#1f2937"
    ACCENT  = "#6366f1"
    USER_C  = "#6366f1"
    BOT_C   = "#10b981"
    TEXT    = "#f9fafb"
    MUTED   = "#6b7280"

    def __init__(self, root):
        self.root = root
        self.root.title("💬 ChatBot 3000")
        self.root.configure(bg=self.BG)
        self.root.geometry("520x680")
        self.backend = ChatBackend()
        self._build_ui()
        self._add_message("bot", "Hello! I'm ChatBot 3000. How can I help you today?")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=self.SURFACE)
        hdr.pack(fill="x")
        dot = tk.Label(hdr, text="⬤", fg=self.BOT_C, bg=self.SURFACE, font=("Arial", 10))
        dot.pack(side="left", padx=(16, 4), pady=14)
        tk.Label(hdr, text="ChatBot 3000", font=("Helvetica", 14, "bold"),
                 fg=self.TEXT, bg=self.SURFACE).pack(side="left")
        tk.Label(hdr, text="online", font=("Helvetica", 9),
                 fg=self.BOT_C, bg=self.SURFACE).pack(side="left", padx=8)

        # Chat area
        self.chat_frame = tk.Frame(self.root, bg=self.BG)
        self.chat_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(self.chat_frame, bg=self.BG, bd=0,
                                highlightthickness=0)
        scrollbar = tk.Scrollbar(self.chat_frame, command=self.canvas.yview,
                                 bg=self.BG, troughcolor=self.BG)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.msgs_frame = tk.Frame(self.canvas, bg=self.BG)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.msgs_frame,
                                                        anchor="nw")
        self.msgs_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Input row
        inp_row = tk.Frame(self.root, bg=self.SURFACE, pady=12)
        inp_row.pack(fill="x", side="bottom")

        self.entry = tk.Entry(inp_row, font=("Helvetica", 12), bg="#374151",
                              fg=self.TEXT, insertbackground=self.TEXT,
                              relief="flat", bd=0)
        self.entry.pack(side="left", fill="x", expand=True, padx=(16, 8), ipady=8)
        self.entry.bind("<Return>", lambda e: self._send())

        self.send_btn = tk.Button(inp_row, text="Send ➤",
                                  font=("Helvetica", 11, "bold"),
                                  bg=self.ACCENT, fg="white",
                                  activebackground="#4f46e5",
                                  activeforeground="white",
                                  bd=0, padx=16, pady=8,
                                  cursor="hand2", command=self._send)
        self.send_btn.pack(side="right", padx=(0, 16))

    def _on_frame_configure(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfig(self.canvas_window, width=e.width)

    def _add_message(self, role: str, text: str):
        is_user = role == "user"
        color  = self.USER_C if is_user else self.BOT_C
        anchor = "e" if is_user else "w"
        bg     = "#312e81" if is_user else "#064e3b"

        outer = tk.Frame(self.msgs_frame, bg=self.BG)
        outer.pack(fill="x", padx=12, pady=3, anchor=anchor)

        bubble = tk.Label(outer, text=text, font=("Helvetica", 11),
                          fg=self.TEXT, bg=bg, wraplength=340,
                          justify="left", padx=12, pady=8)
        bubble.pack(side="right" if is_user else "left")

        name = "You" if is_user else "Bot"
        ts = datetime.datetime.now().strftime("%H:%M")
        tk.Label(outer, text=f"{name} · {ts}", font=("Helvetica", 8),
                 fg=self.MUTED, bg=self.BG).pack(
                     side="right" if is_user else "left", padx=4)

        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    def _send(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, "end")
        self._add_message("user", msg)
        self.send_btn.configure(state="disabled")
        threading.Thread(target=self._get_reply, args=(msg,), daemon=True).start()

    def _get_reply(self, msg):
        reply = self.backend.respond(msg)
        self.root.after(0, self._add_message, "bot", reply)
        self.root.after(0, self.send_btn.configure, {"state": "normal"})


if __name__ == "__main__":
    root = tk.Tk()
    ChatbotApp(root)
    root.mainloop()
