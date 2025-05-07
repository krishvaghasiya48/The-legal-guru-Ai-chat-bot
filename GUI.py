import tkinter as tk
from tkinter import ttk, scrolledtext
from Backend import generate_legal_response
import time
from datetime import datetime
import json
import os
# import uuid removed

class ModernUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LegalGuru - AI Legal Assistant")
        self.geometry("900x700")
        # Change to dark theme
        self.configure(bg="#181A1F")
        self.minsize(500, 500)
        
        # Counter for generating unique IDs
        self.id_counter = 0
        
        # Initialize storage
        self.setup_storage()
        
        # Load the advocate logo image
        try:
            self.logo_image = tk.PhotoImage(file="1.png")
            # Resize and make round
            self.logo_image = self.make_image_round(self.logo_image.subsample(16, 16))
        except Exception as e:
            print(f"Error loading logo image: {e}")
            self.logo_image = None
        
        # Set up the main layout
        self.setup_layout()
        
        # Initialize chat history
        self.chat_history = []
        
        # Add welcome message (always show it since we're not loading history)
        self.add_message("Hello! I'm LegalGuru. How can I assist you with legal matters today?", "bot")
    
    def setup_storage(self):
        """Initialize storage for chat history"""
        # Create a directory for the chat storage if it doesn't exist
        self.storage_path = "chat_storage"
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Path to the single JSON file for all messages
        self.messages_file = os.path.join(self.storage_path, "messages.json")
        
        # Create the file if it doesn't exist
        if not os.path.exists(self.messages_file):
            with open(self.messages_file, 'w') as f:
                json.dump([], f)
    
    def setup_layout(self):
        # Header - dark theme
        self.header = tk.Frame(self, bg="#202123", height=70)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # Logo and title
        logo = tk.Label(self.header, text="⚖️", font=("Segoe UI", 28), bg="#202123", fg="#0084ff")
        logo.pack(side=tk.LEFT, padx=26)
        
        title_frame = tk.Frame(self.header, bg="#202123")
        title_frame.pack(side=tk.LEFT)
        
        title = tk.Label(title_frame, text="LegalGuru", font=("Segoe UI", 20, "bold"), bg="#202123", fg="#FFFFFF")
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="AI Legal Assistant", font=("Segoe UI", 12), bg="#202123", fg="#ACACBE")
        subtitle.pack(anchor=tk.W)
        
        # Clear chat button - dark theme
        clear_btn = tk.Button(self.header, text="Clear Chat", font=("Segoe UI", 11), 
                             bg="#343541", fg="#FFFFFF", bd=0, padx=15, pady=5,
                             command=self.clear_chat, cursor="hand2")
        clear_btn.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Chat area - dark theme
        self.chat_container = tk.Frame(self, bg="#181A1F")
        self.chat_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
        
        # Create canvas with scrollbar for messages
        self.canvas = tk.Canvas(self.chat_container, bg="#181A1F", highlightthickness=0)
        
        # Style the scrollbar for dark theme
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
        
        # Bind resize events
        self.chat_container.bind("<Configure>", self.on_frame_configure)
        self.bind("<Configure>", self.on_window_configure)
        
        # Bind mousewheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input area - dark theme
        self.input_container = tk.Frame(self, bg="#343541", height=80)
        self.input_container.pack(fill=tk.X, side=tk.BOTTOM)
        self.input_container.pack_propagate(False)
        
        self.input_frame = tk.Frame(self.input_container, bg="#343541", padx=20, pady=15)
        self.input_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text input with placeholder - dark theme
        self.input_field = tk.Entry(self.input_frame, font=("Segoe UI", 12), bg="#40414F", fg="#FFFFFF",
                                  insertbackground="#FFFFFF", bd=0, relief=tk.FLAT, highlightthickness=1,
                                  highlightbackground="#565869", highlightcolor="#0084ff")
        self.input_field.insert(0, "Type a message...")
        self.input_field.config(fg="#ACACBE")  # Placeholder color
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        
        # Placeholder handling
        self.placeholder_active = True
        self.input_field.bind("<FocusIn>", self.on_entry_focus_in)
        self.input_field.bind("<FocusOut>", self.on_entry_focus_out)
        self.input_field.bind("<Return>", self.send_message_event)
        
        # Send button - dark theme
        self.send_btn = tk.Button(self.input_frame, text="Send", font=("Segoe UI", 12, "bold"), 
                                bg="#0084ff", fg="white", bd=0, padx=20, pady=8,
                                command=self.send_message, cursor="hand2",
                                activebackground="#0078e7", activeforeground="white")
        self.send_btn.pack(side=tk.RIGHT)
    
    def on_frame_configure(self, event):
        # Update canvas and window width when frame is resized
        width = self.chat_container.winfo_width() - self.scrollbar.winfo_width() - 5
        self.canvas.configure(width=width)
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def on_window_configure(self, event):
        # Update scrollregion when window is resized
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def generate_unique_id(self):
        """Generate a unique ID using timestamp and counter"""
        timestamp = int(time.time() * 1000)  # Milliseconds since epoch
        self.id_counter += 1
        return f"{timestamp}_{self.id_counter}"
    
    def on_entry_focus_in(self, event):
        if self.placeholder_active:
            self.input_field.delete(0, tk.END)
            self.input_field.config(fg="#FFFFFF")  # Changed to white for dark theme
            self.placeholder_active = False
    
    def on_entry_focus_out(self, event):
        if self.input_field.get() == "":
            self.input_field.config(fg="#ACACBE")  # Changed to light gray for dark theme
            self.input_field.insert(0, "Type a message...")
            self.placeholder_active = True
    
    def send_message_event(self, event):
        if not self.placeholder_active:
            self.send_message()
    
    def send_message(self):
        message = self.input_field.get().strip()
        if message and message != "Type a message...":
            # Add user message to chat
            self.add_message(message, "user")
            
            # Clear input field
            self.input_field.delete(0, tk.END)
            
            # Show typing indicator
            typing_indicator = self.add_typing_indicator()
            
            # Update UI
            self.update()
            
            # Get AI response
            response = generate_legal_response(message)
            
            # Remove typing indicator
            typing_indicator.destroy()
            
            # Add bot response
            self.add_message(response, "bot")

    def add_message(self, message, sender):
        # Create message frame
        msg_frame = tk.Frame(self.messages_frame, bg="#181A1F", pady=8)
        msg_frame.pack(fill=tk.X)
        
        # Configure message appearance based on sender
        if sender == "user":
            # User message (right-aligned)
            container = tk.Frame(msg_frame, bg="#181A1F")
            container.pack(side=tk.RIGHT, anchor=tk.E)
            
            # Add "You" label
            sender_label = tk.Label(container, text="You", font=("Segoe UI", 10, "bold"), 
                                  bg="#181A1F", fg="#ACACBE")
            sender_label.pack(anchor=tk.E)
            
            # Message bubble - dark theme
            bubble_bg = "#343541"
            text_color = "#FFFFFF"
            
            bubble = self.create_bubble(container, message, bubble_bg, text_color)
            bubble.pack(anchor=tk.E)
            
            # Timestamp
            timestamp = tk.Label(container, text=datetime.now().strftime("%I:%M %p"), 
                               font=("Segoe UI", 8), bg="#181A1F", fg="#ACACBE")
            timestamp.pack(anchor=tk.E, pady=(2, 0))
            
        else:
            # Bot message (left-aligned)
            container = tk.Frame(msg_frame, bg="#181A1F")
            container.pack(side=tk.LEFT, anchor=tk.W)
            
            # Avatar and message container
            avatar_container = tk.Frame(container, bg="#181A1F")
            avatar_container.pack(side=tk.LEFT, anchor=tk.NW, padx=(0, 8))  # Changed anchor to NW and reduced padding
            
            # Avatar - use logo image if available, otherwise use emoji
            if self.logo_image:
                avatar = tk.Label(avatar_container, image=self.logo_image, bg="#181A1F", bd=0)
                avatar.pack(pady=(24, 4))  # Added small vertical padding
            else:
                avatar = tk.Label(avatar_container, text="👨🏻‍⚖️", font=("Segoe UI", 24), 
                                bg="#181A1F", fg="#0084ff")
                avatar.pack()
            
            # Message container
            msg_container = tk.Frame(container, bg="#181A1F")
            msg_container.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Added fill and expand
            
            # Add "LegalGuru" label
            sender_label = tk.Label(msg_container, text="LegalGuru", font=("Segoe UI", 10, "bold"), 
                                  bg="#181A1F", fg="#ACACBE")
            sender_label.pack(anchor=tk.W)
            
            # Message bubble - dark theme
            bubble_bg = "#444654"
            text_color = "#FFFFFF"
            
            bubble = self.create_bubble(msg_container, message, bubble_bg, text_color)
            bubble.pack(anchor=tk.W)
            
            # Timestamp
            timestamp = tk.Label(msg_container, text=datetime.now().strftime("%I:%M %p"), 
                               font=("Segoe UI", 8), bg="#181A1F", fg="#ACACBE")
            timestamp.pack(anchor=tk.W, pady=(2, 0))
        
        # Scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
        # Create timestamp for the message
        timestamp_str = datetime.now().isoformat()
        
        # Generate a unique ID for the message
        message_id = self.generate_unique_id()
        
        # Add to chat history
        message_data = {
            "id": message_id,
            "sender": sender, 
            "message": message, 
            "time": timestamp_str
        }
        self.chat_history.append(message_data)
        
        # Store in JSON
        self.store_message(message_data)
    
    def store_message(self, message_data):
        """Store a message in the single JSON file"""
        try:
            # Load existing messages
            try:
                with open(self.messages_file, 'r') as f:
                    messages = json.load(f)
            except:
                messages = []
            
            # Add new message
            messages.append(message_data)
            
            # Save all messages back to file
            with open(self.messages_file, 'w') as f:
                json.dump(messages, f, indent=2)
                
        except Exception as e:
            print(f"Error storing message: {e}")
    
    def create_bubble(self, parent, message, bg_color, text_color):
        # Create bubble frame
        bubble_frame = tk.Frame(parent, bg=bg_color, padx=12, pady=10, bd=0)
        
        # Calculate appropriate width based on message content
        msg_length = len(message)
        lines = message.count('\n') + 1
        
        # Determine if message contains code or long words
        has_long_words = any(len(word) > 30 for word in message.split())
        has_code = '```' in message or message.count('    ') > 2
        
        # Calculate appropriate wraplength
        available_width = self.winfo_width() - 200  # Account for padding and avatar
        
        if has_code or has_long_words:
            # Code blocks or long words need more width
            wrap_length = min(700, max(400, available_width))
        else:
            # Regular text can be more compact
            wrap_length = min(max(300, min(msg_length * 7, available_width)), available_width)
        
        # Adjust for multiline messages
        if lines > 1:
            avg_line_length = msg_length / max(1, lines)  # Prevent division by zero
            wrap_length = min(max(300, min(avg_line_length * 10, available_width)), available_width)
        
        # Message text
        message_text = tk.Label(bubble_frame, text=message, justify=tk.LEFT, 
                              wraplength=wrap_length, bg=bg_color, fg=text_color,
                              font=("Segoe UI", 11))
        message_text.pack()
        
        # Round the corners with a custom style
        bubble_frame.configure(highlightbackground=bg_color, highlightthickness=1, highlightcolor=bg_color)
        
        return bubble_frame
    
    def add_typing_indicator(self):
        # Create typing indicator frame
        typing_frame = tk.Frame(self.messages_frame, bg="#181A1F", pady=8)
        typing_frame.pack(fill=tk.X)
        
        # Container for avatar and indicator
        container = tk.Frame(typing_frame, bg="#181A1F")
        container.pack(side=tk.LEFT, anchor=tk.W)
        
        # Avatar
        avatar_container = tk.Frame(container, bg="#181A1F")
        avatar_container.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 10))
        
        # Use logo image if available, otherwise use emoji
        if self.logo_image:
            avatar = tk.Label(avatar_container, image=self.logo_image, bg="#181A1F")
        else:
            avatar = tk.Label(avatar_container, text="👨🏻‍⚖️", font=("Segoe UI", 24), 
                            bg="#181A1F", fg="#0084ff")
        avatar.pack()
        
        # Typing indicator
        indicator_container = tk.Frame(container, bg="#181A1F")
        indicator_container.pack(side=tk.LEFT)
        
        # Add "LegalGuru" label
        sender_label = tk.Label(indicator_container, text="LegalGuru", font=("Segoe UI", 10, "bold"), 
                              bg="#181A1F", fg="#ACACBE")
        sender_label.pack(anchor=tk.W)
        
        # Typing bubble - dark theme
        typing_bubble = tk.Frame(indicator_container, bg="#444654", padx=12, pady=10)
        typing_bubble.pack(anchor=tk.W)
        
        # Dots
        dots_frame = tk.Frame(typing_bubble, bg="#444654")
        dots_frame.pack()
        
        # Create dots
        self.dots = []
        for i in range(3):
            dot = tk.Label(dots_frame, text="•", font=("Segoe UI", 16), bg="#444654", fg="white")
            dot.pack(side=tk.LEFT, padx=2)
            self.dots.append(dot)
        
        # Animate dots
        self.animate_dots(0, typing_frame)
        
        # Scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
        return typing_frame
    
    def animate_dots(self, dot_index, typing_frame):
        if not typing_frame.winfo_exists():
            return
            
        # Reset all dots
        for dot in self.dots:
            if dot.winfo_exists():
                dot.configure(fg="white")
        
        # Highlight current dot
        if self.dots[dot_index].winfo_exists():
            self.dots[dot_index].configure(fg="#b3d9ff")
        
        # Schedule next animation
        next_dot = (dot_index + 1) % len(self.dots)
        typing_frame.after(400, lambda: self.animate_dots(next_dot, typing_frame))
    
    def clear_chat(self):
        # Clear all messages
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        # Clear chat history
        self.chat_history = []
        
        # Clear the JSON file
        with open(self.messages_file, 'w') as f:
            json.dump([], f)
        
        # Add welcome message again
        self.add_message("Hello! I'm LegalGuru. How can I assist you with legal matters today?", "bot")

    def make_image_round(self, image):
        """Create a circular mask for the image"""
        from PIL import Image, ImageTk, ImageDraw
        
        # Convert to PIL Image
        pil_image = Image.open("1.png").resize(
            (image.width(), image.height()),
            Image.LANCZOS
        )
        
        # Create circular mask
        mask = Image.new('L', pil_image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + pil_image.size, fill=255)
        
        # Apply mask and convert back to PhotoImage
        pil_image.putalpha(mask)
        return ImageTk.PhotoImage(pil_image)

if __name__ == "__main__":
    app = ModernUI()
    app.mainloop()
