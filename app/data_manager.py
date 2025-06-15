# app/data_manager.py

from app.db import get_connection
from mysql.connector import Error, IntegrityError


class DataManager:
    @staticmethod
    def _execute_query(query, params=None, fetch_one=False, commit=False):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if commit:
                conn.commit()

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
    def _execute_update(query, params=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return {"success": True, "affected_rows": cursor.rowcount}
        except IntegrityError as e:
            return {"success": False, "error": str(e)}
        except Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    # Site-related operations
    @staticmethod
    def fetch_all_sites():
        """Return all religious sites ordered by name"""
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
        WHERE site_id = %s AND event_date >= CURDATE()
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
        if limit is not None:
            query += f" LIMIT {limit}"
        return DataManager._execute_query(query, (site_id,))

    @staticmethod
    def fetch_sites_by_religion(religion):
        if religion is None:
            query = "SELECT * FROM sites ORDER BY name"
            return DataManager._execute_query(query)
        query = "SELECT * FROM sites WHERE religion = %s ORDER BY name"
        return DataManager._execute_query(query, (religion,))

    # User-related operations
    @staticmethod
    def get_user_by_id(user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        return DataManager._execute_query(query, (user_id,), fetch_one=True)

    @staticmethod
    def fetch_user(username):
        query = "SELECT * FROM users WHERE username = %s"
        return DataManager._execute_query(query, (username,), fetch_one=True)

    @staticmethod
    def get_user_by_email(email):
        query = "SELECT user_id, username, email FROM users WHERE email = %s"
        return DataManager._execute_query(query, (email,), fetch_one=True)

    @staticmethod
    def validate_user_credentials(username, password_hash):
        query = """
        SELECT user_id, username, role, religion, explore_mode
        FROM users
        WHERE username = %s AND password_hash = %s
        """
        return DataManager._execute_query(query, (username, password_hash), fetch_one=True)

    @staticmethod
    def update_user_address(user_id, new_address):
        """Update only the user's address"""
        query = "UPDATE users SET address = %s WHERE user_id = %s"
        result = DataManager._execute_update(query, (new_address, user_id))
        if result['success'] and result['affected_rows'] == 0:
            return {"success": False, "error": "User not found"}
        return result

    @staticmethod
    def register_user(username, email, password_hash):
        query = """
        INSERT INTO users (username, email, password_hash, role)
        VALUES (%s, %s, %s, 'user')
        """
        try:
            result = DataManager._execute_update(query, (username, email, password_hash))
            if result['success']:
                return {"success": True, "user_id": result.get('lastrowid')}
            return result
        except IntegrityError:
            return {"success": False, "error": "Username or Email already in use"}

    @staticmethod
    def update_password(email, new_password_hash):
        query = "UPDATE users SET password_hash = %s WHERE email = %s"
        result = DataManager._execute_update(query, (new_password_hash, email))
        if result['success'] and result['affected_rows'] == 0:
            return {"success": False, "error": "Email not found"}
        return result

    @staticmethod
    def update_user_details(user_id, address=None, dob_str=None, religion=None):
        """Update user details - any parameter can be None to skip updating that field"""
        updates = []
        params = []

        if address is not None:
            updates.append("address = %s")
            params.append(address)
        if dob_str is not None:
            updates.append("dob = %s")
            params.append(dob_str)
        if religion is not None:
            updates.append("religion = %s")
            params.append(religion)

        if not updates:  # Nothing to update
            return {"success": False, "error": "No fields to update"}

        params.append(user_id)  # Always add user_id at the end for WHERE clause
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"

        result = DataManager._execute_update(query, params)
        if result['success'] and result['affected_rows'] == 0:
            return {"success": False, "error": "User not found"}
        return result

    @staticmethod
    def update_user_religion(user_id, new_religion):
        query = "UPDATE users SET religion = %s WHERE user_id = %s"
        result = DataManager._execute_update(query, (new_religion, user_id))
        if result['success'] and result['affected_rows'] == 0:
            return {"success": False, "error": "User not found"}
        return result

    @staticmethod
    def toggle_explore_mode(user_id, explore_mode):
        query = "UPDATE users SET explore_mode = %s WHERE user_id = %s"
        result = DataManager._execute_update(query, (explore_mode, user_id))
        if result['success'] and result['affected_rows'] == 0:
            return {"success": False, "error": "User not found"}
        return result

    # Feedback and ratings
    @staticmethod
    def submit_rating(user_id, rating):
        query = """
        INSERT INTO ratings (user_id, rating, created_at)
        VALUES (%s, %s, NOW())
        """
        return DataManager._execute_update(query, (user_id, rating))

    @staticmethod
    def submit_feedback(user_id, feedback_text):
        query = """
        INSERT INTO feedback (user_id, feedback_text, created_at)
        VALUES (%s, %s, NOW())
        """
        return DataManager._execute_update(query, (user_id, feedback_text))


# Module-level exports
fetch_all_sites = DataManager.fetch_all_sites
fetch_site_by_id = DataManager.fetch_site_by_id
fetch_events_by_site = DataManager.fetch_events_by_site
fetch_images_by_site = DataManager.fetch_images_by_site
fetch_reviews_by_site = DataManager.fetch_reviews_by_site
fetch_user = DataManager.fetch_user
validate_user_credentials = DataManager.validate_user_credentials
register_user = DataManager.register_user
get_user_by_email = DataManager.get_user_by_email
update_password = DataManager.update_password
update_user_details = DataManager.update_user_details
get_user_by_id = DataManager.get_user_by_id
fetch_sites_by_religion = DataManager.fetch_sites_by_religion
update_user_religion = DataManager.update_user_religion
submit_rating = DataManager.submit_rating
submit_feedback = DataManager.submit_feedback
toggle_explore_mode = DataManager.toggle_explore_mode
update_user_address = DataManager.update_user_address