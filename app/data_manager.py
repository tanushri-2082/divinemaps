# app/data_manager.py

from app.db import get_connection
from mysql.connector import Error


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
        """Return a list of all religious sites (ordered by name)."""
        query = "SELECT * FROM sites ORDER BY name"
        return DataManager._execute_query(query)

    @staticmethod
    def fetch_site_by_id(site_id):
        """Return details for a single site (by site_id)."""
        query = "SELECT * FROM sites WHERE site_id = %s"
        return DataManager._execute_query(query, (site_id,), fetch_one=True)

    @staticmethod
    def fetch_events_by_site(site_id):
        """
        Return all upcoming events for a given site.
        (Only those with event_date >= current date, ordered chronologically.)
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
        """Return all reviews for a given site, optionally limited."""
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
        """Return a user record by username (for login/auth)."""
        query = "SELECT * FROM users WHERE username = %s"
        return DataManager._execute_query(query, (username,), fetch_one=True)

    @staticmethod
    def validate_user_credentials(username, password):
        """
        Validate user credentials and return user data (user_id, username)
        if the username/password combination is correct. Otherwise return None.
        """
        query = """
        SELECT user_id, username
        FROM users
        WHERE username = %s
          AND password = %s
        """
        return DataManager._execute_query(query, (username, password), fetch_one=True)


# Expose the methods as module‐level functions
fetch_all_sites = DataManager.fetch_all_sites
fetch_site_by_id = DataManager.fetch_site_by_id
fetch_events_by_site = DataManager.fetch_events_by_site
fetch_images_by_site = DataManager.fetch_images_by_site
fetch_reviews_by_site = DataManager.fetch_reviews_by_site
fetch_user = DataManager.fetch_user
validate_user_credentials = DataManager.validate_user_credentials
