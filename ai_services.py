from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_sql(schema_text, user_question):
    prompt = f"""
You are a MySQL expert.

Database Schema:
{schema_text}

Rules:
- Only generate SELECT queries.
- Do NOT use INSERT, UPDATE, DELETE, DROP.
- Use only existing tables and columns.
- Add LIMIT 500 if no limit exists.
- available charts: "bar" | "line" | "pie" | "stacked-bar" | "multi-line"
- Return "{{ sql:"sql query", chart_type:"chart type",xKey:"x-axis key",yKey:"y-axis key", insight:"insight(should be non technical)"}}".

User Question:
{user_question}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    text = response.text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
    # Remove "json" language identifier if present
    if text.startswith("json"):
        text = text[4:].strip()
        
    print("Aiiiiiiiii responce:   ", text)
    return text


def generate_kpi_response(schema_text, user_question):
    prompt = f"""
You are a MySQL expert.
Database Schema:
{schema_text}

User Question: {user_question}

Task: Generate Key Performance Indicators (KPIs) based on the question.
Rules:
- Return a JSON object with this structure:
{{
  "kpis": [
    {{
      "label": "Name of KPI",
      "sql": "Single SQL query to fetch the value (e.g. SELECT formatted_value...)",
      "trend": "up" | "down" | "neutral" (Infer this if possible, or set to neutral)
    }}
  ],
  "insight": "Brief business insight explaining the metrics."
}}
- The SQL should return a SINGLE row and SINGLE column.
- Format numbers in the SQL if possible (e.g. '1.2M', '$500').
- Ensure queries are compatible with `ONLY_FULL_GROUP_BY`. Wrap non-aggregated columns in MAX() or similar.
- Do NOT use Markdown formatting in the response.
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    
    text = response.text.strip()
    # Clean up markdown
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
    if text.startswith("json"):
        text = text[4:].strip()
        
    return text


def generate_insight(user_question, data):
    prompt = f"""
User question: {user_question}

Query Result:
{data}

Generate a short professional business insight (2-3 sentences).
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )

    return response.text.strip()
