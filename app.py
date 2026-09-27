import os, json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
st.set_page_config(page_title="FeedbackIQ", page_icon="🧠", layout="wide")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
API_KEY = os.getenv("GEMINI_API_KEY")

SCHEMA = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["Positive","Neutral","Negative","Mixed"]},
        "category": {"type": "string"},
        "topic": {"type": "string"},
        "product_area": {"type": "string"},
        "severity": {"type": "string", "enum": ["Low","Medium","High"]},
        "intent": {"type": "string"},
        "summary": {"type": "string"},
        "key_issue": {"type": "string"},
        "evidence": {"type": "string"},
        "confidence": {"type": "number"}
    },
    "required": ["sentiment","category","topic","product_area","severity","intent","summary","key_issue","evidence","confidence"]
}

SYSTEM = """You are a customer feedback analysis assistant for a product team.
Analyze conservatively. Never invent facts unsupported by the feedback.
For missing information use 'Not provided'. Return valid JSON matching the schema.
"""

def client():
    return genai.Client(api_key=API_KEY) if API_KEY else None

def local_demo(text):
    t=text.lower()
    if any(x in t for x in ["crash","crashes","error","not working","failed","freezes"]):
        cat,topic,area,sev="Technical Issue","App reliability","App performance","High"
    elif any(x in t for x in ["refund","money back"]):
        cat,topic,area,sev="Payments & Refunds","Refund","Payments","High"
    elif any(x in t for x in ["delivery","late","arrived","shipping"]):
        cat,topic,area,sev="Delivery","Delivery experience","Delivery","Medium"
    elif any(x in t for x in ["support","agent","response"]):
        cat,topic,area,sev="Customer Support","Support response","Support","Medium"
    elif any(x in t for x in ["price","expensive","cost"]):
        cat,topic,area,sev="Pricing","Price/value","Pricing","Medium"
    elif any(x in t for x in ["coupon","discount","promo"]):
        cat,topic,area,sev="Promotions","Coupon/discount","Promotions","Low"
    else:
        cat,topic,area,sev="General Feedback","General","Other","Low"
    neg=any(x in t for x in ["bad","terrible","failed","crash","problem","late","expensive","frustrat","not working","freeze"])
    pos=any(x in t for x in ["great","love","excellent","good","easy","helpful"])
    sent="Mixed" if neg and pos else "Negative" if neg else "Positive" if pos else "Neutral"
    return {"sentiment":sent,"category":cat,"topic":topic,"product_area":area,"severity":sev,
            "intent":"Complaint" if sent=="Negative" else "Praise" if sent=="Positive" else "Feedback",
            "summary":text[:160],"key_issue":text[:160],"evidence":text[:120],"confidence":0.55}

def analyze(text, c):
    prompt=f"""Analyze this customer feedback:
{text}
Return JSON with sentiment, category, topic, product_area, severity, intent, summary, key_issue, evidence (short exact phrase), and confidence 0-1.
Do not invent facts, causes, dates, business impact, or customer segments."""
    r=c.models.generate_content(model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM,
        response_mime_type="application/json", response_schema=SCHEMA, temperature=0.1))
    return json.loads(r.text)

def process(df, c):
    out=[]; bar=st.progress(0)
    for i,text in enumerate(df["feedback"].fillna("").astype(str)):
        try: x=analyze(text,c) if c else local_demo(text)
        except Exception as e:
            x=local_demo(text); x["_api_error"]=str(e)
        x["feedback"]=text; out.append(x); bar.progress((i+1)/len(df))
    bar.empty()
    return pd.DataFrame(out)

st.title("🧠 FeedbackIQ")
st.caption("AI Customer Feedback Intelligence — turn unstructured feedback into evidence-backed product insights.")

with st.sidebar:
    st.markdown("### FeedbackIQ")
    st.caption("AI Customer Feedback Intelligence")

    st.divider()

    st.markdown("**What it does**")
    st.markdown("""
    - Analyzes customer feedback
    - Identifies recurring issues
    - Detects sentiment & severity
    - Shows evidence behind insights
    - Helps PMs prioritize problems
    """)

    st.divider()

    st.markdown("**How it works**")
    st.caption("Feedback → AI Analysis → Themes → Insights")

    st.divider()

    st.markdown("**Built with**")
    st.caption("Gemini • Python • Streamlit")

    st.divider()

    st.markdown("**Prototype**")
    st.caption("Uses synthetic customer feedback for demonstration.")

