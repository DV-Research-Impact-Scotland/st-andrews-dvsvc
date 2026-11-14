import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
PORT = os.environ["DB_PORT"]



def connect() -> psycopg2.extensions.connection:

    print("Connecting to PostgreSQL database with: %s".format(locals()))
    try:
        with psycopg2.connect(
            host=DB_HOST,
            port=PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        ) as conn:
            print("Connected to PostgreSQL database")
            return conn
    except psycopg2.DatabaseError as error:
        print("Failed to connect to PostgreSQL database: %s".format(error))

""" Selects charities with locations (appears multiple for multiple locations), 
that are within euclidean distance of given location and distance. 
    ordered by distance to location
"""
def get_locations(lat: float, long: float, distance: int):
    if lat is None and long is None:
        print(f"Error: No coordinates for location: {location}")
        return []
    else:
        conn = connect()
        out = []
        try:
            with conn.cursor() as cursor:
                cursor.execute("""

                                
                                SELECT * from (
                                   SELECT distinct charity.charity_id, charity.name, location.name, charity.url, charity.summary, (ST_Distance(ST_SetSRID(ST_MakePoint(%s, %s), 4326), ST_SetSRID(ST_MakePoint((cast (location.longitude as double precision)), (cast (location.latitude as double precision))), 4326), true)) as distance, location.latitude, location.longitude
                                    FROM location
                                    INNER JOIN service_location using (location_id)
                                    INNER JOIN service using (service_id)
                                    INNER JOIN charity using (charity_id)
                                ) temp
                                 WHERE distance < %s
                                 ORDER BY distance ASC
                                """, (long, lat, distance*1000))
                out =  cursor.fetchall()
                conn.commit()

            conn.close()
            return out
        except Exception as e:
            print(f"Error: {e}")

""" Selects all charities with locations (appears multiple for multiple locations), 
"""
def get_all_locations():
    
    conn = connect()
    out = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                            SELECT distinct charity.charity_id, charity.name, location.name, location.latitude, location.longitude, charity.url, charity.summary
                            FROM location
                            INNER JOIN service_location using (location_id)
                            INNER JOIN service using (service_id)
                            INNER JOIN charity using (charity_id)
                            
                            """,)
            out =  cursor.fetchall()
            conn.commit()

        conn.close()
        return out
    except Exception as e:
        print(f"Error: {e}")

def get_all_charities():
    conn = connect()
    out = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                            SELECT distinct charity.charity_id, charity.name, charity.url, charity.summary
                            FROM charity
                            ORDER BY charity.name;
                            """)
            out =  cursor.fetchall()
            conn.commit()

        conn.close()
        return out
    except Exception as e:
        print(f"Error: {e}")

""" Gets all service ids under a charity"""
def get_services_by_charity_id(id: int):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT service_id, description
                FROM service
                WHERE charity_id = %s

            """,
            (id,)
        )

        out = cursor.fetchall()
        conn.commit()
    conn.close()
    return out

""" Gets all emails for a service"""
def get_emails_by_service(service_id:int):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT email
                FROM email
                WHERE service_id = %s

            """,
            (service_id,)
        )

        out = cursor.fetchall()
        conn.commit()
    conn.close()
    return out

""" Gets all phone nums for a service"""
def get_phone_num_by_service(service_id:int):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT phone_number
                FROM phone_num
                WHERE service_id = %s

            """,
            (service_id,)
        )

        out = cursor.fetchall()
        conn.commit()
    conn.close()
    return out

""" Gets all locations for a service"""
def get_location_by_service(service_id:int):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT name
                FROM service 
                INNER JOIN service_location USING (service_id)
                INNER JOIN location USING (location_id)
                where service_id = %s

            """,
            (service_id,)
        )

        out = cursor.fetchall()
        conn.commit()
    conn.close()
    return out

""" Collates all service info required for a charity"""
def get_all_service_info_by_charity_id(id: int):
    service_list = get_services_by_charity_id(id)
    out = []
    for s in service_list:
        phone = get_phone_num_by_service(s[0])
        email = get_emails_by_service(s[0])
        locs = get_location_by_service(s[0])
        full = list(s)
        phone = [p[0] for p in phone]
        email = [e[0] for e in email]
        locs = [l[0] for l in locs]
        full.append(phone)
        full.append(email)
        full.append(locs)
        out.append(full)
    return out

""" Gets info just about charity"""
def get_charity_info_by_id(id: str):
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute(
            """
                SELECT charity.url, charity.summary, charity_num.charity_number, charity.name
                FROM charity 
                LEFT OUTER JOIN charity_num ON charity.charity_id = charity_num.charity_id
                WHERE charity.charity_id = %s

            """,
            (id,)
        )

        out = cursor.fetchall()
        conn.commit()
    conn.close()
    return out
    
if __name__ == "__main__":
    print(get_all_service_info_by_charity_id(17))
    #print(get_charity_info_by_id(0))
    #print("dist")
    #print(get_locations("London", 1000))
