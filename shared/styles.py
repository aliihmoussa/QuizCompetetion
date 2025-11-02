"""
Styling utilities for consistent UI/UX across the application
"""
import streamlit as st


# Color Palette
COLORS = {
    # Primary Colors
    'primary': '#2563EB',  # Blue
    'primary_dark': '#1E40AF',
    'primary_light': '#DBEAFE',
    
    # Secondary Colors
    'secondary': '#10B981',  # Green
    'secondary_dark': '#059669',
    'secondary_light': '#D1FAE5',
    
    # Accent Colors
    'accent': '#F59E0B',  # Amber
    'accent_dark': '#D97706',
    'accent_light': '#FEF3C7',
    
    # Neutrals
    'background': '#F9FAFB',
    'surface': '#FFFFFF',
    'border': '#E5E7EB',
    'text_primary': '#111827',
    'text_secondary': '#6B7280',
    'text_muted': '#9CA3AF',
    
    # Status Colors
    'success': '#10B981',
    'success_light': '#D1FAE5',
    'success_dark': '#059669',
    'warning': '#F59E0B',
    'warning_light': '#FEF3C7',
    'warning_dark': '#D97706',
    'error': '#EF4444',
    'error_light': '#FEE2E2',
    'error_dark': '#DC2626',
    'info': '#3B82F6',
    'info_light': '#DBEAFE',
    'info_dark': '#2563EB',
    
    # Chart Colors
    'chart_1': '#2563EB',
    'chart_2': '#10B981',
    'chart_3': '#F59E0B',
    'chart_4': '#8B5CF6',
    'chart_5': '#EC4899',
}


def inject_custom_css():
    """Inject custom CSS for modern, professional styling"""
    css = f"""
    <style>
        /* Global Styles */
        .main {{
            background-color: {COLORS['background']};
        }}
        
        /* Hide default Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Custom Top Navigation */
        .top-nav {{
            position: sticky;
            top: 0;
            z-index: 999;
            background: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: -1rem -1rem 2rem -1rem;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid {COLORS['border']};
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            margin: 0.5rem 0;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            font-weight: 500;
            color: {COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .metric-delta {{
            font-size: 0.875rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }}
        
        .metric-delta.positive {{
            color: {COLORS['success']};
        }}
        
        .metric-delta.negative {{
            color: {COLORS['error']};
        }}
        
        /* Buttons */
        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
            border: none;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Primary Button */
        .btn-primary {{
            background-color: {COLORS['primary']} !important;
            color: white !important;
        }}
        
        .btn-primary:hover {{
            background-color: {COLORS['primary_dark']} !important;
        }}
        
        /* Success Button */
        .btn-success {{
            background-color: {COLORS['success']} !important;
            color: white !important;
        }}
        
        /* Danger Button */
        .btn-danger {{
            background-color: {COLORS['error']} !important;
            color: white !important;
        }}
        
        /* Cards */
        .custom-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid {COLORS['border']};
            margin-bottom: 1rem;
        }}
        
        /* Status Badges */
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .status-badge.active {{
            background-color: {COLORS['secondary_light']};
            color: {COLORS['secondary_dark']};
        }}
        
        .status-badge.pending {{
            background-color: {COLORS['accent_light']};
            color: {COLORS['accent_dark']};
        }}
        
        .status-badge.closed {{
            background-color: {COLORS['border']};
            color: {COLORS['text_secondary']};
        }}
        
        /* Tables */
        .dataframe {{
            border-radius: 8px;
            overflow: hidden;
        }}
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {{
            border-radius: 8px;
            border: 2px solid {COLORS['border']};
            transition: border-color 0.2s;
        }}
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {COLORS['primary']};
            box-shadow: 0 0 0 3px {COLORS['primary_light']};
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div > div {{
            background-color: {COLORS['primary']};
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: {COLORS['surface']};
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 0.75rem 1.5rem;
            font-weight: 600;
        }}
        
        /* Loading Animation */
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        .spinner {{
            animation: spin 1s linear infinite;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .metric-card {{
                padding: 1rem;
            }}
            
            .metric-value {{
                font-size: 1.5rem;
            }}
            
            .top-nav {{
                padding: 0.75rem 1rem;
            }}
        }}
        
        /* Hide Streamlit branding */
        .stDeployButton {{
            display: none;
        }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS['background']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {COLORS['border']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['text_muted']};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_status_color(status: str) -> str:
    """Get color for a given status"""
    status_colors = {
        'ACTIVE': COLORS['success'],
        'PENDING': COLORS['warning'],
        'CLOSED': COLORS['text_secondary'],
        'active': COLORS['success'],
        'pending': COLORS['warning'],
        'closed': COLORS['text_secondary'],
    }
    return status_colors.get(status, COLORS['text_secondary'])


def get_chart_colors(n: int = 5) -> list:
    """Get list of chart colors"""
    chart_colors = [
        COLORS['chart_1'],
        COLORS['chart_2'],
        COLORS['chart_3'],
        COLORS['chart_4'],
        COLORS['chart_5'],
    ]
    return chart_colors[:n] if n <= 5 else chart_colors * (n // 5 + 1)

