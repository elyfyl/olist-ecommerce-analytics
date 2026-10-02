import duckdb

def create_fact_table():
    """
    DuckDB kullanarak tabloları birleştirir ve ondalık sayıları 
    Tableau'nun (Türkiye bölge ayarları) okuyabileceği virgüllü formata çevirir.
    """
    print("Veri birleştirme işlemi başlıyor, ondalık ayırıcılar düzeltiliyor...")
    
    con = duckdb.connect(database=':memory:')
    
    query = """
    COPY (
        SELECT 
            o.order_id,
            o.customer_id,
            o.order_status,
            o.order_purchase_timestamp,
            o.order_delivered_customer_date,
            o.order_estimated_delivery_date,
            c.customer_state,
            i.product_id,
            
            -- Sayısal değerlerdeki noktaları virgülle değiştiriyoruz
            REPLACE(CAST(i.price AS VARCHAR), '.', ',') AS price,
            REPLACE(CAST(i.freight_value AS VARCHAR), '.', ',') AS freight_value,
            
            p.product_category_name,
            nlp.review_score,
            nlp.sentiment,
            
            date_diff('day', 
                      CAST(o.order_estimated_delivery_date AS DATE), 
                      CAST(o.order_delivered_customer_date AS DATE)) AS delivery_delay_days
                      
        FROM read_csv_auto('data/olist_orders_dataset.csv') AS o
        LEFT JOIN read_csv_auto('data/olist_customers_dataset.csv') AS c 
            ON o.customer_id = c.customer_id
        LEFT JOIN read_csv_auto('data/olist_order_items_dataset.csv') AS i 
            ON o.order_id = i.order_id
        LEFT JOIN read_csv_auto('data/olist_products_dataset.csv') AS p 
            ON i.product_id = p.product_id
        LEFT JOIN read_csv_auto('data/cleaned_reviews.csv') AS nlp 
            ON o.order_id = nlp.order_id
    ) TO 'data/fact_orders.csv' (HEADER, DELIMITER ',');
    """
    
    try:
        con.execute(query)
        print("Başarılı! fact_orders.csv dosyası virgüllü ondalık formatıyla kaydedildi.")
    except Exception as e:
        print(f"Bir hata oluştu:\n{e}")

if __name__ == "__main__":
    create_fact_table()