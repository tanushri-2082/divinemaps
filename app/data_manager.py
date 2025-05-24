# app/data_manager.py
from .db import get_connection

def fetch_all_sites():
    """Return a list of all religious sites."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sites")
    sites = cursor.fetchall()
    conn.close()
    return sites

def fetch_site_by_id(site_id):
    """Return details for a single site."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sites WHERE site_id = %s", (site_id,))
    site = cursor.fetchone()
    conn.close()
    return site

def fetch_events_by_site(site_id):
    """Return all events for a given site."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events WHERE site_id = %s", (site_id,))
    events = cursor.fetchall()
    conn.close()
    return events

def fetch_images_by_site(site_id):
    """Return all image records for a given site."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM images WHERE site_id = %s", (site_id,))
    images = cursor.fetchall()
    conn.close()
    return images

def fetch_reviews_by_site(site_id):
    """Return all reviews for a given site."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT r.*, u.username FROM reviews r "
                   "JOIN users u ON r.user_id = u.user_id "
                   "WHERE r.site_id = %s", (site_id,))
    reviews = cursor.fetchall()
    conn.close()
    return reviews

def fetch_user(username):
    """Return user record by username (for login/auth)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user
