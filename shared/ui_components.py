"""
Reusable UI components for consistent interface across the application
"""
import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime
from .styles import COLORS, get_status_color


def metric_card(label: str, value: str, delta: Optional[str] = None, delta_positive: bool = True):
    """
    Display a modern metric card
    
    Args:
        label: Metric label
        value: Main metric value
        delta: Optional change indicator
        delta_positive: Whether delta is positive (green) or negative (red)
    """
    delta_class = "positive" if delta_positive else "negative"
    delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ''
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """
    Create a status badge HTML
    
    Args:
        status: Status text (ACTIVE, PENDING, CLOSED, etc.)
    
    Returns:
        HTML string for status badge
    """
    status_lower = status.lower()
    return f'<span class="status-badge {status_lower}">{status.upper()}</span>'


def card_container(content: str, title: Optional[str] = None):
    """
    Display content in a card container
    
    Args:
        content: HTML content to display
        title: Optional card title
    """
    title_html = f'<h3 style="margin-top: 0; color: {COLORS["text_primary"]};">{title}</h3>' if title else ''
    html = f"""
    <div class="custom-card">
        {title_html}
        {content}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def empty_state(icon: str, title: str, message: str, action_label: Optional[str] = None):
    """
    Display an empty state with icon and message
    
    Args:
        icon: Emoji or icon
        title: Empty state title
        message: Descriptive message
        action_label: Optional call-to-action button label
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h2 style="color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">{title}</h2>
            <p style="color: {COLORS['text_secondary']}; font-size: 1.125rem;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if action_label:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            return st.button(action_label, use_container_width=True)
    return False


