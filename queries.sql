USE zenith_restaurant;

-- item names and the dates when they are offered -- 
SELECT items.item_name, menus.menu_date
FROM menus
JOIN menu_items 
	ON menus.menu_id = menu_items.menu_id
JOIN items 
	ON menu_items.item_id = items.item_id 
ORDER BY items.item_name;

-- view for simplifying complex queries --
CREATE VIEW items_menus_view AS
SELECT 
	i.*,
    o.order_id,
    c.check_id, 
    m.*
FROM items AS i 
JOIN orders AS o 
	ON i.item_id = o.item_id
JOIN checks AS c
	ON o.check_id = c.check_id
JOIN menus AS m
	ON c.menu_id = m.menu_id;
        
-- item names and the number of times they were ordered (on a certain date range) --
SELECT item_name, COUNT(order_id) as count
FROM items_menus_view
WHERE item_category != 'REQUEST' AND menu_date = '2024-10-13' 
GROUP BY item_name 
ORDER BY count DESC;

-- item categories and the number of time they were ordered (on a certain date range) --
SELECT item_category, COUNT(order_id) as count
FROM items_menus_view
WHERE item_name != "no entree" AND menu_date = '2024-10-13' 
GROUP BY item_category 
ORDER BY count DESC;

