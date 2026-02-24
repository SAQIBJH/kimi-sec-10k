"""
Global CSS styles and design tokens.
Pixel-perfect styling matching Figma design specifications.
"""

# ============================================================================
# DESIGN TOKENS
# ============================================================================

# Color Palette
COLORS = {
    # Primary
    "primary": "#0066CC",
    "primary_hover": "#0052A3",
    "primary_light": "#E6F2FF",
    
    # Secondary
    "secondary": "#6C757D",
    "secondary_hover": "#5A6268",
    
    # Semantic Colors
    "success": "#28A745",
    "success_light": "#D4EDDA",
    "warning": "#FFC107",
    "warning_light": "#FFF3CD",
    "danger": "#DC3545",
    "danger_light": "#F8D7DA",
    "info": "#17A2B8",
    "info_light": "#D1ECF1",
    
    # Neutral Scale
    "white": "#FFFFFF",
    "gray_50": "#F8F9FA",
    "gray_100": "#F1F3F5",
    "gray_200": "#E9ECEF",
    "gray_300": "#DEE2E6",
    "gray_400": "#CED4DA",
    "gray_500": "#ADB5BD",
    "gray_600": "#6C757D",
    "gray_700": "#495057",
    "gray_800": "#343A40",
    "gray_900": "#212529",
    "black": "#000000",
    
    # Chart Colors
    "chart_primary": "#0066CC",
    "chart_secondary": "#00C49F",
    "chart_tertiary": "#FFBB28",
    "chart_quaternary": "#FF8042",
    "chart_up": "#28A745",
    "chart_down": "#DC3545",
}

# Typography
TYPOGRAPHY = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "font_family_mono": "'SF Mono', Monaco, 'Cascadia Code', monospace",
    
    # Font Sizes
    "text_xs": "0.75rem",      # 12px
    "text_sm": "0.875rem",     # 14px
    "text_base": "1rem",       # 16px
    "text_lg": "1.125rem",     # 18px
    "text_xl": "1.25rem",      # 20px
    "text_2xl": "1.5rem",      # 24px
    "text_3xl": "1.875rem",    # 30px
    "text_4xl": "2.25rem",     # 36px
    
    # Font Weights
    "font_normal": "400",
    "font_medium": "500",
    "font_semibold": "600",
    "font_bold": "700",
    
    # Line Heights
    "leading_tight": "1.25",
    "leading_snug": "1.375",
    "leading_normal": "1.5",
    "leading_relaxed": "1.625",
}

# Spacing
SPACING = {
    "space_0": "0",
    "space_1": "0.25rem",   # 4px
    "space_2": "0.5rem",    # 8px
    "space_3": "0.75rem",   # 12px
    "space_4": "1rem",      # 16px
    "space_5": "1.25rem",   # 20px
    "space_6": "1.5rem",    # 24px
    "space_8": "2rem",      # 32px
    "space_10": "2.5rem",   # 40px
    "space_12": "3rem",     # 48px
    "space_16": "4rem",     # 64px
}

# Border Radius
BORDER_RADIUS = {
    "rounded_none": "0",
    "rounded_sm": "0.125rem",   # 2px
    "rounded": "0.25rem",       # 4px
    "rounded_md": "0.375rem",   # 6px
    "rounded_lg": "0.5rem",     # 8px
    "rounded_xl": "0.75rem",    # 12px
    "rounded_2xl": "1rem",      # 16px
    "rounded_full": "9999px",
}

# Shadows
SHADOWS = {
    "shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
    "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    "shadow_xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
}

# ============================================================================
# GLOBAL CSS
# ============================================================================