def loading_spinner(message: str = "Loading..."):
    """Display a loading spinner with message"""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem;">
            <div class="spinner" style="display: inline-block; font-size: 2rem;">⏳</div>
            <p style="color: {COLORS['text_secondary']}; margin-top: 1rem;">{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def data_table(data: List[Dict[str, Any]], columns: List[str], key: str = "table"):
    """
    Display a formatted data table
    
    Args:
        data: List of dictionaries containing row data
        columns: List of column names to display
        key: Unique key for the table
    """
    if not data:
        empty_state("📋", "No Data", "No records to display")
        return
    
    # Create table HTML
    header_html = "".join([f'<th style="text-align: left; padding: 0.75rem; background: {COLORS["background"]}; font-weight: 600; color: {COLORS["text_primary"]};">{col}</th>' for col in columns])
    
    rows_html = ""
    for idx, row in enumerate(data):
        bg_color = COLORS['surface'] if idx % 2 == 0 else COLORS['background']
        cells_html = "".join([
            f'<td style="padding: 0.75rem; border-top: 1px solid {COLORS["border"]};">{row.get(col, "")}</td>'
            for col in columns
        ])
        rows_html += f'<tr style="background: {bg_color};">{cells_html}</tr>'
    
    table_html = f"""
    <table style="width: 100%; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <thead>
            <tr>{header_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)


def section_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None):
    """
    Display a section header with optional subtitle and icon
    
    Args:
        title: Section title
        subtitle: Optional subtitle
        icon: Optional emoji icon
    """
    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ''
    subtitle_html = f'<p style="color: {COLORS["text_secondary"]}; font-size: 1rem; margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''
    
    html = f"""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="color: {COLORS['text_primary']}; margin: 0; display: flex; align-items: center;">
            {icon_html}{title}
        </h2>
        {subtitle_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def progress_indicator(current: int, total: int, label: str = "Progress"):
    """
    Display a progress indicator with label
    
    Args:
        current: Current value
        total: Total value
        label: Progress label
    """
    percentage = (current / total * 100) if total > 0 else 0
    
    st.markdown(
        f"""
        <div style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-weight: 600; color: {COLORS['text_primary']};">{label}</span>
                <span style="color: {COLORS['text_secondary']};">{current}/{total}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.progress(percentage / 100)


def info_box(message: str, type: str = "info"):
    """
    Display an info/warning/error/success box
    
    Args:
        message: Message to display
        type: Type of box (info, warning, error, success)
    """
    colors_map = {
        'info': (COLORS['info'], COLORS['primary_light']),
        'warning': (COLORS['warning'], COLORS['accent_light']),
        'error': (COLORS['error'], '#FEE2E2'),
        'success': (COLORS['success'], COLORS['secondary_light']),
    }
    
    border_color, bg_color = colors_map.get(type, colors_map['info'])
    
    icons = {
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
    }
    
    icon = icons.get(type, 'ℹ️')
    
    html = f"""
    <div style="padding: 1rem; border-left: 4px solid {border_color}; background: {bg_color}; border-radius: 4px; margin: 1rem 0;">
        <span style="margin-right: 0.5rem;">{icon}</span>
        <span style="color: {COLORS['text_primary']};">{message}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def info_card(title: str, message: str, icon: str = "ℹ️"):
    """
    Display an info card with title and message
    
    Args:
        title: Card title
        message: Card message
        icon: Optional emoji icon
    """
    html = f"""
    <div style="background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
        <h3 style="color: {COLORS['text_primary']}; margin: 0.5rem 0;">{title}</h3>
        <p style="color: {COLORS['text_secondary']}; margin: 0.5rem 0;">{message}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def stats_grid(stats: List[Dict[str, str]], columns: int = 4):
    """
    Display statistics in a grid layout
    
    Args:
        stats: List of dicts with 'label', 'value', and optional 'delta'
        columns: Number of columns in grid
    """
    cols = st.columns(columns)
    
    for idx, stat in enumerate(stats):
        with cols[idx % columns]:
            metric_card(
                label=stat['label'],
                value=stat['value'],
                delta=stat.get('delta'),
                delta_positive=stat.get('delta_positive', True)
            )


def action_button(label: str, icon: str = "", button_type: str = "primary", key: Optional[str] = None) -> bool:
    """
    Display a styled action button
    
    Args:
        label: Button label
        icon: Optional emoji icon
        button_type: Button type (primary, success, danger)
        key: Unique key for button
    
    Returns:
        Boolean indicating if button was clicked
    """
    button_label = f"{icon} {label}" if icon else label
    return st.button(button_label, key=key, use_container_width=True, type="primary" if button_type == "primary" else "secondary")


def divider_with_text(text: str):
    """Display a divider with centered text"""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; margin: 2rem 0;">
            <div style="flex: 1; height: 1px; background: {COLORS['border']};"></div>
            <span style="padding: 0 1rem; color: {COLORS['text_secondary']}; font-weight: 600; text-transform: uppercase; font-size: 0.875rem;">{text}</span>
            <div style="flex: 1; height: 1px; background: {COLORS['border']};"></div>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_datetime(dt: datetime, format: str = "relative") -> str:
    """
    Format datetime for display
    
    Args:
        dt: Datetime object
        format: Format type ('relative', 'short', 'long')
    
    Returns:
        Formatted datetime string
    """
    if format == "relative":
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        diff = now - dt
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() / 60)
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff < timedelta(days=30):
            days = diff.days
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            return dt.strftime("%B %d, %Y")
    elif format == "short":
        return dt.strftime("%Y-%m-%d %H:%M")
    else:  # long
        return dt.strftime("%B %d, %Y at %I:%M %p")


def top_navigation(items: List[Dict[str, str]], active: str, logo: str = "🏆"):
    """
    Create top navigation bar
    
    Args:
        items: List of nav items with 'label' and 'key'
        active: Currently active item key
        logo: Logo emoji or text
    
    Returns:
        Selected nav item key
    """
    st.markdown(
        f"""
        <div class="top-nav">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['primary']};">
                    {logo} Quiz Competition
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create navigation tabs
    cols = st.columns([1] * len(items))
    selected = active
    
    for idx, item in enumerate(items):
        with cols[idx]:
            if st.button(item['label'], key=f"nav_{item['key']}", use_container_width=True):
                selected = item['key']
    
    return selected

