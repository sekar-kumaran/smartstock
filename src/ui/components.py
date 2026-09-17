import streamlit as st
from src.state.data_context import DataContext


def page_header(title: str, description: str):
    """Renders a professional page header with breadcrumb and mode badge."""
    mode = DataContext.get_mode()

    if mode == DataContext.MODE_DEMO:
        badge = '<span style="display:inline-flex;align-items:center;padding:3px 10px;border-radius:20px;font-size:0.7rem;font-weight:700;background:linear-gradient(135deg,#dbeafe,#ede9fe);color:#3730a3;border:1px solid #c7d2fe;margin-left:12px;vertical-align:middle;">DEMO DATA</span>'
    elif mode == DataContext.MODE_USER:
        badge = '<span style="display:inline-flex;align-items:center;padding:3px 10px;border-radius:20px;font-size:0.7rem;font-weight:700;background:linear-gradient(135deg,#d1fae5,#ecfdf5);color:#065f46;border:1px solid #a7f3d0;margin-left:12px;vertical-align:middle;">USER DATA</span>'
    else:
        badge = ''

    st.markdown(f"""
        <div style="margin-bottom:2rem;">
            <p style="font-size:0.75rem;font-weight:700;letter-spacing:0.1em;color:#6366f1 !important;margin-bottom:4px;">SMARTSTOCK / {title.upper()}</p>
            <h1 style="margin:0;padding:0;line-height:1.2;">{title} {badge}</h1>
            <p style="color:#64748b !important;font-size:1rem;margin-top:6px;">{description}</p>
        </div>
    """, unsafe_allow_html=True)


def empty_state(title: str, message: str, icon: str = "⚠️"):
    """Professional empty/error state with glassmorphism."""
    st.markdown(f"""
        <div style="text-align:center;padding:3.5rem 2rem;background:rgba(255,255,255,0.7);backdrop-filter:blur(12px);border:1px solid rgba(99,102,241,0.12);border-radius:20px;margin:2rem auto;max-width:500px;box-shadow:0 8px 30px rgba(0,0,0,0.04);">
            <div style="font-size:3.5rem;margin-bottom:1rem;opacity:0.8;">{icon}</div>
            <h3 style="color:#0f172a !important;font-weight:700;margin-bottom:0.5rem;">{title}</h3>
            <p style="color:#64748b !important;font-size:0.95rem;max-width:350px;margin:0 auto;">{message}</p>
        </div>
    """, unsafe_allow_html=True)


def insight_card(title: str, content: str, recommendation: str, level: str = "info"):
    """Professional business insight card with glassmorphism and colored accent."""
    styles = {
        "info": {"border": "#3b82f6", "bg": "rgba(59,130,246,0.06)", "icon": "💡"},
        "warning": {"border": "#f59e0b", "bg": "rgba(245,158,11,0.06)", "icon": "⚠️"},
        "danger": {"border": "#ef4444", "bg": "rgba(239,68,68,0.06)", "icon": "🚨"},
        "success": {"border": "#10b981", "bg": "rgba(16,185,129,0.06)", "icon": "✅"},
    }
    s = styles.get(level, styles["info"])

    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.75);backdrop-filter:blur(12px);border-left:4px solid {s['border']};border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1rem;box-shadow:0 4px 12px rgba(0,0,0,0.04);border:1px solid rgba(99,102,241,0.08);border-left:4px solid {s['border']};transition:transform 0.2s ease;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:1.1rem;">{s['icon']}</span>
                <h4 style="margin:0;color:#0f172a !important;font-size:0.95rem;font-weight:700;">{title}</h4>
            </div>
            <p style="color:#475569 !important;font-size:0.88rem;line-height:1.6;margin-bottom:10px;">{content}</p>
            <div style="background:{s['bg']};padding:10px 14px;border-radius:8px;">
                <span style="font-weight:700;color:#334155 !important;font-size:0.82rem;">→ Action:</span>
                <span style="color:#475569 !important;font-size:0.82rem;margin-left:4px;">{recommendation}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", delta_color: str = "green"):
    """Custom KPI card with glassmorphism — more control than st.metric."""
    delta_html = ""
    if delta:
        color = "#10b981" if delta_color == "green" else "#ef4444" if delta_color == "red" else "#64748b"
        delta_html = f'<span style="font-size:0.8rem;font-weight:600;color:{color} !important;">{delta}</span>'

    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.75);backdrop-filter:blur(12px);border:1px solid rgba(99,102,241,0.12);border-radius:16px;padding:1.25rem;box-shadow:0 4px 12px rgba(0,0,0,0.04);transition:transform 0.2s ease;text-align:center;">
            <p style="font-size:0.75rem;font-weight:700;color:#64748b !important;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">{label}</p>
            <p style="font-size:1.8rem;font-weight:800;color:#0f172a !important;margin:0;line-height:1.2;">{value}</p>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = ""):
    """Section divider with optional subtitle."""
    sub_html = f'<p style="color:#64748b !important;font-size:0.9rem;margin-top:2px;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
        <div style="margin:1.5rem 0 1rem 0;border-bottom:2px solid rgba(99,102,241,0.1);padding-bottom:8px;">
            <h3 style="color:#1e293b !important;margin:0;">{title}</h3>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)


def plotly_light_layout():
    """Returns a standard Plotly layout dict for the light theme."""
    return dict(
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, sans-serif", color="#334155", size=12),
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(showgrid=True, gridcolor="rgba(99,102,241,0.06)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(99,102,241,0.06)", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(255,255,255,0.6)", bordercolor="rgba(99,102,241,0.1)", borderwidth=1),
        colorway=["#3b82f6", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444",
                  "#ec4899", "#6366f1", "#14b8a6", "#f97316"]
    )
