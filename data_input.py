import pymysql.cursors
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
import traceback


def insert_menu(conn, xml_path):
    """
    Insert menu and item data from an XML file into database.
    
    conn: Active MySQL connection object
    xml_path: Path to the XML file containing menu data
    """

    # Parse xml data
    tree = ET.parse(xml_path)
    root = tree.getroot()

    with conn.cursor() as cur:
        # Format menu date
        menu_date = root.get('date')
        menu_date = datetime.strptime(menu_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        # Insert menu record
        menu_insert_sql = "INSERT INTO menus (menu_date) VALUES (%s)" 
        cur.execute(menu_insert_sql, (menu_date,)) 

        # Retrieve menu_id for linking items and menu_items 
        menu_id = cur.lastrowid

        for item in root.findall('item'):
            # Retrieve item details from xml
            name = item.find('name').text.lower() #UNIQUE
            category = item.find('category').text.upper() 
            is_depleted = item.find("depleted") is not None

            # Check for item record by name
            item_id_sql = '''
                SELECT item_id 
                FROM items
                WHERE item_name = %s 
                LIMIT 1
            '''
            cur.execute(item_id_sql, (name,))

            item_id_query = cur.fetchone()
            if not item_id_query:
                # Insert item record if not found
                item_insert_sql = '''
                    INSERT INTO items (item_name, item_category, item_price) 
                    VALUES (%s, %s, %s) 
                '''
                cur.execute(item_insert_sql, (name, category, 12.00))
                item_id = cur.lastrowid
            else: 
                item_id  =  item_id_query[0]

            # Link menu to item 
            menu_item_insert_sql = '''
                INSERT INTO menu_items (item_id, menu_id, is_depleted) 
                VALUES (%s, %s, %s) 
            '''
            cur.execute(menu_item_insert_sql, (item_id, menu_id, is_depleted))
    conn.commit()

def insert_checks(conn, xml_path):
    """
    Insert check and item data from an XML file into database.
    
    conn: Active MySQL connection object
    xml_path: Path to the XML file containing check data
    """

    # Parse xml data
    tree = ET.parse(xml_path)
    root = tree.getroot()

    with conn.cursor() as cur:
        # Format menu date
        menu_date = root.get('date')
        menu_date = datetime.strptime(menu_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        
        # Require menu exists
        menu_id_sql = '''
            SELECT menu_id 
            FROM menus
            WHERE menu_date = %s 
            LIMIT 1
        '''
        cur.execute(menu_id_sql, menu_date) 
        menu_id = cur.fetchone()[0] 

        for chk in root.findall('chk'):
            # Retrieve server name and table number if provided
            server_tag = chk.find('server')
            table_tag = chk.find('table')
            server_name = server_tag.text.upper() if server_tag is not None else None
            table_id = int(table_tag.text) if table_tag is not None else None

            # Insert check record
            check_insert_sql = '''
                INSERT INTO checks (menu_id, table_id, server_name) 
                VALUES (%s, %s, %s)
            '''
            cur.execute(check_insert_sql, (menu_id, table_id, server_name))
            check_id = cur.lastrowid

            # Retrieve every order in check
            for ord in chk.findall('ord'):
                # Get quantity and item name of order 
                qty = int(ord.get('qty', default=1))
                item_name = ord.text.lower()

                # Retrieve item_id record by name
                item_id_sql = '''
                    SELECT item_id
                    FROM items
                    WHERE item_name = %s
                    LIMIT 1
                '''
                cur.execute(item_id_sql, item_name)

                item_id_query = cur.fetchone()
                if item_id_query is not None:
                    item_id = item_id_query[0] 
                else: 
                    # Assume item category REQUEST; insert by default values
                    cur.execute("INSERT INTO items (item_name) VALUES (%s)", (item_name,))
                    item_id = cur.lastrowid
                
                # Insert order record using item_id and repeat qty-many times  
                order_insert_sql = '''
                    INSERT INTO orders (item_id, check_id)
                    VALUES (%s, %s)
                '''
                for _ in range(qty):
                    cur.execute(order_insert_sql, (item_id, check_id))
    conn.commit()


def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument('menu_xml', type=str)
    parser.add_argument('checks_xml', type=str) 
    args = parser.parse_args() 

    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='password321',
            database='zenith_restaurant'
        )   

        insert_menu(conn, args.menu_xml)
        insert_checks(conn, args.checks_xml)
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())
    finally:
        conn.close()

if __name__ == '__main__':
    main()
