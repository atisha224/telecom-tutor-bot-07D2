import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def show_performance():

    st.title("📊 Performance Analytics")

    # =========================
    # LOGIN CHECK
    # =========================
    if "user_id" not in st.session_state:
        st.warning("Please login first.")
        return

    user_id = st.session_state.user_id

    # =========================
    # CONNECT DATABASE
    # =========================
    conn = sqlite3.connect("telequiz.db")

    df = pd.read_sql_query(
        """
        SELECT 
            e.score,
            e.timestamp,
            s.topic
        FROM evaluations e
        JOIN questions q ON e.question_id = q.question_id
        JOIN sessions s ON q.session_id = s.session_id
        WHERE s.user_id = ?
        """,
        conn,
        params=(user_id,)
    )

    conn.close()

    # =========================
    # NO DATA CASE
    # =========================
    if df.empty:
        st.info("No quiz attempts yet.")
        return

    # =========================
    # KPI SECTION
    # =========================
    st.subheader("📈 Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Attempts", len(df))
    col2.metric("Average Score", round(df["score"].mean(), 2))
    col3.metric("Highest Score", df["score"].max())
    col4.metric("Lowest Score", df["score"].min())

    # =========================
    # SCORE TREND
    # =========================
    st.subheader("📉 Score Trend Over Time")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_sorted = df.sort_values("timestamp")

    fig1 = plt.figure()
    plt.plot(df_sorted["timestamp"], df_sorted["score"])
    plt.xlabel("Attempt Time")
    plt.ylabel("Score")
    plt.title("Score Trend")
    plt.xticks(rotation=45)

    st.pyplot(fig1)

    # =========================
    # TOPIC PERFORMANCE
    # =========================
    st.subheader("📊 Topic-wise Performance")

    topic_avg = df.groupby("topic")["score"].mean()

    fig2 = plt.figure()
    topic_avg.plot(kind="bar")
    plt.ylabel("Average Score")
    plt.title("Average Score by Topic")

    st.pyplot(fig2)

    # =========================
    # WEAK TOPICS
    # =========================
    st.subheader("⚠ Weak Topics")

    weak_topics = topic_avg[topic_avg < 6]

    if weak_topics.empty:
        st.success("No weak topics detected.")
    else:
        weak_df = weak_topics.reset_index()
        weak_df.columns = ["Topic", "Average Score"]
        st.dataframe(weak_df)