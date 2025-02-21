import streamlit as st
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ✅ MySQL Connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="healthcare_db"
    )


# ✅ Function to Run SQL Queries
def run_query(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    conn.close()
    return result, columns


# ✅ Streamlit UI - Dashboard Title
st.title("📊 Healthcare Insights Dashboard")
st.write("Explore patient admissions, diagnoses, billing, and trends.")

# 🔹 Dropdown Query Selector
query_options = {
    "📋 Sample Data": "SELECT * FROM healthcare_data LIMIT 10;",
    "📈 Monthly Admission Trends": "SELECT DATE_FORMAT(Admit_Date, '%Y-%m') AS Month, COUNT(*) AS Total_Admissions FROM healthcare_data GROUP BY Month ORDER BY Month;",
    "🩺 Top 5 Diagnoses": "SELECT Diagnosis, COUNT(*) AS Frequency FROM healthcare_data GROUP BY Diagnosis ORDER BY Frequency DESC LIMIT 5;",
    "🛏️ Bed Occupancy Analysis": "SELECT Bed_Occupancy, COUNT(*) AS Count FROM healthcare_data GROUP BY Bed_Occupancy;",
    "⏳ Length of Stay Analysis": "SELECT Diagnosis, AVG(DATEDIFF(Discharge_Date, Admit_Date)) AS Avg_Stay FROM healthcare_data GROUP BY Diagnosis ORDER BY Avg_Stay DESC LIMIT 5;",
    "📅 Seasonal Admission Patterns": "SELECT MONTHNAME(Admit_Date) AS Month, COUNT(*) AS Total_Admissions FROM healthcare_data GROUP BY Month;",

    # ✅ Fixed Query: Follow-up vs Non-Follow-up Patients
    "📊 Follow-up vs Non-Follow-up Patients": """ 
        SELECT 'Follow-up' AS Category, COUNT(*) AS Count FROM healthcare_data WHERE Followup_Date != 'No Follow-up Required'
        UNION ALL
        SELECT 'Non-Follow-up', COUNT(*) FROM healthcare_data WHERE Followup_Date = 'No Follow-up Required';
    """,

    "💰 Monthly Revenue Trends": "SELECT DATE_FORMAT(Admit_Date, '%Y-%m') AS Month, SUM(Billing_Amount) AS Total_Revenue FROM healthcare_data GROUP BY Month ORDER BY Month;",
    "🩺 Average Feedback by Doctor": "SELECT Doctor, AVG(Feedback) AS Avg_Feedback FROM healthcare_data GROUP BY Doctor ORDER BY Avg_Feedback DESC;",
    "💰 Diagnoses with Highest Billing": "SELECT Diagnosis, SUM(Billing_Amount) AS Total_Billing FROM healthcare_data GROUP BY Diagnosis ORDER BY Total_Billing DESC LIMIT 5;",
    "📋 Patients Without Follow-ups": "SELECT COUNT(*) FROM healthcare_data WHERE Followup_Date = 'No Follow-up Required';",
    "⏳ Diagnoses with Longest Stay": "SELECT Diagnosis, AVG(DATEDIFF(Discharge_Date, Admit_Date)) AS Avg_Length_Of_Stay FROM healthcare_data GROUP BY Diagnosis ORDER BY Avg_Length_Of_Stay DESC LIMIT 5;",
    "🧪 Most Popular Medical Tests": "SELECT Test, COUNT(*) AS Test_Count FROM healthcare_data GROUP BY Test ORDER BY Test_Count DESC LIMIT 5;",
    "💰 Highest Earning Doctors": "SELECT Doctor, SUM(Billing_Amount) AS Total_Earnings FROM healthcare_data GROUP BY Doctor ORDER BY Total_Earnings DESC LIMIT 5;",
    "📊 Diagnosis Count by Month": "SELECT Diagnosis, MONTHNAME(Admit_Date) AS Month, COUNT(*) AS Count FROM healthcare_data GROUP BY Diagnosis, Month;",
    "📈 Total Revenue by Diagnosis": "SELECT Diagnosis, SUM(Billing_Amount) AS Total_Revenue FROM healthcare_data GROUP BY Diagnosis ORDER BY Total_Revenue DESC;"
}

selected_query_name = st.selectbox("📊 Select a Query to Display", list(query_options.keys()))

# 🔹 Execute and Display the Selected Query
if selected_query_name:
    sql_query = query_options[selected_query_name]
    query_result, column_names = run_query(sql_query)

    if query_result:
        df = pd.DataFrame(query_result, columns=column_names)
        st.write(f"### {selected_query_name}")

        # ✅ Only show the table for "Follow-up vs Non-Follow-up Patients"
        if selected_query_name == "📊 Follow-up vs Non-Follow-up Patients":
            st.write("### Follow-up vs Non-Follow-up Patients Table")
            st.dataframe(df)
        else:
            st.dataframe(df)

            # 🔹 Visualization (Only for other queries)
            if len(df.columns) == 2:
                fig, ax = plt.subplots(figsize=(10, 6))
                if "Month" in df.columns[0] or "Date" in df.columns[0]:
                    sns.lineplot(x=df[df.columns[0]], y=df[df.columns[1]], marker="o", ax=ax)
                    ax.set_xticks(range(len(df[df.columns[0]])))
                    ax.set_xticklabels(df[df.columns[0]], rotation=45, ha='right')
                    ax.set_xlabel(df.columns[0])
                    ax.set_ylabel(df.columns[1])
                elif "Count" in df.columns[1] or "Total" in df.columns[1]:
                    sns.barplot(x=df[df.columns[0]], y=df[df.columns[1]], ax=ax)
                    ax.set_xticklabels(df[df.columns[0]], rotation=45)
                else:
                    ax.pie(df[df.columns[1]], labels=df[df.columns[0]], autopct='%1.1f%%', startangle=90)
                    ax.axis("equal")

                ax.set_title(selected_query_name)
                st.pyplot(fig)
    else:
        st.write("No data available for this query.")