def get_global_css() -> str:
    """Return global CSS styles — minimal, matching screenshot design."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {{
        --primary: {COLORS["primary"]};
        --primary-hover: {COLORS["primary_hover"]};
        --primary-light: {COLORS["primary_light"]};
        --success: {COLORS["success"]};
        --danger: {COLORS["danger"]};
        --warning: {COLORS["warning"]};
        --gray-50: {COLORS["gray_50"]};
        --gray-100: {COLORS["gray_100"]};
        --gray-200: {COLORS["gray_200"]};
        --gray-300: {COLORS["gray_300"]};
        --gray-600: {COLORS["gray_600"]};
        --gray-700: {COLORS["gray_700"]};
        --gray-800: {COLORS["gray_800"]};
        --gray-900: {COLORS["gray_900"]};
    }}
    
    /* Global Reset — white background per screenshot */
    .stApp {{
        font-family: {TYPOGRAPHY["font_family"]};
        background-color: {COLORS["white"]};
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS["gray_100"]};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {COLORS["gray_400"]};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS["gray_500"]};
    }}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {TYPOGRAPHY["font_family"]};
        font-weight: {TYPOGRAPHY["font_semibold"]};
        color: {COLORS["gray_900"]};
        margin-bottom: 1rem;
    }}
    [data-testid="stSidebarCollapsedControl"] {{
        visibility: hidden;
        display: none !important;
    }}
    
    /* Button Styling */
    .stButton > button {{
        font-family: {TYPOGRAPHY["font_family"]};
        font-weight: {TYPOGRAPHY["font_medium"]};
        border-radius: {BORDER_RADIUS["rounded_lg"]};
        transition: all 0.2s ease;
    }}
    
    .stButton > button[kind="primary"] {{
        background-color: {COLORS["primary"]};
        border: none;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {COLORS["primary_hover"]};
        transform: translateY(-1px);
        box-shadow: {SHADOWS["shadow_md"]};
    }}
    
    /* Input Styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {{
        border-radius: {BORDER_RADIUS["rounded_lg"]};
        border: 1px solid {COLORS["gray_300"]};
        font-family: {TYPOGRAPHY["font_family"]};
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus {{
        border-color: {COLORS["primary"]};
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }}
    
    /* DataFrame Styling */
    .stDataFrame {{
        border-radius: {BORDER_RADIUS["rounded_lg"]};
        overflow: hidden;
    }}
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        border-bottom: 1px solid {COLORS["gray_200"]};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 1rem 1.5rem;
        font-weight: {TYPOGRAPHY["font_medium"]};
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {COLORS["primary"]} !important;
        border-bottom-color: {COLORS["primary"]} !important;
    }}
    </style>
    """


def render_styles():
    """Render global CSS styles in Streamlit."""
    import streamlit as st
    st.markdown(get_global_css(), unsafe_allow_html=True)


def set_page_layout(
    header_full_width: bool = True,
    footer_full_width: bool = True,
    body_padding: str = "0 20px",
    max_content_width: str = "1350px",
    remove_top_padding: bool = True,
    footer_at_bottom: bool = True
):
    """
    Set adjustable page layout parameters.
    
    This function allows you to customize the page layout padding and width.
    Call this in your page entry point after hide_sidebar().
    
    LOCATION: app/components/styles.py
    
    Parameters:
    -----------
    header_full_width : bool
        If True, header takes full width with no side padding
    footer_full_width : bool
        If True, footer takes full width with no side padding
    body_padding : str
        CSS padding for body content (e.g., "0 20px", "20px", "0")
        Default: "0 20px" (0 top/bottom, 20px left/right)
    max_content_width : str
        Maximum width for content (e.g., "1350px", "100%", "1200px")
        Default: "1350px"
    remove_top_padding : bool
        If True, removes the default top padding from Streamlit
    footer_at_bottom : bool
        If True, footer sticks to bottom of page
        
    Examples:
    ---------
    # Full width with minimal padding
    set_page_layout(body_padding="0 10px", max_content_width="100%")
    
    # Centered content with more padding
    set_page_layout(body_padding="20px 40px", max_content_width="1200px")
    
    # Default behavior
    set_page_layout()  # Uses all defaults
    """
    import streamlit as st
    
    css_parts = []
    
    # Remove top padding and margins
    if remove_top_padding:
        css_parts.append("""
        /* Remove default Streamlit top padding */
        .stApp {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
            max-width: """ + max_content_width + """;
            padding-left: """ + body_padding.split()[1] if len(body_padding.split()) > 1 else body_padding + """;
            padding-right: """ + body_padding.split()[1] if len(body_padding.split()) > 1 else body_padding + """;
        }
        /* Remove padding from main container */
        div[data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        """)
    
    # Body content padding
    css_parts.append(f"""
    /* Body content padding - ADJUSTABLE via body_padding parameter */
    .main .block-container > div {{
        padding: {body_padding};
    }}
    """)
    
    # Footer at bottom
    if footer_at_bottom:
        css_parts.append("""
        /* Footer at bottom - no space below */
        .site-footer {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        """)
    
    st.markdown("<style>" + "\n".join(css_parts) + "</style>", unsafe_allow_html=True)


