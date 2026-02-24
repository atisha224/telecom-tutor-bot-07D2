import streamlit as st
from datetime import datetime
from backend.database import (
    init_db,
    create_session,
    end_session,
    store_question,
    store_evaluation,
    update_performance
)
from backend.rag_pipeline import RAGPipeline
from backend.pdf_utils import extract_text_from_pdf, chunk_text


def show_quiz():

    st.title("📘 Telecomm Tutor Bot")

    # ==============================
    # INIT DATABASE
    # ==============================
    init_db()

    # ==============================
    # LOGIN PROTECTION
    # ==============================
    if "user_id" not in st.session_state:
        st.warning("Please login first.")
        return

    # ==============================
    # INITIALIZE RAG
    # ==============================
    if "rag" not in st.session_state:
        st.session_state.rag = RAGPipeline()

    # ==============================
    # SESSION MEMORY
    # ==============================
    if "session_memory" not in st.session_state:
        st.session_state.session_memory = {
            "score": 0,
            "attempts": 0,
            "weak_topics": [],
            "history": []
        }

    # ==============================
    # STEP 1 — Upload Document
    # ==============================
    st.subheader("1️⃣ Upload Telecom PDF")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file:
        with st.spinner("Processing document..."):
            text = extract_text_from_pdf(uploaded_file)

            if not text.strip():
                st.error("Could not extract text from PDF.")
            else:
                chunks = chunk_text(text)
                st.session_state.rag.create_embeddings(chunks)
                st.success("Document processed successfully!")
                st.session_state.doc_ready = True

    # ==============================
    # STEP 2 — Generate Question
    # ==============================
    if st.session_state.get("doc_ready"):

        st.subheader("2️⃣ Generate Question")

        topic = st.text_input("Enter Topic (Example: FUP, Roaming, Billing)")

        if st.button("Generate Question"):

            question, context = st.session_state.rag.generate_question(topic)

            if "session_id" not in st.session_state:
                st.session_state.session_id = create_session(
                    st.session_state.user_id,
                    topic
                )

            question_id = store_question(
                st.session_state.session_id,
                question
            )

            st.session_state.question_id = question_id
            st.session_state.question = question
            st.session_state.context = context
            st.session_state.current_topic = topic

            st.markdown("### 📝 Question")
            st.write(question)

    # ==============================
    # STEP 3 — Submit Answer
    # ==============================
    if "question" in st.session_state:

        st.subheader("3️⃣ Submit Your Answer")

        answer = st.text_area("Your Answer")

        if st.button("Submit Answer"):

            result = st.session_state.rag.evaluate_answer(
                st.session_state.context,
                st.session_state.question,
                answer
            )

            # Update memory
            st.session_state.session_memory["attempts"] += 1
            st.session_state.session_memory["score"] += result["score"]

            if result["score"] < 6:
                st.session_state.session_memory["weak_topics"].append(
                    result["weak_concept"]
                )

            st.session_state.session_memory["history"].append({
                "topic": st.session_state.current_topic,
                "score": result["score"],
                "time": datetime.now()
            })

            # Store in DB
            store_evaluation(
                st.session_state.question_id,
                answer,
                result
            )

            update_performance(
                st.session_state.user_id,
                result["weak_concept"],
                result["score"]
            )

            # Display result
            st.markdown("### 📊 Evaluation Result")
            st.write("Score:", result["score"])
            st.write("Correctness:", result["correctness"])
            st.write("Weak Concept:", result["weak_concept"])
            st.write("Explanation:")
            st.write(result["explanation"])

            # Adaptive follow-up
            if result["score"] < 6:
                st.warning("Adaptive Reinforcement Activated")

                adaptive_question, adaptive_context = (
                    st.session_state.rag.generate_adaptive_question(
                        result["weak_concept"]
                    )
                )

                st.session_state.question = adaptive_question
                st.session_state.context = adaptive_context
                st.session_state.current_topic = result["weak_concept"]

                st.markdown("### 🔁 Adaptive Follow-Up Question")
                st.write(adaptive_question)

    # ==============================
    # SESSION SUMMARY
    # ==============================
    if st.session_state.session_memory["attempts"] > 0:

        st.subheader("📈 Current Session Summary")

        avg_score = (
            st.session_state.session_memory["score"] /
            st.session_state.session_memory["attempts"]
        )

        st.write("Total Attempts:",
                 st.session_state.session_memory["attempts"])
        st.write("Average Score:", round(avg_score, 2))
        st.write("Weak Concepts Identified:",
                 list(set(st.session_state.session_memory["weak_topics"])))

    # ==============================
    # END SESSION
    # ==============================
    if "session_id" in st.session_state:
        if st.button("End Session"):
            end_session(st.session_state.session_id)
            st.success("Session Ended")
            del st.session_state.session_id