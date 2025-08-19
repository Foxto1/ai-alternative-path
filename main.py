import os
import threading
import queue
import time
from dotenv import load_dotenv
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

PROMPT_PREFIX = r"C:\> "


class TerminalApp:
    def __init__(self, root):
        self.root = root
        root.title("AI What If - Terminal")
        root.geometry("900x600")

        main = ttk.Frame(root)
        main.pack(fill="both", expand=True)

        self.output = scrolledtext.ScrolledText(
            main,
            wrap="word",
            font=("Consolas", 12),
            bg="black",
            fg="#e6e6e6",
            insertbackground="white",
            state="disabled",
        )
        self.output.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", padx=8, pady=(0,8))

        self.prompt_label = ttk.Label(bottom, text=PROMPT_PREFIX, font=("Consolas", 12))
        self.prompt_label.pack(side="left")

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(bottom, textvariable=self.input_var, font=("Consolas", 12))
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.bind("<Up>", self.on_history_up)
        self.input_entry.bind("<Down>", self.on_history_down)
        self.input_entry.focus_set()

        self.status_label = ttk.Label(bottom, text="ready", font=("Consolas", 10))
        self.status_label.pack(side="right", padx=(8,0))

        root.bind("<Control-c>", self.copy_selection)
        root.bind("<Control-C>", self.copy_selection)
        root.bind("<Control-s>", self.save_history_dialog)
        root.bind("<Control-S>", self.save_history_dialog)

        self.cmd_history = []
        self.history_idx = None
        self.loading = False
        self.loading_job = None

        self.result_queue = queue.Queue()

        self.root.after(100, self.check_queue)

        self.append_text("Alternative Path - terminal\nEnter the question, e.g. \"What if gravity suddenly stopped working?\"\n", "system")
        self.append_prompt()

    def append_text(self, text, tag=None, disable_scroll=False):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        if not disable_scroll:
            self.output.see("end")
        self.output.configure(state="disabled")

    def append_prompt(self):
        self.append_text(PROMPT_PREFIX)

    def clear_terminal(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.append_text("Alternative Path - terminal\nEnter the question, e.g. \"What if gravity suddenly stopped working?\"\n", "system")
        self.append_prompt()

    def on_enter(self, event=None):
        cmd = self.input_var.get().strip()
        if not cmd:
            return "break"

        if cmd.lower() == "cls":
            self.append_text(cmd + "\n")
            self.cmd_history.append(cmd)
            self.history_idx = None
            self.input_var.set("")
            self.clear_terminal()
            return "break"

        self.append_text(cmd + "\n")
        self.cmd_history.append(cmd)
        self.history_idx = None
        self.input_var.set("")
        self.start_ai_request(cmd)
        return "break"

    def on_history_up(self, event=None):
        if not self.cmd_history:
            return "break"
        if self.history_idx is None:
            self.history_idx = len(self.cmd_history) - 1
        else:
            self.history_idx = max(0, self.history_idx - 1)
        self.input_var.set(self.cmd_history[self.history_idx])
        self.input_entry.icursor("end")
        return "break"

    def on_history_down(self, event=None):
        if not self.cmd_history:
            return "break"
        if self.history_idx is None:
            return "break"
        self.history_idx += 1
        if self.history_idx >= len(self.cmd_history):
            self.history_idx = None
            self.input_var.set("")
        else:
            self.input_var.set(self.cmd_history[self.history_idx])
            self.input_entry.icursor("end")
        return "break"

    def copy_selection(self, event=None):
        try:
            sel = self.output.selection_get()
        except Exception:
            sel = self.input_var.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(sel)
        return "break"

    def save_history_dialog(self, event=None):
        try:
            fname = "alternative_path.txt"
            with open(fname, "w", encoding="utf-8") as f:
                txt = self.output.get("1.0", "end").rstrip()
                f.write(txt)
            self.status_label.config(text=f"saved: {fname}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        return "break"

    def start_ai_request(self, user_input):
        if self.loading:
            self.append_text("[! You have to wait for the previous answer]\n")
            return
        self.loading = True
        self.status_label.config(text="thinking")
        self.input_entry.configure(state="disabled")
        self.start_loading_anim()

        thread = threading.Thread(target=self.ai_worker, args=(user_input,), daemon=True)
        thread.start()

    def start_loading_anim(self):
        spinner = "|/-\\"
        def step(i=0):
            if not self.loading:
                self.status_label.config(text="ready")
                return
            self.status_label.config(text="thinking " + spinner[i % len(spinner)])
            self.loading_job = self.root.after(120, step, i+1)
        step(0)

    def stop_loading_anim(self):
        if self.loading_job:
            self.root.after_cancel(self.loading_job)
            self.loading_job = None

    def ai_worker(self, user_input):
        if not GEMINI_API_KEY:
            self.result_queue.put("[Błąd: brak GEMINI_API_KEY w .env]")
            return
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            full_prompt = (
                "You are an expert at exploring 'what if' scenarios.\n"
                "User will provide a hypothetical situation, starting with 'Załóżmy:'.\n"
                "Your task: respond in a structured, clear, professional way, adapting format to the scenario.\n"
                "- If it's about history -> create a timeline of events.\n"
                "- If it's about science/technology -> explain consequences and implications.\n"
                "- If it's about society/culture -> describe possible changes in daily life.\n"
                "Always be concise, logical, factual, and keep a consistent style (like a professional report).\n"
                f"Scenario: {user_input}\n"
                "Answer:"
            )
            resp = model.generate_content(full_prompt)
            text = resp.text
        except Exception as e:
            text = f"[Error: {e}]"
        self.result_queue.put(text)

    def check_queue(self):
        try:
            while True:
                text = self.result_queue.get_nowait()
                self.root.after(0, self.animate_ai_response, text)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def animate_ai_response(self, full_text):
        self.loading = False
        self.stop_loading_anim()
        self.append_text("AP: ")
        i = 0
        chunk = 4
        def step():
            nonlocal i
            if i >= len(full_text):
                self.append_text("\n")
                self.append_prompt()
                self.input_entry.configure(state="normal")
                self.input_entry.focus_set()
                self.status_label.config(text="ready")
                return
            piece = full_text[i:i+chunk]
            self.append_text(piece)
            i += chunk
            delay = 12
            if piece.endswith("\n"):
                delay = 60
            elif piece.endswith(".") or piece.endswith("!"):
                delay = 30
            self.root.after(delay, step)
        step()


def main():
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = TerminalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
