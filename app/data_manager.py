# app/data_manager.py

from app.db import get_connection
from mysql.connector import Error, IntegrityError

class DataManager:
    @staticmethod
    def _execute_query(query, params=None, fetch_one=False):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
        except Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def fetch_all_sites():
        """Return a list of all religious sites (ordered by name)."""
        query = "SELECT * FROM sites ORDER BY name"
        return DataManager._execute_query(query)

    @staticmethod
    def fetch_site_by_id(site_id):
        """Return details for a single site (lookup by site_id)."""
        query = "SELECT * FROM sites WHERE site_id = %s"
        return DataManager._execute_query(query, (site_id,), fetch_one=True)

    @staticmethod
    def fetch_events_by_site(site_id):
        """
        Return upcoming events for a given site (event_date >= today),
        ordered chronologically.
        """
        query = """
        SELECT * FROM events
        WHERE site_id = %s
          AND event_date >= CURDATE()
        ORDER BY event_date
        """
        return DataManager._execute_query(query, (site_id,))

    @staticmethod
    def fetch_images_by_site(site_id):
        """Return all image records for a given site (primary images first)."""
        query = "SELECT * FROM images WHERE site_id = %s ORDER BY is_primary DESC, image_id"
        return DataManager._execute_query(query, (site_id,))

    @staticmethod
    def fetch_reviews_by_site(site_id, limit=None):
        """Return all reviews for a given site, optionally limited in number."""
        query = """
        SELECT r.*, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.site_id = %s
        ORDER BY r.created_at DESC
        """
        if limit is not None:
            query += f" LIMIT {limit}"
        return DataManager._execute_query(query, (site_id,))

    @staticmethod
    def fetch_user(username):
        """Return a user record by username (as a dict), or None if not found."""
        query = "SELECT * FROM users WHERE username = %s"
        return DataManager._execute_query(query, (username,), fetch_one=True)

    @staticmethod
    def validate_user_credentials(username, password_hash):
        """
        Validate user credentials. If you store hashed passwords, pass the hash.
        Returns {user_id, username, role} if credentials match, else None.
        """
        query = """
        SELECT user_id, username, role
        FROM users
        WHERE username = %s
          AND password_hash = %s
        """
        return DataManager._execute_query(query, (username, password_hash), fetch_one=True)

    @staticmethod
    def register_user(username, email, password_hash):
        """
        Insert a new user row into users(username, email, password_hash, role='user').
        On success: return {"success": True, "user_id": <new_id>}.
        On failure (e.g. duplicate username/email): return {"success": False, "error": <message>}.
        """
        insert_query = """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, 'user')
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(insert_query, (username, email, password_hash))
            conn.commit()
            return {"success": True, "user_id": cursor.lastrowid}
        except IntegrityError:
            return {"success": False, "error": "Username or Email already in use."}
        except Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def get_user_by_email(email):
        """
        Return a single user row (as a dict) if that email is registered.
        Otherwise returns None.
        """
        query = "SELECT user_id, username, email FROM users WHERE email = %s"
        return DataManager._execute_query(query, (email,), fetch_one=True)

    @staticmethod
    def update_password(email, new_password_hash):
        """
        Update the password_hash for the user with the given email.
        Returns {"success": True} if exactly one row was updated,
                or {"success": False, "error": <message>} otherwise.
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            update_query = "UPDATE users SET password_hash = %s WHERE email = %s"
            cursor.execute(update_query, (new_password_hash, email))
            conn.commit()
            if cursor.rowcount == 0:
                return {"success": False, "error": "Email not found."}
            return {"success": True}
        except Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def update_user_details(user_id, address, dob_str, religion):
        """
        Update address, dob, religion for given user_id.
        Expects `dob_str` in 'YYYY-MM-DD' format.
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                UPDATE users
                SET address = %s, dob = %s, religion = %s
                WHERE user_id = %s
            """
            cursor.execute(query, (address, dob_str, religion, user_id))
            conn.commit()
            if cursor.rowcount == 1:
                return {"success": True}
            else:
                return {"success": False, "error": "No row updated"}
        except Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


# Expose module‐level functions
fetch_all_sites          = DataManager.fetch_all_sites
fetch_site_by_id         = DataManager.fetch_site_by_id
fetch_events_by_site     = DataManager.fetch_events_by_site
fetch_images_by_site     = DataManager.fetch_images_by_site
fetch_reviews_by_site    = DataManager.fetch_reviews_by_site
fetch_user               = DataManager.fetch_user
validate_user_credentials = DataManager.validate_user_credentials
register_user            = DataManager.register_user
get_user_by_email        = DataManager.get_user_by_email
update_password          = DataManager.update_password
update_user_details      = DataManager.update_user_details