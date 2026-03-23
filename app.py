from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from config import DB_CONFIG
import json

from parse_database_data import parse_database_data, formate_sql_query_data, format_schema_for_ai
from ai_services import generate_sql, generate_insight, generate_kpi_response

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

def get_schema_raw_data():
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    SELECT DISTINCT table_name as TABLE_NAME ,column_name as COLUMN_NAME, data_type as DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema = %s
    ORDER BY table_name;
    """

    cursor.execute(query, (DB_CONFIG["database"],))
    result = cursor.fetchall()

    cursor.close()
    connection.close()
    return result

def execute_query(sql):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(sql)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    connection.close()

    return columns, result

@app.route("/api/tables", methods=["GET"])
def get_tables():
    try:
        raw_data = get_schema_raw_data()
        result_f = parse_database_data(raw_data)

        return jsonify({
            "status": "success",
            "tables": result_f
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/generate_query", methods=["POST"])
def generate_query_endpoint():
    try:
        data = request.get_json()
        user_query = data.get("query")
        
        if not user_query:
             return jsonify({"status": "error", "message": "Query is required"}), 400

        # 1. Get Schema
        raw_schema = get_schema_raw_data()
        schema_text = format_schema_for_ai(raw_schema)

        # 2. Generate SQL
        ai_response_str = generate_sql(schema_text, user_query)
        
        try:
            ai_response = json.loads(ai_response_str)
        except json.JSONDecodeError:
             return jsonify({"status": "error", "message": "Failed to parse AI response", "raw": ai_response_str}), 500

        sql_query = ai_response.get("sql")
        chart_type = ai_response.get("chart_type", "bar")
        insight = ai_response.get("insight", "")
        x_key = ai_response.get("xKey", "")
        y_key = ai_response.get("yKey", "")

        if not sql_query:
            return jsonify({"status": "error", "message": "AI did not return a SQL query"}), 500

        # 3. Execute SQL
        columns, query_result = execute_query(sql_query)
        
        # 4. Format Data
        formatted_data = formate_sql_query_data((columns, query_result))
        
        response_data = {
            "sql": sql_query,
            "columns": formatted_data["columns"],
            "data": formatted_data["data"],
            "insight": insight,
            "chart_type": chart_type,
            "xKey": x_key,
            "yKey": y_key
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/generate_kpi", methods=["POST"])
def generate_kpi_endpoint():
    try:
        data = request.get_json()
        user_query = data.get("query")
        
        if not user_query:
            return jsonify({"status": "error", "message": "Query is required"}), 400

        # 1. Get Schema
        raw_schema = get_schema_raw_data()
        schema_text = format_schema_for_ai(raw_schema)

        # 2. Get KPI structure from AI
        ai_response_str = generate_kpi_response(schema_text, user_query)
        
        try:
            ai_response = json.loads(ai_response_str)
        except json.JSONDecodeError:
            return jsonify({"status": "error", "message": "Failed to parse AI response", "raw": ai_response_str}), 500
            
        kpis = ai_response.get("kpis", [])
        insight = ai_response.get("insight", "")
        
        # 3. Execute SQL for each KPI to get the value
        final_kpis = []
        for kpi in kpis:
            sql = kpi.get("sql")
            label = kpi.get("label")
            trend = kpi.get("trend")
            
            if sql:
                try:
                    # We expect a single value
                    _, result = execute_query(sql)
                    if result and len(result) > 0:
                        # Get the first value of the first row
                        first_row = result[0]
                        value = next(iter(first_row.values()))
                    else:
                        value = "N/A"
                except Exception as e:
                    print(f"Error executing KPI SQL: {sql} - {e}")
                    value = "Error"
            else:
                value = "N/A"
                
            final_kpis.append({
                "label": label,
                "value": str(value),
                "trend": trend
            })
            
        return jsonify({
            "mode": "kpi",
            "kpis": final_kpis,
            "insight": insight
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
