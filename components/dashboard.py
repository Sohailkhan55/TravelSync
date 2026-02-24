import streamlit as st
from streamlit_autorefresh import st_autorefresh
import json
from agents.insider import LocalInsiderAgent
from agents.chatbot import LocalChatbotAgent
from database.db_manager import (
    get_itinerary, get_group, update_item_status, 
    get_user_groups, search_users, add_group_member, get_group_members,
    send_chat_message, fetch_chat_messages, get_group_insider_data, update_group_insider_data
)

def render_dashboard(user_phone):
    """
    Renders the dashboard for an authenticated user.
    """
    st.title("👤 My Dashboard")
    
    # 1. Sidebar: My List of Groups
    my_groups = get_user_groups(user_phone)
    group_options = {g['group_name']: g['group_id'] for g in my_groups}
    
    selected_group_name = st.selectbox("Select Trip", options=list(group_options.keys()))
    
    if not selected_group_name:
        st.info("You don't have any trips yet. Go to 'Plan a Trip' to create one!")
        return

    group_id = group_options[selected_group_name]
    group = get_group(group_id)

    st.divider()
    
    # 2. Main Dashboard Area
    st.header(f"🌴 {group['group_name']}")
    
    # Determine user name for chat
    current_user_name = "User"
    all_members = get_group_members(group_id)
    for m in all_members:
        if m['phone_number'] == user_phone:
            current_user_name = m['full_name']
            break

    tab_itinerary, tab_chat, tab_discover, tab_memories, tab_members = st.tabs([
        "📅 Itinerary", "💬 Lounge", "✨ Discover", "📸 Memories", "👥 Team"
    ])

    # --- TAB 1: Itinerary ---
    with tab_itinerary:
        items = get_itinerary(group_id)
        if not items:
            st.info("No items in itinerary yet.")
        else:
            total = len(items)
            visited = sum(1 for i in items if i['status'] == 'Visited')
            progress = visited / total if total > 0 else 0
            st.progress(progress, text=f"Progress: {visited}/{total}")
            
            for item in items:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                     is_done = item['status'] == 'Visited'
                     checked = st.checkbox(
                        f"**{item['place_name']}** ({item['category'].title()})", 
                        value=is_done,
                        key=f"item_{item['id']}"
                    )
                     if checked != is_done:
                        new_status = "Visited" if checked else "Pending"
                        update_item_status(item['id'], new_status)
                        st.rerun()

    # --- TAB 2: Chat Lounge ---
    with tab_chat:
        st.header("Chat Room")
        
        # Auto-Refresh mechanism (poll every 5 seconds)
        # Only run if NOT currently fetching insider data to prevent interruption
        if not st.session_state.get('fetching_insider'):
             count = st_autorefresh(interval=5000, limit=None, key="chatrefresh")
        
        # Fetch Messages
        messages = fetch_chat_messages(group_id)
        
        # Display Messages container
        chat_container = st.container(height=450)
        with chat_container:
            if not messages:
                st.info("No messages yet. Start the conversation!")
            
            for msg in messages:
                is_me = (msg['sender_phone'] == user_phone)
                is_ai = (msg['sender_phone'] == "+0000000000")
                
                # Styles
                if is_me:
                    align = "margin-left: auto; text-align: right;"
                    bg_color = "#E0F7FA" # Cyan (Me)
                    border_radius = "15px 15px 0px 15px"
                    
                    # Name Display (Me)
                    sender_display = f"<b>You</b> <span style='font-size:0.9em; font-weight:bold; color:#555;'>({msg['sender_phone']})</span>"
                    name_align = "text-align: right;"
                elif is_ai:
                    align = "margin-right: auto; text-align: left;"
                    bg_color = "#F3E5F5" # Purple (AI)
                    border_radius = "15px 15px 15px 0px"
                    
                    # Name Display (AI)
                    sender_display = f"<b>{msg['sender_name']}</b> <span style='font-size:0.9em; font-weight:bold; color:#8E24AA;'>(AI Assistant)</span>"
                    name_align = "text-align: left;"
                else:
                    align = "margin-right: auto; text-align: left;"
                    bg_color = "#FFF3E0" # Orange (Others)
                    border_radius = "15px 15px 15px 0px"
                    
                    # Name Display (Others)
                    sender_display = f"<b>{msg['sender_name']}</b> <span style='font-size:0.9em; font-weight:bold; color:#555;'>({msg['sender_phone']})</span>"
                    name_align = "text-align: left;"
                
                # Reply Block HTML
                reply_html = ""
                if msg['reply_to_id']:
                    reply_html = f"""<div style="background-color: rgba(0,0,0,0.05); border-left: 4px solid #888; padding: 5px; margin-bottom: 5px; border-radius: 4px; font-size: 0.8rem; color: #444; text-align: left;"><b>{msg['reply_sender'] or 'Unknown'}</b><br>{msg['reply_content'] or 'Deleted Message'}</div>"""

                # Format Mention Style for @TravelAI
                formatted_content = msg["message_content"].replace(
                    "@TravelAI", 
                    "<span style='font-weight:bold; color:#1976D2; background-color:rgba(25, 118, 210, 0.1); padding:0px 4px; border-radius:4px;'>@TravelAI</span>"
                )

                # HTML Bubble
                chat_bubble_html = (
                    f'<div style="background-color: {bg_color}; padding: 10px 15px; border-radius: {border_radius}; '
                    f'max_width: 75%; width: fit-content; margin-bottom: 5px; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); {align}">'
                    f'<div style="font-size: 0.75rem; color: #444; margin-bottom: 4px; {name_align}">{sender_display}</div>'
                    f'{reply_html}'
                    f'<div style="font-size: 1rem; color: #222; word-wrap: break-word;">{formatted_content}</div>'
                    f'<div style="font-size: 0.6rem; color: #888; text-align: right; margin-top: 5px;">{msg["timestamp"]}</div>'
                    f'</div>'
                )
                st.markdown(chat_bubble_html, unsafe_allow_html=True)
                
                # Reply Button
                if is_me:
                    c1, c2, c3 = st.columns([1, 8, 1])
                    with c3:
                        if st.button("↩️", key=f"rep_{msg['message_id']}", help="Reply to this message"):
                            st.session_state["reply_context"] = {
                                "id": msg['message_id'],
                                "sender": "You" if is_me else msg['sender_name'],
                                "text": msg['message_content']
                            }
                            st.rerun()
                else:
                    c1, c2, c3 = st.columns([1, 8, 1])
                    with c1:
                         if st.button("↩️", key=f"rep_{msg['message_id']}", help="Reply to this message"):
                            st.session_state["reply_context"] = {
                                "id": msg['message_id'],
                                "sender": msg['sender_name'],
                                "text": msg['message_content']
                            }
                            st.rerun()


        # Quick Actions & Emojis
        with st.expander("😀 Quick Reactions & Emojis", expanded=False):
            st.caption("Tip: Press `Windows + .` (Windows) or `Ctrl + Cmd + Space` (Mac) to open the full system emoji keyboard inside the text bar.")
            
            # Quick Send Buttons
            st.write("**Send a Quick Reaction:**")
            cols = st.columns(8)
            emojis = ["👍", "❤️", "😂", "🎉", "✈️", "🍔", "📸", "🚍"]
            for i, emo in enumerate(emojis):
                with cols[i]:
                    if st.button(emo, key=f"emo_{i}"):
                        reply_id = st.session_state.get("reply_context", {}).get("id")
                        send_chat_message(group_id, user_phone, current_user_name, emo, reply_to_id=reply_id)
                        # Clear reply context after sending
                        if "reply_context" in st.session_state:
                             del st.session_state["reply_context"]
                        st.rerun()

        # Reply Context Banner
        if "reply_context" in st.session_state:
            ctx = st.session_state["reply_context"]
            st.info(f"↩️ Replying to **{ctx['sender']}**: \"{ctx['text'][:30]}...\"")
            if st.button("Cancel Reply"):
                del st.session_state["reply_context"]
                st.rerun()

        # Input Area (Fixed at bottom by st.chat_input)
        if prompt := st.chat_input("Type a message..."):
            reply_id = st.session_state.get("reply_context", {}).get("id")
            send_chat_message(group_id, user_phone, current_user_name, prompt, reply_to_id=reply_id)
            # Clear reply context
            if "reply_context" in st.session_state:
                del st.session_state["reply_context"]
                
            # Check for AI Trigger
            if "@TravelAI" in prompt:
                with st.spinner("TravelAI is typing..."):
                    agent = LocalChatbotAgent()
                    
                    # group is currently an sqlite3.Row, which doesn't support .get()
                    dest = group['destination'] if group['destination'] else group['group_name'].replace(' Trip', '')
                    
                    response = agent.handle_chat_query(prompt, dest)
                    # Save AI Response
                    send_chat_message(group_id, "+0000000000", "TravelAI 🤖", response, reply_to_id=None)
                    
            st.rerun()

    # --- TAB 3: Discover (Insider) ---
    with tab_discover:
        st.header(f"✨ Discover {group['destination'] or 'Local Gems'}")
        
        # Check DB for Insider Data
        insider_json = get_group_insider_data(group_id)
        
        if not insider_json:
            st.info("🕵️ Contacting our local insider agent to fetch the best secrets for you...")
            
            if st.button("Unlock Local Insights"):
                st.session_state['fetching_insider'] = True
                st.rerun()
                
            if st.session_state.get('fetching_insider'):
                agent = LocalInsiderAgent()
                target_city = group['destination'] if group['destination'] else group['group_name'].replace(" Trip", "")
                
                with st.status("🕵️ Insider Agent Working... (Chat Refresh Paused)", expanded=True) as status:
                    st.write("🍛 Scouting authentic food and restaurants...")
                    food = agent.fetch_food_intel(target_city)
                    
                    st.write("🛍️ Finding best souvenirs and markets...")
                    shop = agent.fetch_shopping_intel(target_city)
                    
                    st.write("💡 Gathering local hacks and culture tips...")
                    hacks = agent.fetch_hacks_intel(target_city)
                    
                    data = {
                        "food": food,
                        "shopping": shop,
                        "hacks": hacks
                    }
                    
                    update_group_insider_data(group_id, json.dumps(data))
                    status.update(label="✅ Insights Unlocked!", state="complete", expanded=False)
                
                # Turn off fetching flag and refresh to show data
                st.session_state['fetching_insider'] = False
                st.rerun()
        else:
            try:
                data = json.loads(insider_json)
                
                # Magazine Layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🍛 Taste of the City")
                    st.success(data.get('food', 'No food info.'))
                    
                with col2:
                    st.subheader("🛍️ Shopper's Guide")
                    st.warning(data.get('shopping', 'No shopping info.'))
                
                st.divider()
                st.subheader("💡 Local Hacks & Culture")
                st.info(data.get('hacks', 'No hacks found.'))
                
                if st.button("Refresh Insights"):
                    update_group_insider_data(group_id, None) # Clear to force re-fetch
                    st.rerun()

            except json.JSONDecodeError:
                st.error("Data error. Please refresh insights.")
                if st.button("Reset Data"):
                     update_group_insider_data(group_id, None)
                     st.rerun()

    # --- TAB 4: Memories ---
    with tab_memories:
        st.subheader("📸 Shared Gallery")
        
        import random
        
        # Styles for Polaroid Effect
        st.markdown("""
        <style>
        .polaroid {
            width: 100%;
            border: 10px solid white;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            border-radius: 2px;
            margin-bottom: 20px;
            transition: all 0.3s ease-in-out;
            cursor: pointer;
        }
        
        .hover-rot-right:hover { transform: scale(1.05) rotate(3deg); z-index: 10; }
        .hover-rot-left:hover { transform: scale(1.05) rotate(-3deg); z-index: 10; }
        .hover-zoom:hover { transform: scale(1.1); z-index: 10; }
        .hover-float:hover { transform: translateY(-10px) scale(1.02); z-index: 10; }
        </style>
        """, unsafe_allow_html=True)

        # Mock Photos (Random Travel/Friends)
        photos = [
            "https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=500&h=500&fit=crop", # Friends
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500&h=500&fit=crop", # Beach
            "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?w=500&h=500&fit=crop", # Hiking
            "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=500&h=500&fit=crop", # Switzerland
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&h=500&fit=crop", # Food
            "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=500&h=500&fit=crop", # Venice
            "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=500&h=500&fit=crop", # Santorini
            "https://images.unsplash.com/photo-1506012787146-f92b2d7d6d96?w=500&h=500&fit=crop", # Adventure
        ]

        # Gallery Layout (3 Columns)
        st.write("Relive the best moments from your trip!")
        cols = st.columns(3)
        effects = ["hover-rot-right", "hover-rot-left", "hover-zoom", "hover-float"]
        
        for i, url in enumerate(photos):
            effect = random.choice(effects)
            with cols[i % 3]:
                st.markdown(f"""
                    <img src="{url}" class="polaroid {effect}" title="Memory #{i+1}">
                    <div style="text-align: center; font-size: 0.8em; color: #555; margin-top: 5px;">Memory #{i+1}</div>
                """, unsafe_allow_html=True)
        
        st.caption("✨ Pro Tip: Interactions are now randomized!")

    # --- TAB 5: Members ---
    with tab_members:
        # Show current members
        members = get_group_members(group_id)
        st.subheader("Group Members")
        for mem in members:
            st.text(f"👤 {mem['full_name']} ({mem['phone_number']})")
        
        st.divider()
        
        # Add Friend Section
        st.subheader("➕ Add User to Group")
        st.caption("ℹ️ For phone search, please explicitly add the code (e.g., +919999900000).")
        search_query = st.text_input("Search by Email or Phone", placeholder="e.g. friend@gmail.com")
        
        if search_query:
            # Smart Search Logic
            results = search_users(search_query)
            if not results and search_query.isdigit() and len(search_query) == 10:
                # Try adding +91 automatically
                results = search_users(f"+91{search_query}")
                
            if results:
                for u in results:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"**{u['full_name']}**")
                        c1.caption(f"Phone: {u['phone_number']}")
                        
                        if any(m['phone_number'] == u['phone_number'] for m in members):
                            c2.success("Already Added")
                        else:
                            if c2.button("Add", key=f"add_{u['phone_number']}"):
                                if add_group_member(group_id, u['phone_number']):
                                    st.success(f"Added {u['full_name']}!")
                                    st.rerun()
                                else:
                                    st.warning("Failed to add.")
            else:
                st.warning("No users found. Ask them to sign up first!")
