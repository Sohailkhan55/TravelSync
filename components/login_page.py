import streamlit as st
import os
import time
from src.auth import (
    start_manual_registration, finalize_manual_registration, 
    login_manual, hash_password, finalize_google_user, google_login_flow
)



def render_login_page():
    st.title("🔐 Sign In to TravelSync")
    
    # Toggle between modes
    auth_mode = st.radio("Select Mode", ["Login", "Create Account"], horizontal=True)
    
    st.divider()

    if auth_mode == "Login":
        col1, col2 = st.columns(2)
        
        # --- Option A: Google Login ---
        with col1:
            st.subheader("Google Login")
            
            # Check for Auth Code in URL
            query_params = st.query_params
            auth_code = query_params.get("code")

            if auth_code:
                with st.spinner("Authenticating with Google..."):
                    try:
                        from google_auth_oauthlib.flow import Flow
                        
                        redirect_uri_env = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501").strip()
                        
                        client_config = {
                            "web": {
                                "client_id": os.getenv("GOOGLE_CLIENT_ID").strip(),
                                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET").strip(),
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": [redirect_uri_env]
                            }
                        }
                        
                        flow = Flow.from_client_config(
                            client_config,
                            scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
                            redirect_uri=redirect_uri_env
                        )
                        
                        flow.fetch_token(code=auth_code)
                        credentials = flow.credentials
                        
                        # Get User Info
                        import requests
                        user_info_service = requests.get(
                            "https://www.googleapis.com/oauth2/v1/userinfo",
                            params={"alt": "json"},
                            headers={"Authorization": f"Bearer {credentials.token}"}
                        )
                        google_user_data = user_info_service.json()
                        
                        # Store in temp session
                        st.session_state["google_temp"] = {
                            "email": google_user_data.get("email"),
                            "name": google_user_data.get("name"),
                            "picture": google_user_data.get("picture")
                        }
                        
                        # Clear URL code
                        st.query_params.clear()
                        
                    except Exception as e:
                        st.error(f"Authentication Failed: {e}")
                        st.caption("Ensure your Redirect URI in Google Console matches your Streamlit URL.")

            # Logic to Display Login Button or Handle Success
            
            if "google_temp" in st.session_state:
                g_user = st.session_state["google_temp"]
                
                # Check DB
                res = google_login_flow(g_user['email'], g_user['name'], g_user['picture'])
                
                if not res['is_new']:
                    # Existing user -> Login
                    st.session_state["user_phone"] = res['user']['phone_number']
                    st.session_state["user_name"] = res['user']['full_name']
                    st.success(f"Welcome back, {res['user']['full_name']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    # New User -> Prompt for Phone
                    st.info(f"✨ Welcome {g_user['name']}! Please complete your profile.")
                    st.caption(f"Authenticated as: {g_user['email']}")
                    
                    with st.form("google_completion"):
                        st.markdown("**Enter Mobile Number**")
                        c_a, c_b = st.columns([1, 4])
                        with c_a:
                            st.text_input("Prefix", value="+91", disabled=True, key="p_prefix_g")
                        with c_b:
                            phone_digits = st.text_input("Number", max_chars=10, key="p_input_g", placeholder="9999900000")
                            
                        submitted = st.form_submit_button("Complete Registration")
                        if submitted:
                            if len(phone_digits) != 10 or not phone_digits.isdigit():
                                st.error("Please enter a valid 10-digit mobile number.")
                            else:
                                final_phone = f"+91{phone_digits}"
                                reg_res = finalize_google_user(g_user['email'], g_user['name'], g_user['picture'], final_phone)
                                if reg_res["success"]:
                                    st.session_state["user_phone"] = reg_res["phone"]
                                    st.session_state["user_name"] = g_user["name"]
                                    st.success("Profile Created!")
                                    st.rerun()
                                else:
                                    st.error(reg_res["error"])
                                
            else:
                # Show Login Button (Generate URL)
                if os.getenv("GOOGLE_CLIENT_ID"):
                    try:
                        from google_auth_oauthlib.flow import Flow
                        redirect_uri_env = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501").strip()
                        client_config = {
                            "web": {
                                "client_id": os.getenv("GOOGLE_CLIENT_ID").strip(),
                                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET").strip(),
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": [redirect_uri_env]
                            }
                        }
                        flow = Flow.from_client_config(
                            client_config,
                            scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
                            redirect_uri=redirect_uri_env
                        )
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        
                        # Use Streamlit's native link button which handles target logic better
                        st.link_button(
                            "🌐 Sign in with Google", 
                            url=auth_url,
                            use_container_width=True,
                            type="secondary"
                        )
                        
                    except Exception as e:
                        st.error(f"Config Error: {e}")
                else:
                    st.error("Missing GOOGLE_CLIENT_ID in .env")

        # --- Option B: Manual Login ---
        with col2:
            st.subheader("Manual Login")
            with st.form("manual_login"):
                email_or_phone = st.text_input("Email or Phone")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    res = login_manual(email_or_phone, password)
                    if res["success"]:
                        st.session_state["user_phone"] = res["user"]["phone_number"]
                        st.session_state["user_name"] = res["user"]["full_name"]
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error(res["error"])

    elif auth_mode == "Create Account":
        st.subheader("📝 Create New Account")
        with st.form("signup_form"):
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email Address")
            new_pass = st.text_input("Password", type="password")
            
            st.markdown("**Mobile Number**")
            c_a, c_b = st.columns([1, 4])
            with c_a:
                st.text_input("Prefix", value="+91", disabled=True, key="p_prefix_m")
            with c_b:
                new_phone_digits = st.text_input("Number", max_chars=10, key="p_input_m", placeholder="9999900000")
            
            submitted = st.form_submit_button("Send OTP")
            
            if submitted:
                if not (new_name and new_email and new_phone_digits and new_pass):
                    st.error("All fields are required.")
                elif len(new_phone_digits) != 10 or not new_phone_digits.isdigit():
                    st.error("Please enter a valid 10-digit mobile number.")
                else:
                    full_phone = f"+91{new_phone_digits}"
                    res = start_manual_registration(new_name, new_email, full_phone, new_pass)
                    if res["success"]:
                        st.session_state["signup_data"] = {
                            "name": new_name, "email": new_email, 
                            "phone": res["formatted_phone"], 
                            "pass_hash": hash_password(new_pass),
                            "otp": res["otp"]
                        }
                        st.toast("OTP Generated Successfully!", icon="📩")
                    else:
                        st.error(res["error"])
        
        # OTP verification Step
        if "signup_data" in st.session_state:
            otp_code = st.session_state["signup_data"]["otp"]
            st.success(f"**DEV MODE:** Your simulated OTP is: `{otp_code}`")
            otp_input = st.text_input("Enter OTP", key="signup_otp")
            if st.button("Verify & Create Account"):
                data = st.session_state["signup_data"]
                if otp_input == data["otp"]:
                    fin_res = finalize_manual_registration(data["name"], data["email"], data["phone"], data["pass_hash"])
                    if fin_res["success"]:
                       st.session_state["user_phone"] = fin_res["phone"]
                       st.session_state["user_name"] = fin_res["name"]
                       st.success("Account Created Successfully!")
                       st.rerun()
                    else:
                       st.error(fin_res["error"])
                else:
                    st.error("Invalid OTP")
