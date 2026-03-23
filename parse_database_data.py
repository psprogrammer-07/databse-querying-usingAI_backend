from collections import defaultdict
import json
from datetime import date
from decimal import Decimal

# Your raw data
raw_data_old = [
    {'TABLE_NAME': 'customers', 'COLUMN_NAME': 'churned', 'DATA_TYPE': 'tinyint'}, 
    {'TABLE_NAME': 'customers', 'COLUMN_NAME': 'customer_id', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'customers', 'COLUMN_NAME': 'customer_name', 'DATA_TYPE': 'varchar'}, 
    {'TABLE_NAME': 'customers', 'COLUMN_NAME': 'email', 'DATA_TYPE': 'varchar'}, 
    {'TABLE_NAME': 'customers', 'COLUMN_NAME': 'region_id', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'customers', 'COLUMN_NAME': 'signup_date', 'DATA_TYPE': 'date'}, 
    {'TABLE_NAME': 'monthly_targets', 'COLUMN_NAME': 'month_year', 'DATA_TYPE': 'varchar'}, 
    {'TABLE_NAME': 'monthly_targets', 'COLUMN_NAME': 'revenue_target', 'DATA_TYPE': 'decimal'}, 
    {'TABLE_NAME': 'monthly_targets', 'COLUMN_NAME': 'target_id', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'products', 'COLUMN_NAME': 'category', 'DATA_TYPE': 'varchar'}, 
    {'TABLE_NAME': 'products', 'COLUMN_NAME': 'price', 'DATA_TYPE': 'decimal'}, 
    {'TABLE_NAME': 'products', 'COLUMN_NAME': 'product_id', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'products', 'COLUMN_NAME': 'product_name', 'DATA_TYPE': 'varchar'}, 
    {'TABLE_NAME': 'regions', 'COLUMN_NAME': 'region_id', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'regions', 'COLUMN_NAME': 'region_name', 'DATA_TYPE': 'varchar'}, 
    {'TABLE_NAME': 'transactions', 'COLUMN_NAME': 'customer_id', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'transactions', 'COLUMN_NAME': 'product_id', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'transactions', 'COLUMN_NAME': 'quantity', 'DATA_TYPE': 'int'}, 
    {'TABLE_NAME': 'transactions', 'COLUMN_NAME': 'total_amount', 'DATA_TYPE': 'decimal'}, 
    {'TABLE_NAME': 'transactions', 'COLUMN_NAME': 'transaction_date', 'DATA_TYPE': 'date'}, 
    {'TABLE_NAME': 'transactions', 'COLUMN_NAME': 'transaction_id', 'DATA_TYPE': 'int'}
]
def parse_database_data(raw_data):
    #print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
    final_table=[]
    # 1. Group the data by Table Name
    schema = defaultdict(list)
    for entry in raw_data:
        table = entry['TABLE_NAME']
        column_info = f"{entry['COLUMN_NAME']} ({entry['DATA_TYPE']})"
        schema[table].append(column_info)


    print(schema)


    for table, columns in schema.items():
        final_table.append(table)

    print("\n final table data: ")
    print(final_table)
    
    return final_table


def format_schema_for_ai(raw_data):
    schema = defaultdict(list)
    for entry in raw_data:
        table = entry['TABLE_NAME']
        column_info = f"{entry['COLUMN_NAME']} ({entry['DATA_TYPE']})"
        schema[table].append(column_info)
    
    schema_str = ""
    for table, columns in schema.items():
        schema_str += f"Table: {table}\nColumns: {', '.join(columns)}\n\n"
        
    return schema_str



def formate_sql_query_data(raw_tuple):
    # Unpack the columns and the list of dictionaries
    columns, rows = raw_tuple
    
    # Process the rows to handle special types (Decimal, Date)
    clean_data = []
    for row in rows:
        clean_row = {}
        for key, value in row.items():
            if isinstance(value, Decimal):
                clean_row[key] = float(value)
            elif isinstance(value, date):
                clean_row[key] = value.isoformat()
            else:
                clean_row[key] = value
        clean_data.append(clean_row)
    
    # Create the final structure
    result = {
        "columns": columns,
        "data": clean_data
    }
    
    return result

# --- Example Usage with your data ---
raw_input = (['customer_id', 'customer_name', 'email', 'region_id', 'signup_date', 'churned'], [{'customer_id': 1, 'customer_name': 'Arun Kumar', 'email': 'arun@email.com', 'region_id': 1, 'signup_date': date(2023, 1, 15), 'churned': 0}])

formatted_output = formate_sql_query_data(raw_input)

# Print as a pretty JSON string
print(json.dumps(formatted_output, indent=2))