tab1,tab2,tab3=st.tabs(["📊 Analyze feedback","🔎 Ask about feedback","ℹ️ Product notes"])

with tab1:
    st.subheader("Add customer feedback")
    sample=pd.DataFrame({"feedback":[
        "The payment failed three times when I tried to place my order.",
        "Delivery took 8 days instead of the promised 3 days.",
        "Customer support did not reply to my ticket for two days.",
        "I love the new interface. It is much easier to navigate.",
        "The app crashes whenever I try to upload a PDF.",
        "The refund has not arrived even though the order was cancelled.",
        "The coupon did not work at checkout.",
        "The product quality is excellent and delivery was on time.",
        "The delivery charge is too expensive for a small order.",
        "I cannot log in after the latest update."]})
    uploaded=st.file_uploader("Upload CSV with a column named `feedback`",type=["csv"])
    df= pd.read_csv(uploaded) if uploaded else sample
    if "feedback" not in df.columns:
        st.error("CSV must contain a `feedback` column."); df=sample
    st.dataframe(df.head(20),use_container_width=True)
    if st.button("🚀 Analyze Feedback",type="primary"):
        if not API_KEY: st.info("Running in local demo mode.")
        with st.spinner("Analyzing..."): st.session_state.result=process(df,client())
        st.success(f"Analyzed {len(df)} feedback items.")
    result=st.session_state.get("result")
    if result is not None:
        total=len(result)
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Total feedback",total)
        c2.metric("Negative",f"{(result.sentiment.eq('Negative').mean()*100):.1f}%")
        c3.metric("High severity",f"{(result.severity.eq('High').mean()*100):.1f}%")
        c4.metric("Topics",result.topic.nunique())
        st.subheader("Top recurring topics")
        themes=result.groupby("topic").size().sort_values(ascending=False).head(10)
        rows=[]
        for topic,count in themes.items():
            sub=result[result.topic==topic]
            sev=sub.severity.mode().iloc[0]
            score=round(min(count/total*100/10,5)+({"Low":1,"Medium":2,"High":3}[sev])*5/3,2)
            rows.append({"Topic":topic,"Feedback":int(count),"Share":f"{count/total*100:.1f}%","Typical severity":sev,
                          "Priority":"High" if score>=6 else "Medium" if score>=4 else "Low"})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        st.subheader("Sentiment")
        st.bar_chart(result.sentiment.value_counts())
        st.subheader("Evidence")
        selected=st.selectbox("Choose a topic",themes.index.tolist())
        st.dataframe(result[result.topic==selected][["feedback","sentiment","severity","evidence","confidence"]],
                     use_container_width=True,hide_index=True)
        st.subheader("AI product insight")
        top=themes.index[0]; n=int(themes.iloc[0])
        st.info(f"**{top}** is the most frequently detected topic: {n}/{total} feedback items ({n/total*100:.1f}%). Investigate the underlying feedback before deciding on a solution.")
        with st.expander("All structured outputs"): st.dataframe(result,use_container_width=True,hide_index=True)

with tab2:
    st.subheader("Ask questions about analyzed feedback")
    result=st.session_state.get("result")
    q=st.text_input("Example: What are the top problems customers are reporting?")
    if st.button("Ask AI"):
        if result is None: st.warning("Analyze feedback first.")
        elif not API_KEY: st.warning("Q&A requires a Gemini API key.")
        elif not q.strip(): st.warning("Enter a question.")
        else:
            context=result[["feedback","sentiment","topic","severity","summary"]].to_dict("records")
            prompt=f"""Answer the product manager's question using ONLY this feedback evidence.
Question: {q}
Evidence: {json.dumps(context,ensure_ascii=False)}
If evidence is insufficient, say so."""
            with st.spinner("Finding evidence..."):
                r=client().models.generate_content(model=MODEL,contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM,temperature=0.1))
            st.write(r.text)

with tab3:
    st.subheader("How it works")
    st.markdown("""**Problem:** Product teams receive large volumes of unstructured feedback.

**Solution:** An LLM extracts structured information and groups recurring issues; deterministic code handles aggregation, evidence display and transparent prioritization.

**Prototype note:** Uses synthetic/sample feedback and is not connected to private company data.

**Future:** embeddings + vector search + RAG, trend analysis, source connectors, human review and stronger evaluation.""")
