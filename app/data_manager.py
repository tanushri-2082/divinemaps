# app/data_manager.py

from app.db import get_connection
from mysql.connector import Error, IntegrityError


class DataManager:
    @staticmethod
    def _execute_query(query, params=None, fetch_one=False):
        """
        Helper method to execute SQL queries with proper connection handling.
        Returns either a single row dict (if fetch_one=True) or a list of dicts.
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

            return result

        except Error as e:
            print(f"Database error: {e}")
            return None

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def fetch_all_sites():
        query = "SELECT * FROM sites ORDER BY name"
        return DataManager._execute_query(query)

    @staticmethod
    def fetch_site_by_id(site_id):
        query = "SELECT * FROM sites WHERE site_id = %s"
        return DataManager._execute_query(query, (site_id,), fetch_one=True)

    @staticmethod
    def fetch_events_by_site(site_id):
        query = """
        SELECT * FROM events
        WHERE site_id = %s
          AND event_date >= CURDATE()
        ORDER BY event_date
        """
        return DataManager._execute_query(query, (site_id,))

    @staticmethod
    def fetch_images_by_site(site_id):
        query = "SELECT * FROM images WHERE site_id = %s ORDER BY is_primary DESC, image_id"
        return DataManager._execute_query(query, (site_id,))

    @staticmethod
    def fetch_reviews_by_site(site_id, limit=None):
        query = """
        SELECT r.*, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.site_id = %s
        ORDER BY r.created_at DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        return DataManager._execute_query(query, (site_id,))

    @staticmethod
    def fetch_user(username):
        query = "SELECT * FROM users WHERE username = %s"
        return DataManager._execute_query(query, (username,), fetch_one=True)

    @staticmethod
    def validate_user_credentials(username, password):
        """
        If you are still storing a plain password (not hashed),
        this method would be:
          SELECT user_id, username FROM users
            WHERE username=%s AND password_hash=%s
        However, if you’re hashing with SHA-256, you’d compare
        against the hash. In any case, adapt as needed.
        """
        query = """
        SELECT user_id, username, role
        FROM users
        WHERE username = %s AND password_hash = %s
        """
        return DataManager._execute_query(query, (username, password), fetch_one=True)

    @staticmethod
    def register_user(username, email, password_hash):
        """
        Insert a new row into users(username, email, password_hash, role).
        We default role='user'. Return a dict:
          { 'success': True, 'user_id': <new_id> }
          or { 'success': False, 'error': <error_msg> }
        """
        insert_query = """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (%s, %s, %s, 'user')
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(insert_query, (username, email, password_hash))
            conn.commit()
            new_id = cursor.lastrowid
            return {"success": True, "user_id": new_id}

        except IntegrityError as ie:
            # Typically a duplicate‐username or duplicate‐email situation (UNIQUE constraint)
            # We don’t expose raw SQL errors to the user; instead, return a friendly message:
            return {"success": False, "error": "Username or Email already in use."}

        except Error as e:
            return {"success": False, "error": str(e)}

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()


# Expose the module‐level functions:
fetch_all_sites = DataManager.fetch_all_sites
fetch_site_by_id = DataManager.fetch_site_by_id
fetch_events_by_site = DataManager.fetch_events_by_site
fetch_images_by_site = DataManager.fetch_images_by_site
fetch_reviews_by_site = DataManager.fetch_reviews_by_site
fetch_user = DataManager.fetch_user
validate_user_credentials = DataManager.validate_user_credentials
register_user = DataManager.register_user
