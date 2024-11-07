USE zenith_restaurant;

-- item names and the dates when they are offered -- 
SELECT items.item_name, menus.menu_date
FROM menus
JOIN menu_items 
	ON menus.menu_id = menu_items.menu_id
JOIN items 
	ON menu_items.item_id = items.item_id 
GROUP BY items.item_name, menus.menu_date
ORDER BY items.item_name, menus.menu_date;

-- item names and the number of times they were ordered (on a certain date range) --
SELECT items.item_name, COUNT(orders.order_id)
FROM items
JOIN orders 
	ON items.item_id = orders.item_id
JOIN checks
	ON orders.check_id = checks.check_id
JOIN menus
	ON checks.menu_id = menus.menu_id
WHERE items.item_category != 'REQUEST' AND menus.menu_date = '2024-10-13' 
GROUP BY items.item_name 
ORDER BY COUNT(orders.order_id) DESC;