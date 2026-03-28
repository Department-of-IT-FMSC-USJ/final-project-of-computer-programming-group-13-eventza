import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

# --- MYSQL DATABASE SETUP ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",      
        password="",      
        database="event_hub"
    )

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), role VARCHAR(50), type VARCHAR(100))')
    c.execute('CREATE TABLE IF NOT EXISTS posts (id INT AUTO_INCREMENT PRIMARY KEY, author VARCHAR(255), content TEXT, image_url TEXT, date VARCHAR(100))')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INT AUTO_INCREMENT PRIMARY KEY, sender VARCHAR(255), receiver VARCHAR(255), msg TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS planner_offers (offer_id INT AUTO_INCREMENT PRIMARY KEY, planner_name VARCHAR(255), service_type VARCHAR(100), discount_val VARCHAR(50), offer_details TEXT, expiry_date VARCHAR(100))')
    conn.commit()
    c.close()
    conn.close()

init_db()

# --- CUSTOM STYLING ---
def apply_styles(show_bg=False):
    bg_style = ""
    if show_bg:
        # Background for all pages except Home
        bg_url = "https://th.bing.com/th/id/R.b04280ed7a7ebcf673e27f2228fccaaa?rik=L8DpGha%2fgsbadQ&riu=http%3a%2f%2flivesonlovestreet.com%2fwp-content%2fuploads%2f2019%2f03%2fvogue-ballroom-burwood-wedding-photography-59.jpg&ehk=05Na3lJflHUonSN%2bbTkTgzXgGmSaovKDpB3zywIeNAA%3d&risl=&pid=ImgRaw&r=0"
        bg_style = f"""
        .stApp {{
            background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("{bg_url}");
            background-size: cover;
            background-attachment: fixed;
        }}
        """

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap');
        
        {bg_style}

        html, body, [class*="st-"] {{
            font-family: 'Inter', sans-serif;
        }}

        /* Hero Section */
        .hero-section {{
            padding: 120px 20px;
            text-align: center;
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                        url('https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=2069&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            border-radius: 30px;
            color: white;
            margin-bottom: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }}
        .hero-title {{ 
            font-size: 6rem; 
            font-weight: 800; 
            margin-bottom: 0px; 
            letter-spacing: -3px; 
            text-transform: uppercase;
        }}
        .hero-subtitle {{ 
            font-size: 1.6rem; 
            font-weight: 300; 
            margin-bottom: 30px; 
            opacity: 0.9;
            letter-spacing: 2px;
        }}

        /* Buttons */
        .stButton>button {{
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        /* Sidebar and Inputs */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.9);
        }}

        /* Chat Bubbles */
        .chat-container {{
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }}
        .sent {{ background-color: #E3F2FD; text-align: right; border-left: 5px solid #2196F3; }}
        .received {{ background-color: #F5F5F5; text-align: left; border-right: 5px solid #9E9E9E; }}
        </style>
    """, unsafe_allow_html=True)

# --- AUTHENTICATION COMPONENTS ---
def sign_up_ui():
    st.subheader("✨ Create your EVENTZA account")
    
    st.info("""
    **💳 Payment Details for Registration:**
    * **Acc No:** 9689 5689 1002
    * **Name:** B D H Jayaweera
    * **Bank:** People's Bank - Nugegoda
    * **WhatsApp No:** 0759864564
    * **Registration Fee:** Rs.2500
    * **Monthly Payment:** Rs.1000
            
    * Only **EVENT PLANNERS** should pay registration & monthly fees
            
    ⚠️ *Please send your payment receipt via WhatsApp within 24 hours. Otherwise, your registration will be canceled.*
    """)

    col1, col2 = st.columns(2)
    with col1:
        new_user = st.text_input("Username", placeholder="Create a unique username")
        new_pass = st.text_input("Password", type='password', placeholder="Minimum 8 characters")
    with col2:
        role = st.selectbox("I am a:", ["Customer", "Event Planner"])
        planner_type = "N/A"
        if role == "Event Planner":
            planner_type = st.selectbox("Specialization:", ["Hotel", "Salon", "DJ Artist", "Photographer"])
    
    if st.button("Complete Registration", use_container_width=True):
        if new_user and new_pass:
            conn = get_db_connection()
            c = conn.cursor()
            try:
                query = 'INSERT INTO users (username, password, role, type) VALUES (%s, %s, %s, %s)'
                c.execute(query, (new_user, new_pass, role, planner_type))
                conn.commit()
                st.success("✅ Account created! Please log in above.")
            except mysql.connector.Error:
                st.error("❌ Username already exists.")
            finally:
                c.close()
                conn.close()

# --- APP PAGES ---
def planner_dashboard(username):
    st.title(f"Planner Dashboard: {username}")
    st.header("1. Quick Social Post")
    with st.form("post_form", clear_on_submit=True):
        content = st.text_area("Enter offers & details")
        img_url = st.text_input("Image URL (from Unsplash or similar)")
        if st.form_submit_button("Post to Feed"):
            conn = get_db_connection()
            c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute('INSERT INTO posts (author, content, image_url, date) VALUES (%s, %s, %s, %s)', (username, content, img_url, now))
            conn.commit()
            c.close()
            conn.close()
            st.rerun()

    st.divider()
    st.header("2. Manage Your Posts")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, content, date FROM posts WHERE author = %s ORDER BY id DESC', (username,))
    my_posts = c.fetchall()
    
    if not my_posts:
        st.info("You haven't published any posts yet.")
    else:
        for p in my_posts:
            with st.container(border=True):
                st.write(f"**Date:** {p[2]}")
                st.write(p[1])
                if st.button(f"🗑️ Delete Post", key=f"del_dash_{p[0]}"):
                    c.execute('DELETE FROM posts WHERE id = %s', (p[0],))
                    conn.commit()
                    st.success("Post deleted successfully!")
                    st.rerun()
    c.close()
    conn.close()

    st.divider()
    st.header("3. Official Offer (Bot-Searchable)")
    with st.form("offer_form", clear_on_submit=True):
        s_type = st.selectbox("Service Category", ["Photography", "Music/DJ", "Venue/Hotel", "Beauty/Salon"])
        d_val = st.text_input("Discount Value (e.g. 15% OFF)")
        o_details = st.text_area("Describe the deal")
        e_date = st.date_input("Offer Expiry")
        if st.form_submit_button("Launch Official Offer"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('INSERT INTO planner_offers (planner_name, service_type, discount_val, offer_details, expiry_date) VALUES (%s, %s, %s, %s, %s)', 
                      (username, s_type, d_val, o_details, str(e_date)))
            conn.commit()
            c.close()
            conn.close()
            st.success("The Trend Bot has been updated with your offer!")

def customer_feed():
    st.title("Top Event Professionals")
    
    search_q = st.text_input("🔍 Search posts or planners...", placeholder="Try 'wedding', 'discount', or a name...")
    categories = ["All", "DJ Artist", "Photographer", "Salon", "Hotel"]
    selected_cat = st.pills("Filter by Category:", categories, selection_mode="single", default="All")
    st.write("") 

    conn = get_db_connection()
    c = conn.cursor()
    
    base_query = "SELECT posts.id, posts.author, posts.content, posts.image_url, posts.date, users.type FROM posts JOIN users ON posts.author = users.username WHERE 1=1"
    params = []

    if selected_cat != "All":
        base_query += " AND users.type = %s"
        params.append(selected_cat)
    
    if search_q:
        base_query += " AND (posts.content LIKE %s OR posts.author LIKE %s)"
        search_val = f"%{search_q}%"
        params.extend([search_val, search_val])

    base_query += " ORDER BY posts.id DESC"
    c.execute(base_query, tuple(params))
    posts = c.fetchall()
    
    if not posts:
        st.info("No matching results found.")
    
    for p in posts:
        post_id, author, content, img, date, p_type = p
        with st.container(border=True):
            st.markdown(f"**✨ {author}** | `{p_type}`")
            if img: 
                st.image(img, width=450) 
            
            edit_key = f"edit_mode_{post_id}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            if st.session_state[edit_key]:
                new_content = st.text_area("Edit Content", value=content, key=f"area_{post_id}")
                col_save, col_cancel = st.columns(2)
                if col_save.button("Save Changes", key=f"save_{post_id}"):
                    c.execute("UPDATE posts SET content = %s WHERE id = %s", (new_content, post_id))
                    conn.commit()
                    st.session_state[edit_key] = False
                    st.rerun()
                if col_cancel.button("Cancel", key=f"cancel_{post_id}"):
                    st.session_state[edit_key] = False
                    st.rerun()
            else:
                st.write(content)

            if st.session_state['role'] == "Event Planner" and st.session_state['user'] == author:
                col1, col2 = st.columns([1, 4])
                if col1.button("📝 Edit", key=f"btn_edit_{post_id}"):
                    st.session_state[edit_key] = True
                    st.rerun()
                if col2.button("🗑️ Delete", key=f"btn_del_feed_{post_id}"):
                    c.execute('DELETE FROM posts WHERE id = %s', (post_id,))
                    conn.commit()
                    st.rerun()
            elif st.session_state['role'] == "Customer":
                if st.button(f"Inquire with {author}", key=f"btn_inq_{post_id}"):
                    st.session_state['chat_with'] = author
                    st.info(f"Navigate to 'Messages' to talk to {author}")
                    
    c.close()
    conn.close()

def messaging_system(username):
    st.title("📬 Inbox")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT DISTINCT username FROM users WHERE username != %s', (username,))
    all_users = [row[0] for row in c.fetchall()]
    
    if not all_users:
        st.info("No other users found in the network yet.")
        return

    receiver = st.selectbox("Select contact:", all_users, index=all_users.index(st.session_state.get('chat_with', all_users[0])) if st.session_state.get('chat_with') in all_users else 0)

    st.subheader(f"Chat with {receiver}")
    c.execute('''SELECT sender, msg, timestamp FROM messages 
                 WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s) 
                 ORDER BY timestamp ASC''', (username, receiver, receiver, username))
    chat_history = c.fetchall()

    with st.container(height=400, border=True):
        if not chat_history:
            st.write("No messages yet. Say hi!")
        else:
            for sender, message, time in chat_history:
                is_me = sender == username
                div_class = "sent" if is_me else "received"
                st.markdown(f"""
                    <div class="chat-container {div_class}">
                        <b>{'You' if is_me else sender}</b><br>{message}
                    </div>
                """, unsafe_allow_html=True)

    with st.form("send_msg", clear_on_submit=True):
        new_msg = st.text_input("Type your message...")
        if st.form_submit_button("Send"):
            if new_msg:
                c.execute('INSERT INTO messages (sender, receiver, msg) VALUES (%s, %s, %s)', (username, receiver, new_msg))
                conn.commit()
                st.rerun()
    
    c.close()
    conn.close()

def trend_chatbot():
    st.title("🤖 EVENTZA Smart Assistant")
    user_q = st.chat_input("Ask about trends, search posts, or say hello...")
    
    if user_q:
        with st.chat_message("assistant"):
            query = user_q.lower()
            conn = get_db_connection()
            c = conn.cursor()

            greetings = ["hello", "hi", "hey", "hola", "greetings"]
            if any(greet in query for greet in greetings):
                st.write("Hello! I'm your EVENTZA Assistant. How can I help you discover great events or planners today?")

            if "trend" in query:
                st.subheader("📅 2026 Industry Forecast")
                if "dj" in query or "music" in query:
                    st.write("2026 DJs are 'performers' using AI-enhanced stems for real-time mashups.")
                elif "photo" in query:
                    st.write("Visuals focus on 'Vibe' over perfection—using cinematic grain and intentional motion blur.")
                elif "venue" in query or "hotel" in query:
                    st.write("Hotels are becoming 'Experience Hubs' with wellness suites ('Hushpitality') and AI virtual concierges.")
                else:
                    st.write("Trends focus on 'Quiet Luxury', sustainable beauty, and deep tech integration.")
            
            if any(x in query for x in ["suggest", "discount", "deal", "offer"]):
                st.subheader("🏷️ Current Planner Deals")
                c.execute("SELECT planner_name, service_type, discount_val, offer_details FROM planner_offers")
                offers = c.fetchall()
                if offers:
                    for off in offers:
                        st.info(f"**{off[0]}** ({off[1]}): **{off[2]}**\n\n{off[3]}")
                else:
                    st.write("No active deals found at this moment.")

            st.subheader("📸 Direct Results from the Network")
            search_val = f"%{query}%"
            c.execute("SELECT author, content, date FROM posts WHERE content LIKE %s OR author LIKE %s", (search_val, search_val))
            related_posts = c.fetchall()
            
            if related_posts:
                st.write(f"I found {len(related_posts)} post(s) matching your request:")
                for post in related_posts:
                    with st.expander(f"Update from {post[0]} ({post[2]})"):
                        st.write(post[1])
            elif "trend" not in query and not any(greet in query for greet in greetings) and "offer" not in query:
                st.write("I couldn't find any specific posts related to your request. Try being more specific!")

            c.close()
            conn.close()

def main():
    st.set_page_config(page_title="EVENTZA | Premium Event Network", layout="wide", page_icon="✨")
    
    if 'logged_in' not in st.session_state: 
        st.session_state['logged_in'] = False

    # Logic to show background: Not Logged in + Show Auth OR Logged In
    should_show_bg = st.session_state['logged_in'] or st.session_state.get('show_auth', False)
    apply_styles(show_bg=should_show_bg)
    
    if not st.session_state['logged_in']:
        if not st.session_state.get('show_auth'):
            st.markdown("""
                <div class="hero-section">
                    <h1 class="hero-title">EVENTZA</h1>
                    <p class="hero-subtitle">WHERE VISIONARY PLANNERS MEET EXTRAORDINARY CLIENTS</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### 📸 Visual Discovery\nExplore a curated feed of the most beautiful events happening right now.")
            with col2:
                st.markdown("### 🤖 2026 Trend Bot\nGet exclusive insights into the future of music, beauty, and venue technology.")
            with col3:
                st.markdown("### 🤝 Direct Access\nConnect directly with photographers, DJs, and hotels with no middleman.")
            
            st.write("")
            if st.button("GO → GET STARTED NOW", use_container_width=True, type="primary"):
                st.session_state['show_auth'] = True
                st.rerun()
        else:
            st.markdown("<h2 style='text-align: center; color: black;'>Welcome to the Network</h2>", unsafe_allow_html=True)
            tab_login, tab_signup = st.tabs(["🔑 Login Eventza", "✨ Register Eventza"])
            
            with tab_login:
                col_l, col_r = st.columns([1, 1])
                with col_l:
                    u = st.text_input("Username")
                    p = st.text_input("Password", type='password')
                    if st.button("Log In"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute('SELECT * FROM users WHERE username=%s AND password=%s', (u, p))
                        data = c.fetchone()
                        if data:
                            st.session_state.update({'logged_in': True, 'user': u, 'role': data[2]})
                            st.rerun()
                        else: st.error("Access denied.")
                        c.close()
                        conn.close()
                with col_r:
                    st.info("Log in to access your personalized feed, messages, and the Trend Bot.")

            with tab_signup:
                sign_up_ui()
            
            if st.button("← Back to Home"):
                st.session_state['show_auth'] = False
                st.rerun()
    else:
        st.sidebar.markdown(f"### Welcome back, <br><span style='color:#FF4B4B;'>{st.session_state['user']}</span>", unsafe_allow_html=True)
        st.sidebar.write(f"Role: {st.session_state['role']}")
        
        menu_options = ["Feed", "Messages", "Trend Bot"]
        if st.session_state['role'] == "Event Planner":
            menu_options.insert(0, "Dashboard")
            
        page = st.sidebar.radio("» Navigate", menu_options)
        
        if st.sidebar.button("Log Out"):
            st.session_state['logged_in'] = False
            st.rerun()
        
        if page == "Dashboard": planner_dashboard(st.session_state['user'])
        elif page == "Feed": customer_feed()
        elif page == "Messages": messaging_system(st.session_state['user'])
        elif page == "Trend Bot": trend_chatbot()

if __name__ == '__main__':
    main()