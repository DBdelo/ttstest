import tkinter as tk
from tkinter import messagebox
import subprocess
import tempfile
import os
import threading

# Speech Synthesis（ブラウザ）を使うため、ローカルでHTMLを作って既定ブラウザで開きます。
# 入力した英文をボタンで読み上げます（端末の標準TTSに依存）。

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Speech Synthesis Test</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 20px; }}
    textarea {{ width: 100%; height: 160px; font-size: 16px; }}
    button {{ font-size: 16px; padding: 10px 14px; margin-right: 8px; }}
    .row {{ margin-top: 12px; }}
    .note {{ color: #444; font-size: 13px; margin-top: 10px; }}
  </style>
</head>
<body>
  <h2>Speech Synthesis Test</h2>
  <textarea id="t" placeholder="Type English text here..."></textarea>
  <div class="row">
    <button onclick="speak()">Speak</button>
    <button onclick="stopSpeak()">Stop</button>
  </div>
  <div class="note">
    Uses the browser's built-in SpeechSynthesis (voice/quality depends on device).
  </div>
<script>
  function pickEnglishVoice() {{
    const voices = speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;
    // Prefer en-US, else any English voice
    return voices.find(v => (v.lang || '').toLowerCase().startsWith('en-us'))
        || voices.find(v => (v.lang || '').toLowerCase().startsWith('en'))
        || null;
  }}

  function speak() {{
    const text = document.getElementById('t').value.trim();
    if (!text) return;

    // Stop any existing speech
    speechSynthesis.cancel();

    const u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    const v = pickEnglishVoice();
    if (v) u.voice = v;

    speechSynthesis.speak(u);
  }}

  function stopSpeak() {{
    speechSynthesis.cancel();
  }}

  // Some browsers populate voices asynchronously
  window.speechSynthesis.onvoiceschanged = () => {{}};
</script>
</body>
</html>
"""


def open_in_browser(html: str) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as f:
        f.write(html)
        path = f.name
    os.startfile(path)  # Windows: open default browser


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech Synthesis (Browser) Launcher")
        self.geometry("720x300")

        tk.Label(self, text="英文を入力して「Open & Speak」を押すと、ブラウザで読み上げます").pack(pady=(10, 6))

        self.text = tk.Text(self, height=9, wrap="word")
        self.text.pack(fill="both", expand=True, padx=10)

        btns = tk.Frame(self)
        btns.pack(pady=10)

        tk.Button(btns, text="Open & Speak", width=14, command=self.on_open).pack(side="left", padx=6)
        tk.Button(btns, text="Clear", width=14, command=lambda: self.text.delete("1.0", "end")).pack(side="left", padx=6)

    def on_open(self):
        text = self.text.get("1.0", "end").strip()
        if not text:
            return

        # 入力内容をHTMLに埋め込む（最低限のエスケープ）
        safe = (
            text.replace("\\", "\\\\")
                .replace("</", "<\\/")
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

        html = HTML_TEMPLATE.replace(
            '<textarea id="t" placeholder="Type English text here..."></textarea>',
            f'<textarea id="t">{safe}</textarea>'
        )

        try:
            threading.Thread(target=open_in_browser, args=(html,), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    App().mainloop()
