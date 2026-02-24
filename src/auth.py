import os
import phonenumbers
import bcrypt
import streamlit as st
import random
from database.db_manager import (
    create_google_user, create_manual_user, 
    get_user_by_email, get_user_by_phone
)

def validate_indian_phone(number_str):
    """Validates if the number is a valid Indian phone number. Returns formatted E.164 number or None."""
    try:
        x = phonenumbers.parse(number_str, "IN")
        if not phonenumbers.is_valid_number(x):
            return None
        return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None

def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') # decode converts raw data into text string format we can save in DB

def check_password(password, hashed):
    """Verifies a password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# --- Manual Auth Flow ---

def start_manual_registration(name, email, phone_raw, password):
    """
    Step 1: Validate inputs and check for existence.
    Returns: {"success": bool, "error": str, "otp": str}
    """
    formatted_phone = validate_indian_phone(phone_raw)
    if not formatted_phone:
        return {"success": False, "error": "Invalid Indian phone number."}
    
    if get_user_by_email(email):
        return {"success": False, "error": "Email already exists."}
    if get_user_by_phone(formatted_phone):
        return {"success": False, "error": "Phone number already exists."}
        
    # Generate OTP
    otp = str(random.randint(100000, 999999))
    print(f"SIMULATED SMS OTP: {otp}") # Console output as requested
    
    return {"success": True, "otp": otp, "formatted_phone": formatted_phone}

def finalize_manual_registration(name, email, formatted_phone, password_hash):
    """Step 2: Create DB Record."""
    success = create_manual_user(formatted_phone, email, name, password_hash)
    if success:
        return {"success": True, "phone": formatted_phone, "name": name}
    else:
        return {"success": False, "error": "Database error."}

def login_manual(email_or_phone, password):
    """
    Handles login for manually registered users.
    Accepts Email OR Phone.
    """
    user = None
    if "@" in email_or_phone:
        user = get_user_by_email(email_or_phone)
    else:
        # Check if valid phone format, otherwise try as-is
        p = validate_indian_phone(email_or_phone)
        if p:
             user = get_user_by_phone(p)
        else:
             # Try raw just in case
             user = get_user_by_phone(email_or_phone)
             
    if not user:
        return {"success": False, "error": "User not found."}
        
    if not user['password_hash']:
        return {"success": False, "error": "Please login with Google."}
        
    if check_password(password, user['password_hash']):
        return {"success": True, "user": user}
    else:
        return {"success": False, "error": "Invalid credentials."}

# --- Google Auth Flow ---

def google_login_flow(email, name, photo_url):
    """
    Called after successful Google Auth to link/check user.
    """
    user = get_user_by_email(email)
    
    if user:
        return {"success": True, "user": user, "is_new": False}
    else:
        # New user -> Needs phone number
        return {"success": True, "user": {"email": email, "full_name": name, "profile_pic_url": photo_url}, "is_new": True}

def finalize_google_user(email, name, photo_url, phone_raw):
    """Links Google info with a Phone number."""
    formatted_phone = validate_indian_phone(phone_raw)
    
    print(f"DEBUG: Finalizing User - Email: {email}, Phone: {phone_raw} -> {formatted_phone}")
    
    if not formatted_phone:
        return {"success": False, "error": f"Invalid phone number: {phone_raw}. Must be an Indian number (+91)."}
        
    if get_user_by_phone(formatted_phone):
        return {"success": False, "error": "Phone number already linked to another account."}
        
    success = create_google_user(formatted_phone, email, name, photo_url)
    
    if success:
        print("DEBUG: DB Insert Success")
        return {"success": True, "phone": formatted_phone}
    else:
        print("DEBUG: DB Insert Failed")
        return {"success": False, "error": "Database error: Failed to create user. Email or Phone might be duplicate."}