def hide_sidebar():
    """
    Immediately hide the Streamlit sidebar to prevent skeleton flash.
    
    IMPORTANT: Must be called immediately after st.set_page_config() 
    to prevent sidebar skeleton from showing during page load.
    
    Uses both CSS and JavaScript for maximum compatibility during navigation.
    Also removes top spacing from Streamlit's default elements.
    
    LOCATION: app/components/styles.py
    """
    import streamlit as st
    from streamlit.components.v1 import html
    
    # CSS to hide sidebar AND remove top spacing
    css_styles = """
    <style>
    /* Collapse st.markdown wrappers that ONLY contain a <style> tag (no other content) */
    div[data-testid="stElementContainer"]:has(> div[data-testid="stMarkdown"] style:only-child) {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        line-height: 0 !important;
    }

    /* Hide sidebar immediately on page load - prevents skeleton flash */
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"],
    .stSidebar {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        opacity: 0 !important;
    }
    /* Also hide the sidebar collapse button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Remove spacing from sidebar iframe containers only */
    [data-testid="stSidebar"] iframe {
        display: block;
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
    }
    /* Ensure no top padding on main container */
    .stApp {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .stAppViewContainer {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .stMain {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
        padding-bottom: 0 !important;
    }

    
    /* Override Emotion link styles with higher specificity */
    html body .coresight-header-container a,
    html body .coresight-header-container a:link,
    html body .coresight-header-container a:visited,
    html body .coresight-header-container a:active,
    html body [class*="coresight-header"] a,
    html body [class*="coresight-header"] a:link,
    html body [class*="coresight-header"] a:visited,
    html body [class*="coresight-header"] a:active {
        color: inherit !important;
        text-decoration: none !important;
    }
    /* Override any emotion cache link styles for nav links */
    html body [class*="st-emotion-cache"] a.coresight-nav-link {
        color: inherit !important;
        text-decoration: none !important;
    }
    /* Contact Us button - WHITE text with high specificity */
    html body .coresight-contact-btn,
    html body [class*="st-emotion-cache"] a.coresight-contact-btn,
    html body .coresight-header-container a.coresight-contact-btn,
    html body .coresight-header-container a.coresight-contact-btn:link,
    html body .coresight-header-container a.coresight-contact-btn:visited {
        color: #fff !important;
        text-decoration: none !important;
    }
    html body .coresight-contact-btn:hover,
    html body [class*="st-emotion-cache"] a.coresight-contact-btn:hover,
    html body .coresight-header-container a.coresight-contact-btn:hover {
        color: #d62e2f !important;
    }
    /* Remove Emotion style tags from head via CSS (backup) */
    """
    
    st.markdown(css_styles, unsafe_allow_html=True)
    
    # JavaScript approach - runs immediately to hide elements, remove Emotion styles, and remove spacing
   
