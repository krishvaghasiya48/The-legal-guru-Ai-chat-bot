import tkinter as tk
from tkinter import ttk
from Backend import generate_legal_response
import time
from datetime import datetime
import json
import os

class ModernUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LegalGuru - Your Personal Legal Assistant")
        self.geometry("900x700")
        self.configure(bg="#181A1F")
        self.minsize(500, 500)
        
        self.id_counter = 0
        self.setup_storage()
        
        # Load logo image
        try:
            self.logo_image = tk.PhotoImage(file="1.png")
            self.logo_image = self.make_image_round(self.logo_image.subsample(16, 16))
        except Exception as e:
            print(f"Error loading logo image: {e}")
            self.logo_image = None
        
        self.setup_layout()
        self.chat_history = []
        self.add_message("Hello! I'm LegalGuru, your personal legal assistant. How can I help you today? Feel free to ask me any legal questions you might have.", "bot")
    
    def setup_storage(self):
        self.storage_path = "chat_storage"
        os.makedirs(self.storage_path, exist_ok=True)
        self.messages_file = os.path.join(self.storage_path, "messages.json")
        if not os.path.exists(self.messages_file):
            with open(self.messages_file, 'w') as f:
                json.dump([], f)
    
    def setup_layout(self):
        # Header with more personality
        self.header = tk.Frame(self, bg="#202123", height=70)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # Friendlier logo and title
        tk.Label(self.header, text="⚖️", font=("Segoe UI", 28), bg="#202123", fg="#0084ff").pack(side=tk.LEFT, padx=26)
        
        title_frame = tk.Frame(self.header, bg="#202123")
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(title_frame, text="LegalGuru", font=("Segoe UI", 20, "bold"), bg="#202123", fg="#FFFFFF").pack(anchor=tk.W)
        tk.Label(title_frame, text="Your Personal Legal Assistant", font=("Segoe UI", 12), bg="#202123", fg="#ACACBE").pack(anchor=tk.W)
        
        # More friendly button text
        clear_btn = tk.Button(self.header, text="Clear Chat", font=("Segoe UI", 11), bg="#343541", fg="#FFFFFF", bd=0, 
                             padx=15, pady=5, command=self.clear_chat, cursor="hand2",
                             relief=tk.FLAT, highlightthickness=1, highlightbackground="#343541")
        clear_btn.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Chat area
        self.chat_container = tk.Frame(self, bg="#181A1F")
        self.chat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
        
        # Canvas with scrollbar
        self.canvas = tk.Canvas(self.chat_container, bg="#181A1F", highlightthickness=0)
        
        # Style scrollbar
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
        
        # Bind events
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
        
        # Text input
        self.input_field = tk.Entry(self.input_frame, font=("Segoe UI", 12), bg="#40414F", fg="#ACACBE",
                                  insertbackground="#FFFFFF", bd=0, relief=tk.FLAT, highlightthickness=1,
                                  highlightbackground="#565869", highlightcolor="#0084ff")
        self.input_field.insert(0, "Type a message...")
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        
        self.placeholder_active = True
        self.input_field.bind("<FocusIn>", self.on_entry_focus_in)
        self.input_field.bind("<FocusOut>", self.on_entry_focus_out)
        self.input_field.bind("<Return>", self.send_message_event)
        
        # Send button
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
            
            # Show typing indicator
            typing_indicator = self.add_typing_indicator()
            self.update()
            
            # Get response immediately without delay
            response = generate_legal_response(message)
            typing_indicator.destroy()
            self.add_message(response, "bot")

    def add_message(self, message, sender):
        msg_frame = tk.Frame(self.messages_frame, bg="#181A1F", pady=8)
        msg_frame.pack(fill=tk.X)
        
        if sender == "user":
            container = tk.Frame(msg_frame, bg="#181A1F")
            container.pack(side=tk.RIGHT, anchor=tk.E)
            
            tk.Label(container, text="You", font=("Segoe UI", 10, "bold"), 
                   bg="#181A1F", fg="#ACACBE").pack(anchor=tk.E)
            
            bubble = self.create_bubble(container, message, "#343541", "#FFFFFF")
            bubble.pack(anchor=tk.E)
            
            tk.Label(container, text=datetime.now().strftime("%I:%M %p"), 
                   font=("Segoe UI", 8), bg="#181A1F", fg="#ACACBE").pack(anchor=tk.E, pady=(2, 0))
        else:
            container = tk.Frame(msg_frame, bg="#181A1F")
            container.pack(side=tk.LEFT, anchor=tk.W)
            
            avatar_container = tk.Frame(container, bg="#181A1F")
            avatar_container.pack(side=tk.LEFT, anchor=tk.NW, padx=(0, 8))
            
            if self.logo_image:
                tk.Label(avatar_container, image=self.logo_image, bg="#181A1F", bd=0).pack(pady=(24, 4))
            else:
                tk.Label(avatar_container, text="👨🏻‍⚖️", font=("Segoe UI", 24), 
                       bg="#181A1F", fg="#0084ff").pack()
            
            msg_container = tk.Frame(container, bg="#181A1F")
            msg_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            tk.Label(msg_container, text="LegalGuru", font=("Segoe UI", 10, "bold"), 
                   bg="#181A1F", fg="#ACACBE").pack(anchor=tk.W)
            
            bubble = self.create_bubble(msg_container, message, "#444654", "#FFFFFF")
            bubble.pack(anchor=tk.W)
            
            tk.Label(msg_container, text=datetime.now().strftime("%I:%M %p"), 
                   font=("Segoe UI", 8), bg="#181A1F", fg="#ACACBE").pack(anchor=tk.W, pady=(2, 0))
        
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
        message_data = {
            "id": self.generate_unique_id(),
            "sender": sender, 
            "message": message, 
            "time": datetime.now().isoformat()
        }
        self.chat_history.append(message_data)
        self.store_message(message_data)
    
    def store_message(self, message_data):
        try:
            try:
                with open(self.messages_file, 'r') as f:
                    messages = json.load(f)
            except:
                messages = []
            
            messages.append(message_data)
            
            with open(self.messages_file, 'w') as f:
                json.dump(messages, f, indent=2)
                
        except Exception as e:
            print(f"Error storing message: {e}")
    
    def create_bubble(self, parent, message, bg_color, text_color):
        # Create a more friendly bubble with rounded corners
        bubble_frame = tk.Frame(parent, bg=bg_color, padx=12, pady=10, bd=0)
        
        # Calculate wrap length
        msg_length = len(message)
        available_width = self.winfo_width() - 200
        has_code = '```' in message or message.count('    ') > 2
        has_long_words = any(len(word) > 30 for word in message.split())
        
        if has_code or has_long_words:
            wrap_length = min(700, max(400, available_width))
        else:
            wrap_length = min(max(300, min(msg_length * 7, available_width)), available_width)
        
        # More readable text with better spacing
        tk.Label(bubble_frame, text=message, justify=tk.LEFT, wraplength=wrap_length,
               bg=bg_color, fg=text_color, font=("Segoe UI", 11), padx=2, pady=2).pack()
        
        # Enhanced rounded corners
        bubble_frame.configure(highlightbackground=bg_color, highlightthickness=2, 
                           highlightcolor=bg_color, relief=tk.FLAT)
        return bubble_frame
    
    def add_typing_indicator(self):
        typing_frame = tk.Frame(self.messages_frame, bg="#181A1F", pady=8)
        typing_frame.pack(fill=tk.X)
        
        container = tk.Frame(typing_frame, bg="#181A1F")
        container.pack(side=tk.LEFT, anchor=tk.W)
        
        avatar_container = tk.Frame(container, bg="#181A1F")
        avatar_container.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        
        if self.logo_image:
            tk.Label(avatar_container, image=self.logo_image, bg="#181A1F").pack()
        else:
            tk.Label(avatar_container, text="👨🏻‍⚖️", font=("Segoe UI", 24), 
                   bg="#181A1F", fg="#0084ff").pack()
        
        indicator_container = tk.Frame(container, bg="#181A1F")
        indicator_container.pack(side=tk.LEFT)
        
        tk.Label(indicator_container, text="LegalGuru", font=("Segoe UI", 10, "bold"), 
               bg="#181A1F", fg="#ACACBE").pack(anchor=tk.W)
        
        typing_bubble = tk.Frame(indicator_container, bg="#444654", padx=12, pady=10)
        typing_bubble.pack(anchor=tk.W)
        
        dots_frame = tk.Frame(typing_bubble, bg="#444654")
        dots_frame.pack()
        
        self.dots = []
        for i in range(3):
            dot = tk.Label(dots_frame, text="•", font=("Segoe UI", 16), bg="#444654", fg="white")
            dot.pack(side=tk.LEFT, padx=2)
            self.dots.append(dot)
        
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
        
        # More welcoming restart message
        self.add_message("I've cleared our conversation. What legal matter can I help you with now?", "bot")

    def make_image_round(self, image):
        from PIL import Image, ImageTk, ImageDraw
        
        pil_image = Image.open("1.png").resize((image.width(), image.height()), Image.LANCZOS)
        mask = Image.new('L', pil_image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + pil_image.size, fill=255)
        
        pil_image.putalpha(mask)
        return ImageTk.PhotoImage(pil_image)

if __name__ == "__main__":
    app = ModernUI()
    app.mainloop()