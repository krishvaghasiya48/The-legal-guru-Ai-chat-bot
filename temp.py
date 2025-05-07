import tkinter as tk
from tkinter import ttk, scrolledtext
from Backend import generate_legal_response  # Ensure this module exists
import time
from datetime import datetime
import json
import os

class ModernUI(tk.Tk):
    def __init__(self):  # Fixed from _init_ to __init__
        super().__init__()  # Fixed from super()._init_() to super().__init__()
        self.title("LegalGuru - AI Legal Assistant")
        self.geometry("900x700")
        self.configure(bg="#181A1F")  # Dark theme background
        self.minsize(500, 500)
        
        self.id_counter = 0
        self.setup_storage()
        
        try:
            self.logo_image = tk.PhotoImage(file="1.png")
            self.logo_image = self.make_image_round(self.logo_image.subsample(16, 16))
        except Exception as e:
            print(f"Error loading logo image: {e}")
            self.logo_image = None
        
        self.setup_layout()
        self.chat_history = []
        self.add_message("Hello! I'm LegalGuru. How can I assist you with legal matters today?", "bot")
    
    def setup_storage(self):
        self.storage_path = "chat_storage"
        os.makedirs(self.storage_path, exist_ok=True)
        self.messages_file = os.path.join(self.storage_path, "messages.json")
        if not os.path.exists(self.messages_file):
            with open(self.messages_file, 'w') as f:
                json.dump([], f)
    
    def setup_layout(self):
        # Header
        self.header = tk.Frame(self, bg="#202123", height=70)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        logo = tk.Label(self.header, text="⚖", font=("Segoe UI", 28), bg="#202123", fg="#0084ff")
        logo.pack(side=tk.LEFT, padx=26)
        
        title_frame = tk.Frame(self.header, bg="#202123")
        title_frame.pack(side=tk.LEFT)
        
        title = tk.Label(title_frame, text="LegalGuru", font=("Segoe UI", 20, "bold"), bg="#202123", fg="#FFFFFF")
        title.pack(anchor=tk.W)
        subtitle = tk.Label(title_frame, text="AI Legal Assistant", font=("Segoe UI", 12), bg="#202123", fg="#ACACBE")
        subtitle.pack(anchor=tk.W)
        
        clear_btn = tk.Button(self.header, text="Clear Chat", font=("Segoe UI", 11), 
                             bg="#343541", fg="#FFFFFF", bd=0, padx=15, pady=5,
                             command=self.clear_chat, cursor="hand2")
        clear_btn.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Chat area
        self.chat_container = tk.Frame(self, bg="#181A1F")
        self.chat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
        
        self.canvas = tk.Canvas(self.chat_container, bg="#181A1F", highlightthickness=0)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", background="#343541", troughcolor="#181A1F", 
                        arrowcolor="#FFFFFF", bordercolor="#181A1F")
        self.scrollbar = ttk.Scrollbar(self.chat_container, orient=tk.VERTICAL, command=self.canvas.yview, 
                                      style="Vertical.TScrollbar")
        self.messages_frame = tk.Frame(self.canvas, bg="#181A1F")
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.chat_container.bind("<Configure>", self.on_frame_configure)
        self.bind("<Configure>", self.on_window_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input area
        self.input_container = tk.Frame(self, bg="#343541", height=80)
        self.input_container.pack(fill=tk.X, side=tk.BOTTOM)
        self.input_container.pack_propagate(False)
        
        self.input_frame = tk.Frame(self.input_container, bg="#343541", padx=20, pady=15)
        self.input_frame.pack(fill=tk.BOTH, expand=True)
        
        self.input_field = tk.Entry(self.input_frame, font=("Segoe UI", 12), bg="#40414F", fg="#FFFFFF",
                                  insertbackground="#FFFFFF", bd=0, relief=tk.FLAT, highlightthickness=1,
                                  highlightbackground="#565869", highlightcolor="#0084ff")
        self.input_field.insert(0, "Type a message...")
        self.input_field.config(fg="#ACACBE")
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        
        self.placeholder_active = True
        self.input_field.bind("<FocusIn>", self.on_entry_focus_in)
        self.input_field.bind("<FocusOut>", self.on_entry_focus_out)
        self.input_field.bind("<Return>", self.send_message_event)
        
        self.send_btn = tk.Button(self.input_frame, text="Send", font=("Segoe UI", 12, "bold"), 
                                bg="#0084ff", fg="white", bd=0, padx=20, pady=8,
                                command=self.send_message, cursor="hand2",
                                activebackground="#0078e7", activeforeground="white")
        self.send_btn.pack(side=tk.RIGHT)
    
    def on_frame_configure(self, event):
        width = self.chat_container.winfo_width() - self.scrollbar.winfo_width() - 5
        self.canvas.configure(width=width)
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def on_window_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def generate_unique_id(self):
        timestamp = int(time.time() * 1000)
        self.id_counter += 1
        return f"{timestamp}_{self.id_counter}"
    
    def on_entry_focus_in(self, event):
        if self.placeholder_active:
            self.input_field.delete(0, tk.END)
            self.input_field.config(fg="#FFFFFF")
            self.placeholder_active = False
    
    def on_entry_focus_out(self, event):
        if self.input_field.get() == "":
            self.input_field.config(fg="#ACACBE")
            self.input_field.insert(0, "Type a message...")
            self.placeholder_active = True
    
    def send_message_event(self, event):
        if not self.placeholder_active:
            self.send_message()
    
    def send_message(self):
        message = self.input_field.get().strip()
        if message and message != "Type a message...":
            self.add_message(message, "user")
            self.input_field.delete(0, tk.END)
            typing_indicator = self.add_typing_indicator()
            self.update()
            response = generate_legal_response(message)
            typing_indicator.destroy()
            self.add_message(response, "bot")

    def add_message(self, message, sender):
        msg_frame = tk.Frame(self.messages_frame, bg="#181A1F", pady=8)
        msg_frame.pack(fill=tk.X)
        
        if sender == "user":
            container = tk.Frame(msg_frame, bg="#181A1F")
            container.pack(side=tk.RIGHT, anchor=tk.E)
            sender_label = tk.Label(container, text="You", font=("Segoe UI", 10, "bold"), 
                                  bg="#181A1F", fg="#ACACBE")
            sender_label.pack(anchor=tk.E)
            bubble = self.create_bubble(container, message, "#343541", "#FFFFFF")
            bubble.pack(anchor=tk.E)
            timestamp = tk.Label(container, text=datetime.now().strftime("%I:%M %p"), 
                               font=("Segoe UI", 8), bg="#181A1F", fg="#ACACBE")
            timestamp.pack(anchor=tk.E, pady=(2, 0))
        else:
            container = tk.Frame(msg_frame, bg="#181A1F")
            container.pack(side=tk.LEFT, anchor=tk.W)
            avatar_container = tk.Frame(container, bg="#181A1F")
            avatar_container.pack(side=tk.LEFT, anchor=tk.NW, padx=(0, 8))
            if self.logo_image:
                avatar = tk.Label(avatar_container, image=self.logo_image, bg="#181A1F", bd=0)
                avatar.pack(pady=(24, 4))
            else:
                avatar = tk.Label(avatar_container, text="👨🏻‍⚖", font=("Segoe UI", 24), 
                                bg="#181A1F", fg="#0084ff")
                avatar.pack()
            msg_container = tk.Frame(container, bg="#181A1F")
            msg_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
            sender_label = tk.Label(msg_container, text="LegalGuru", font=("Segoe UI", 10, "bold"), 
                                  bg="#181A1F", fg="#ACACBE")
            sender_label.pack(anchor=tk.W)
            bubble = self.create_bubble(msg_container, message, "#444654", "#FFFFFF")
            bubble.pack(anchor=tk.W)
            timestamp = tk.Label(msg_container, text=datetime.now().strftime("%I:%M %p"), 
                               font=("Segoe UI", 8), bg="#181A1F", fg="#ACACBE")
            timestamp.pack(anchor=tk.W, pady=(2, 0))
        
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
        message_id = self.generate_unique_id()
        message_data = {"id": message_id, "sender": sender, "message": message, "time": datetime.now().isoformat()}
        self.chat_history.append(message_data)
        self.store_message(message_data)
    
    def store_message(self, message_data):
        try:
            with open(self.messages_file, 'r') as f:
                messages = json.load(f)
        except:
            messages = []
        messages.append(message_data)
        with open(self.messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
    
    def create_bubble(self, parent, message, bg_color, text_color):
        # Calculate wraplength
        msg_length = len(message)
        lines = message.count('\n') + 1
        has_long_words = any(len(word) > 30 for word in message.split())
        has_code = '```' in message or message.count('    ') > 2
        available_width = max(200, self.winfo_width() - 200)  # Ensure minimum width
        if has_code or has_long_words:
            wrap_length = min(700, max(400, available_width))
        else:
            wrap_length = min(max(300, min(msg_length * 7, available_width)), available_width)
        if lines > 1:
            avg_line_length = msg_length / max(1, lines)
            wrap_length = min(max(300, min(avg_line_length * 10, available_width)), available_width)
        
        padding_x, padding_y = 20, 10
        radius = 15
        
        # Create canvas
        canvas = tk.Canvas(parent, bg="#181A1F", highlightthickness=0)
        
        # Estimate initial size and draw bubble first
        temp_label = tk.Label(self, text=message, font=("Segoe UI", 11), wraplength=wrap_length)
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        canvas_width = text_width + 2 * padding_x
        canvas_height = text_height + 2 * padding_y
        canvas.configure(width=canvas_width, height=canvas_height)
        
        # Draw rounded rectangle
        x0, y0 = 0, 0
        x1, y1 = canvas_width, canvas_height
        canvas.create_arc(x0, y0, x0 + 2*radius, y0 + 2*radius, start=90, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(x1 - 2*radius, y0, x1, y0 + 2*radius, start=0, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(x0, y1 - 2*radius, x0 + 2*radius, y1, start=180, extent=90, fill=bg_color, outline='')
        canvas.create_arc(x1 - 2*radius, y1 - 2*radius, x1, y1, start=270, extent=90, fill=bg_color, outline='')
        canvas.create_rectangle(x0 + radius, y0, x1 - radius, y0 + radius, fill=bg_color, outline='')
        canvas.create_rectangle(x0 + radius, y1 - radius, x1 - radius, y1, fill=bg_color, outline='')
        canvas.create_rectangle(x0, y0 + radius, x0 + radius, y1 - radius, fill=bg_color, outline='')
        canvas.create_rectangle(x1 - radius, y0 + radius, x1, y1 - radius, fill=bg_color, outline='')
        canvas.create_rectangle(x0 + radius, y0 + radius, x1 - radius, y1 - radius, fill=bg_color, outline='')
        
        # Add text on top
        canvas.create_text(canvas_width/2, canvas_height/2, text=message, anchor='center', width=wrap_length, 
                          font=("Segoe UI", 11), fill=text_color)
        
        return canvas
    
    def add_typing_indicator(self):
        typing_frame = tk.Frame(self.messages_frame, bg="#181A1F", pady=8)
        typing_frame.pack(fill=tk.X)
        container = tk.Frame(typing_frame, bg="#181A1F")
        container.pack(side=tk.LEFT, anchor=tk.W)
        avatar_container = tk.Frame(container, bg="#181A1F")
        avatar_container.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        if self.logo_image:
            avatar = tk.Label(avatar_container, image=self.logo_image, bg="#181A1F")
        else:
            avatar = tk.Label(avatar_container, text="👨🏻‍⚖", font=("Segoe UI", 24), bg="#181A1F", fg="#0084ff")
        avatar.pack()
        indicator_container = tk.Frame(container, bg="#444654", padx=12, pady=10)
        indicator_container.pack(side=tk.LEFT)
        sender_label = tk.Label(indicator_container, text="LegalGuru", font=("Segoe UI", 10, "bold"), 
                              bg="#181A1F", fg="#ACACBE")
        sender_label.pack(anchor=tk.W)
        typing_bubble = tk.Frame(indicator_container, bg="#444654", padx=12, pady=10)
        typing_bubble.pack(anchor=tk.W)
        dots_frame = tk.Frame(typing_bubble, bg="#444654")
        dots_frame.pack()
        self.dots = [tk.Label(dots_frame, text="•", font=("Segoe UI", 16), bg="#444654", fg="white") for _ in range(3)]
        for dot in self.dots:
            dot.pack(side=tk.LEFT, padx=2)
        self.animate_dots(0, typing_frame)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        return typing_frame
    
    def animate_dots(self, dot_index, typing_frame):
        if not typing_frame.winfo_exists():
            return
        for dot in self.dots:
            if dot.winfo_exists():
                dot.configure(fg="white")
        if self.dots[dot_index].winfo_exists():
            self.dots[dot_index].configure(fg="#b3d9ff")
        next_dot = (dot_index + 1) % len(self.dots)
        typing_frame.after(400, lambda: self.animate_dots(next_dot, typing_frame))
    
    def clear_chat(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self.chat_history = []
        with open(self.messages_file, 'w') as f:
            json.dump([], f)
        self.add_message("Hello! I'm LegalGuru. How can I assist you with legal matters today?", "bot")

    def make_image_round(self, image):
        from PIL import Image, ImageTk, ImageDraw
        # Convert PhotoImage to PIL Image
        width, height = image.width(), image.height()
        # Create a new PIL image with the same size
        pil_image = Image.new('RGBA', (width, height))
        # Create circular mask
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, width, height), fill=255)
        # Apply mask
        pil_image.putalpha(mask)
        return ImageTk.PhotoImage(pil_image)

if __name__ == "__main__":
    app = ModernUI()
    app.mainloop()