Comprehensive Streamlit Documentation Analysis
1. ALL STREAMLIT COMPONENTS (Complete API Reference)
1.1 Write and Magic Commands
Component	Description
st.write(*args, unsafe_allow_html=False)	Swiss-army knife for displaying data, text, markdown, dataframes, charts, and more
st.write_stream(stream, *, cursor=None)	Write generators or streams with typewriter effect
Magic	Auto-prints variables/literals on their own line
1.2 Text Elements (13 components)
Component	Description
st.markdown(body, unsafe_allow_html=False, help=None, width="stretch", text_alignment="left")	GitHub-flavored Markdown display
st.title(body, anchor=None, help=None, width="stretch", text_alignment="left")	Title formatting
st.header(body, anchor=None, help=None, divider=False, width="stretch", text_alignment="left")	Header formatting with optional divider
st.subheader(body, anchor=None, help=None, divider=False, width="stretch", text_alignment="left")	Subheader formatting
st.badge(label, icon=None, color="blue", width="content", help=None)	Small colored badge
st.caption(body, unsafe_allow_html=False, help=None, width="stretch", text_alignment="left")	Small caption text
st.code(body, language="python", line_numbers=False, wrap_lines=False, height="content", width="stretch")	Syntax-highlighted code block
st.text(body, help=None, width="content", text_alignment="left")	Fixed-width preformatted text
st.latex(body, help=None, width="stretch")	LaTeX mathematical expressions
st.divider(width="stretch")	Horizontal rule/divider
st.help(obj, width="stretch")	Display object's docstring
st.html(body, width="stretch", unsafe_allow_javascript=False)	Render HTML strings
st.echo(code_location="above")	Display code then execute it
1.3 Data Display Elements (6 components)
Component	Description
st.dataframe(data, width="stretch", height="auto", hide_index=None, column_order=None, column_config=None, on_select="ignore", selection_mode="multi-row")	Interactive dataframe table with selection
st.data_editor(data, width="stretch", height="auto", num_rows="fixed", disabled=False, on_change=None)	Editable data table
st.column_config.*	Configure column display (17 column types - see section 4)
st.table(data)	Static table display
st.metric(label, value, delta=None, delta_color="normal", help=None, border=False, chart_data=None, chart_type="line", format=None)	Metric display with sparkline
st.json(data)	Pretty-printed JSON
1.4 Chart Elements (10 native + library support)
Component	Description
st.line_chart(data, x=None, y=None, color=None)	Simple line chart
st.area_chart(data, x=None, y=None, color=None)	Area chart
st.bar_chart(data, x=None, y=None, color=None)	Bar chart
st.scatter_chart(data, x=None, y=None, color=None)	Scatter plot
st.map(data, latitude=None, longitude=None, color=None, size=None, zoom=None)	Map with scatter points
st.pyplot(fig)	Matplotlib figure
st.altair_chart(chart)	Altair chart
st.vega_lite_chart(spec)	Vega-Lite chart
st.plotly_chart(fig)	Plotly chart
st.pydeck_chart(pydeck_obj)	PyDeck (deck.gl) chart
st.graphviz_chart(spec)	GraphViz graph
1.5 Input Widgets (25+ components)
Component	Description
st.button(label, key=None, help=None, on_click=None, type="secondary", icon=None, disabled=False, shortcut=None)	Button widget
st.download_button(label, data, file_name, mime=None, on_click="rerun", type="secondary", icon=None, shortcut=None)	Download button
st.form_submit_button(label, type="secondary", icon=None)	Form submit button
st.link_button(label, url, type="secondary", icon=None, shortcut=None)	External link button
st.page_link(page, label=None, icon=None, help=None)	Link to another page
st.checkbox(label, value=False, key=None, help=None, on_change=None)	Checkbox
st.toggle(label, value=False, key=None, help=None, on_change=None)	Toggle switch
st.radio(label, options, index=0, format_func=None, horizontal=False, captions=None)	Radio buttons
st.selectbox(label, options, index=0, format_func=None, placeholder=None, accept_new_options=False)	Dropdown select
st.multiselect(label, options, default=None, format_func=None, max_selections=None, accept_new_options=False)	Multi-select dropdown
st.pills(label, options, selection_mode="single", format_func=None)	Pill-button selection
st.segmented_control(label, options, selection_mode="single", format_func=None)	Segmented button control
st.select_slider(label, options, value=None, format_func=None)	Slider with discrete options
st.slider(label, min_value=None, max_value=None, value=None, step=None, format=None)	Numeric/date/time range slider
st.number_input(label, min_value=None, max_value=None, value="min", step=None, format=None, placeholder=None, icon=None)	Numeric input
st.text_input(label, value="", max_chars=None, type="default", placeholder=None, icon=None, autocomplete=None)	Single-line text
st.text_area(label, value="", height=None, max_chars=None, placeholder=None)	Multi-line text area
st.date_input(label, value="today", min_value=None, max_value=None, format="YYYY/MM/DD")	Date picker
st.time_input(label, value="now", step=None)	Time picker
st.datetime_input(label, value="now", min_value=None, max_value=None, step=None)	DateTime picker
st.color_picker(label, value=None)	Color picker
st.file_uploader(label, type=None, accept_multiple_files=False, max_upload_size=None)	File upload
st.camera_input(label)	Camera/image capture
st.audio_input(label, sample_rate=16000)	Audio recording
st.chat_input(placeholder, max_chars=None)	Chat message input
st.feedback(options="thumbs", default=None)	Rating widget (thumbs/faces/stars)
1.6 Layout & Containers (11 components)
Component	Description
st.columns(spec, gap="small", vertical_alignment="top", border=False)	Side-by-side columns
st.container(*, border=None, key=None, width="stretch", height="content", horizontal=False, horizontal_alignment="left", vertical_alignment="top", gap="small")	Multi-element container
st.empty()	Single-element placeholder
st.expander(label, expanded=False, icon=None)	Collapsible section
st.popover(label, type="secondary", help=None, icon=None)	Popover container
st.tabs(tabs, width="stretch", default=None)	Tabbed interface
st.sidebar	Sidebar container (object notation or with)
st.form(key, clear_on_submit=False, enter_to_submit=True, border=True)	Form for batching inputs
st.dialog(title, *, width="small", dismissible=True, icon=None, on_dismiss="ignore")	Modal dialog (decorator)
@st.fragment(run_every=None)	Partial reruns
st.space("small")	Add vertical/horizontal space
1.7 Media Elements (5 components)
Component	Description
st.image(image, caption=None, width="content", clamp=False, channels="RGB", output_format="auto")	Display images
st.audio(data, format="audio/wav", start_time=0, sample_rate=None, end_time=None, loop=False, autoplay=False)	Audio player
st.video(data, format="video/mp4", start_time=0, subtitles=None, end_time=None, loop=False, autoplay=False, muted=False)	Video player
st.logo(image, *, size="medium", link=None, icon_image=None)	App logo
st.pdf(data, *, height=500)	PDF viewer
1.8 Chat Elements (3 components)
Component	Description
st.chat_input(placeholder, max_chars=None)	Chat input widget
st.chat_message(name, avatar=None)	Chat message container
st.status(label, expanded=False, state="running")	Status container for long tasks
1.9 Status & Progress (9 components)
Component	Description
st.progress(value, text=None)	Progress bar (0-100)
st.spinner(text="In progress...", show_time=False)	Loading spinner
st.status(label, expanded=False, state="running")	Expandable status container
st.toast(body, icon=None, duration="short")	Brief notification
st.balloons()	Celebration animation
st.snow()	Snowfall animation
st.success(body, icon=None)	Success message box
st.info(body, icon=None)	Info message box
st.warning(body, icon=None)	Warning message box
st.error(body, icon=None)	Error message box
st.exception(exception)	Display exception traceback
1.10 Execution Flow (4 components)
Component	Description
@st.dialog(title)	Modal dialog decorator
@st.fragment(run_every=None)	Fragment decorator for partial reruns
st.rerun(scope="app")	Rerun script
st.stop()	Stop execution immediately
1.11 Configuration & Utilities
Component	Description
st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="auto")	Page configuration
st.secrets	Access secrets.toml
st.cache_data(ttl=None, max_entries=None)	Cache data decorator
st.cache_resource(ttl=None, max_entries=None)	Cache resources decorator
st.connection(name, type=None)	Database connection manager
st.navigation(pages, position="sidebar", expanded=False)	Multipage navigation
st.Page(page, *, title=None, icon=None, url_path=None, default=False)	Page definition
st.context	Access request context
2. LAYOUT AND CONTAINERS (Detailed)
2.1 Columns
col1, col2 = st.columns([0.7, 0.3])  # Ratio widths
col1, col2, col3 = st.columns(3, gap="large", vertical_alignment="center", border=True)
Parameters: spec (int or list of floats), gap (spacing), vertical_alignment ("top"/"center"/"bottom"), border (bool)
Returns list of container objects
2.2 Container
c = st.container(border=True, key="my_container", height=300, horizontal=True)
with c:
    st.write("Content")
Key features: Border, fixed height (scrolling), horizontal flex layout, alignment options
Can insert elements out of order
2.3 Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"], default="Tab 2")
with tab1:
    st.write("Content")
Tab labels support Markdown
Default tab selection available
2.4 Expander
with st.expander("See more", expanded=True, icon="🔍"):
    st.write("Hidden content")
Collapsible content sections
Icon support
2.5 Popover
with st.popover("Settings", type="primary", help="Click for settings"):
    st.checkbox("Show completed")
Button-triggered overlay container
Width matches button width
2.6 Sidebar
st.sidebar.selectbox("Options", ["A", "B"])
# or
with st.sidebar:
    st.radio("Choose", ["A", "B"])
Not supported: st.echo, st.spinner, st.toast (use with notation)
2.7 Dialog
@st.dialog("Sign up", width="medium", dismissible=True)
def email_form():
    name = st.text_input("Name")
    if st.button("Submit"):
        st.rerun()
2.8 Form
with st.form("my_form", clear_on_submit=True, enter_to_submit=True):
    name = st.text_input("Name")
    submitted = st.form_submit_button("Submit")
2.9 Empty (Placeholder)
placeholder = st.empty()
placeholder.write("Initial")
placeholder.progress(50)  # Replaces previous content
3. DATA DISPLAY COMPONENTS (Detailed)
3.1 DataFrame
Interactive features: Sorting, column resizing, column reordering, search
Selection modes: on_select="ignore"/"rerun"/callable, selection_mode="multi-row"/"single-row"/"multi-column"/"single-column"/"multi-cell"/"single-cell"
Configuration: column_config, column_order, hide_index, row_height
Returns: Selection data dict when selection enabled
3.2 Data Editor
Edit modes: Inline editing with num_rows="fixed"/"dynamic"/"add"/"delete"
Column configuration: Disable specific columns, set data types
Callbacks: on_change for edit events
3.3 Column Configuration (17 Types)
Type	Description
st.column_config.Column	Generic column
st.column_config.TextColumn	Text with validation
st.column_config.NumberColumn	Numbers with formatting
st.column_config.CheckboxColumn	Boolean checkbox
st.column_config.SelectboxColumn	Dropdown selection
st.column_config.MultiselectColumn	Multi-selection
st.column_config.DatetimeColumn	DateTime formatting
st.column_config.DateColumn	Date formatting
st.column_config.TimeColumn	Time formatting
st.column_config.JSONColumn	JSON display
st.column_config.ListColumn	List display
st.column_config.LinkColumn	Clickable links
st.column_config.ImageColumn	Image thumbnails
st.column_config.AreaChartColumn	Sparkline area chart
st.column_config.LineChartColumn	Sparkline line chart
st.column_config.BarChartColumn	Sparkline bar chart
st.column_config.ProgressColumn	Progress bars
3.4 Metric
Features: Delta indicator, sparkline charts, color customization
Chart types: line, bar, area
Delta colors: normal, inverse, off, or specific colors
3.5 Table
Static HTML table (non-interactive)
Good for small datasets
3.6 JSON
Pretty-printed JSON with syntax highlighting
Expandable/collapsible nodes
4. HTML/CSS SUPPORT
4.1 st.html()
st.html("<p>Raw HTML content</p>", unsafe_allow_javascript=False)
Accepts: HTML strings, file paths, objects with _repr_html_()
CSS files automatically wrapped in <style> tags
JavaScript execution controlled by unsafe_allow_javascript
4.2 st.markdown()
st.markdown("""
    :red[Colored text] 
    :blue-background[Highlighted]
    :green-badge[Badge]
    :small[Small text]
""", unsafe_allow_html=False)
Markdown features: Standard GFM, emoji shortcodes, Material icons (:material/icon_name:)
Color directives: :color[text], :color-background[text], :color-badge[text]
Colors supported: red, orange, yellow, green, blue, violet, gray/grey, rainbow, primary
HTML support: unsafe_allow_html=True to render HTML
4.3 Custom CSS Injection
st.markdown("""
    <style>
    .custom-class { color: red; }
    </style>
""", unsafe_allow_html=True)
4.4 Container Styling
Containers with key parameter get CSS class st-key-{key}
Allows targeted CSS styling
5. STATE MANAGEMENT
5.1 Session State
# Initialize
if 'key' not in st.session_state:
    st.session_state.key = 'value'

# Access (dict or attribute style)
value = st.session_state['key']
value = st.session_state.key

# Update
st.session_state.key = 'new_value'

# Widget binding
st.slider("Value", 0, 100, key="slider_key")
5.2 Callbacks
def callback(arg1, kwarg1=None):
    st.session_state.count += 1

st.button("Click", on_click=callback, args=(arg1,), kwargs={"kwarg1": "value"})
5.3 Query Parameters
# Access
params = st.query_params  # Dict-like object
value = st.query_params.get("key")

# Set
st.query_params["key"] = "value"
st.query_params.key = "value"
5.4 Caching
@st.cache_data(ttl=3600, max_entries=100)
def load_data(url):
    return pd.read_csv(url)

@st.cache_resource
def get_model():
    return load_model()
st.cache_data: For serializable data (DataFrames, arrays, strings)
st.cache_resource: For unserializable resources (models, DB connections)
6. CUSTOM COMPONENTS
6.1 Using Third-Party Components
Popular community components:

streamlit-elements: Draggable dashboard (MUI-based)
streamlit-aggrid: Advanced data grid
streamlit-folium: Interactive maps
streamlit-echarts: Apache ECharts
streamlit-drawable-canvas: Sketching canvas
streamlit-tags: Tag input
stqdm: Progress bars for loops
6.2 Creating Custom Components
import streamlit.components.v1 as components

# HTML component
components.html("<div>Custom HTML</div>", height=200)

# IFrame component
components.iframe("https://example.com", height=500)
6.3 Component Architecture
Components are bidirectional:

Frontend: TypeScript/React code
Backend: Python wrapper
Communication: WebSocket between frontend and Python
7. PERFORMANCE OPTIMIZATION
7.1 Caching Strategies
Decorator	Use Case	Data Types
@st.cache_data	Data transformations, API calls, DB queries	Serializable (DataFrame, dict, list)
@st.cache_resource	ML models, DB connections	Unserializable objects
Cache parameters:

ttl: Time-to-live in seconds
max_entries: Maximum cached items
persist: Disk persistence option
7.2 Fragment Reruns
@st.fragment(run_every="10s")
def auto_refresh():
    df = get_data()
    st.line_chart(df)
Only reruns the function, not the entire app
Supports periodic auto-refresh with run_every
7.3 Forms
Batch widget changes into single rerun
Reduces unnecessary script runs
7.4 Pagination Patterns
# Manual pagination
page_size = 20
page = st.number_input("Page", 1, total_pages)
offset = (page - 1) * page_size
display_data = df.iloc[offset:offset + page_size]
st.dataframe(display_data)
7.5 Lazy Loading
@st.cache_data
def expensive_computation():
    # Slow operation
    return result
8. JAVASCRIPT INTEGRATION
8.1 streamlit.components.v1
import streamlit.components.v1 as components

# Raw HTML with optional JS
components.html("""
    <script>
        console.log("Hello from JS");
    </script>
    <div id="custom">Content</div>
""", height=200)

# IFrame embedding
components.iframe("https://example.com", height=500, scrolling=True)
8.2 HTML with JavaScript
st.html("""
    <button onclick="alert('Clicked')">Click me</button>
""", unsafe_allow_javascript=True)  # Use with caution
8.3 Component Communication
Custom components use Streamlit.setComponentValue() for bidirectional communication
Events flow from frontend to Python via WebSocket
9. TOOLTIP/POPOVER FEATURES
9.1 Widget Tooltips (help parameter)
Most widgets support a help parameter:

st.text_input("Name", help="Enter your full name")
st.button("Submit", help="Click to save changes")
st.metric("Revenue", "$1M", help="Annual recurring revenue")
9.2 Popover Container
with st.popover("Settings", help="Click to configure"):
    st.checkbox("Enable notifications")
    st.slider("Update frequency", 1, 60)
Button-triggered overlay
Supports any Streamlit content inside
9.3 Tooltip Content
Supports GitHub-flavored Markdown
Can include emoji and Material icons
Displayed on hover
10. LINK HANDLING
10.1 External Links
# Link button
st.link_button("Go to Google", "https://google.com", type="primary", icon="🔗")

# Markdown link
st.markdown("[Click here](https://google.com)")

# HTML link
st.html('<a href="https://google.com" target="_blank">Open</a>')
10.2 Page Navigation (Multipage Apps)
# Page link widget
st.page_link("app.py", label="Home", icon="🏠")
st.page_link("pages/profile.py", label="My Profile")

# Navigation setup
pages = {
    "Your account": [st.Page("create_account.py", title="Create")],
    "Resources": [st.Page("learn.py", title="Learn")]
}
pg = st.navigation(pages, position="sidebar")
pg.run()
10.3 Programmatic Navigation
# Rerun current page
st.rerun()

# Switch page (deprecated in favor of st.navigation)
st.switch_page("pages/other.py")
10.4 Query Parameter Navigation
# Set URL parameters
st.query_params["page"] = "profile"
st.query_params["id"] = "123"
# URL becomes: /?page=profile&id=123
SUMMARY OF KEY CAPABILITIES
Category	Count	Highlights
Total Components	80+	Comprehensive UI toolkit
Input Widgets	25+	All common form controls + advanced (camera, audio, chat)
Layout Options	11	Columns, tabs, expanders, popovers, dialogs
Data Display	6 + 17 column types	Interactive tables, metrics, sparklines
Charts	10 native + 6 library	Native simple charts + full library support
Text Elements	13	Full Markdown support with color directives
Status Elements	11	Progress, spinners, toasts, animations
State Management	4	Session state, callbacks, query params, caching
This comprehensive analysis covers every major feature and component available in Streamlit's API as of the current documentation.

Streamlit GitHub Repository - Comprehensive Analysis Report
Executive Summary
The Streamlit repository is a mature, well-organized open-source project with 43.5k stars, 4.1k forks, and 321 contributors. It's primarily written in Python (59.5%) and TypeScript (39.9%), with a sophisticated monorepo structure for its frontend architecture.

1. Repository Structure
Main Directories
Directory	Purpose
frontend/	Frontend monorepo with React/TypeScript packages
lib/	Python Streamlit library source code
component-lib/	npm package for creating custom components
proto/	Protocol Buffer definitions for Python/JS communication
e2e_playwright/	End-to-end tests using Playwright
scripts/	Build and utility scripts
specs/	Specification documents
wiki/	Project wiki content
.github/	GitHub Actions, issue templates, workflows
Key Configuration Files
pyproject.toml - Python package configuration
Makefile - Build automation
CONTRIBUTING.md - Comprehensive contribution guidelines
AGENTS.md / CLAUDE.md - AI agent development guidelines
2. Frontend Architecture
Technology Stack
Framework: React 18+ with TypeScript
Build Tool: Vite (for lib package)
Package Manager: Yarn (with workspaces)
Testing: Vitest (unit tests), Playwright (e2e)
Styling: Emotion (CSS-in-JS), styled-components
UI Library: Base Web (Uber's design system)
Monorepo Structure (frontend/)
frontend/
├── app/                    # Streamlit app shell/layout
├── component-v2-lib/       # New custom components v2 system
├── connection/             # WebSocket connection handling
├── lib/                    # Core component library
│   └── src/
│       ├── components/     # React components
│       │   ├── ChatInput/
│       │   ├── audio/
│       │   ├── core/       # Core UI components
│       │   ├── elements/   # Display elements
│       │   ├── shared/     # Shared utilities
│       │   └── widgets/    # Interactive widgets
│       ├── dataframes/     # DataFrame handling
│       ├── hooks/          # React hooks
│       ├── hostComm/       # Host communication
│       ├── render-tree/    # Render tree management
│       ├── theme/          # Theming system
│       └── util/           # Utilities
├── protobuf/               # Generated protobuf code
├── typescript-config/      # Shared TS configurations
└── utils/                  # Shared utilities
Dependency Architecture
The frontend uses a well-defined dependency graph:

app → lib (side-loads), connection, protobuf, utils
lib → protobuf, utils
connection → protobuf, utils
3. Component System
Component Organization
Components are organized into clear categories:

Category	Location	Examples
Core	components/core/	App layout, header, sidebar
Elements	components/elements/	Text, markdown, images, charts
Widgets	components/widgets/	Buttons, sliders, inputs
Shared	components/shared/	Common UI primitives
DataFrames	dataframes/	Table rendering
Component Implementation Pattern
Each component typically follows this structure:

// Component with TypeScript interface
interface Props {
  element: ElementProto;
  width: number;
  // ... widget-specific props
}

// Uses Emotion for styling
const StyledComponent = styled.div`
  // CSS-in-JS styles
`;

// Integrates with theme system
const theme = useTheme();
Key Component Files Found
ChatInput - New chat input component (v1.54+)
Audio - Audio player component
DataFrames - Complex table/data rendering
Core Components - App layout, sidebar, header
4. Example Apps and Demos
Built-in Examples
The repository doesn't contain extensive example apps directly, but includes:

streamlit hello - The built-in demo app showcasing features
e2e_playwright/ - Contains test apps that serve as examples
Documentation - Points to external template repos
External Resources Referenced
Component Template Repo: https://github.com/streamlit/component-template
Gallery: https://streamlit.io/gallery
5. Custom Component Examples
Two Generations of Custom Components
Component v1 (component-lib/)
Located in component-lib/
Traditional iframe-based custom components
Published as npm package: streamlit-component-lib
Uses React class components pattern
Component v2 (frontend/component-v2-lib/)
Newer system for custom components
Better performance and integration
Supports bytes in dictionaries (Issue #13671)
More modern React patterns
Creating Custom Components
From the documentation:

# Use the official template
git clone https://github.com/streamlit/component-template
The component-lib/src/ contains the support code for:

Component registration
Message passing between Python and React
TypeScript types for component props
Streamlit communication API
6. CSS/Styling Capabilities
Theming System Architecture
The theming system is sophisticated and located in frontend/lib/src/theme/:

Theme Structure
theme/
├── emotionBaseTheme/      # Base theme configuration
├── emotionDarkTheme/      # Dark theme variant
├── emotionLightTheme/     # Light theme variant
├── primitives/            # Design tokens
├── baseui.ts             # Base Web UI integration
├── createBaseUiTheme.ts  # Theme factory
├── getColors.ts          # Color utilities
├── getShadows.ts         # Shadow utilities
├── globalStyles.ts       # Global CSS
├── namedColors.ts        # Named color palette
├── themeConfigs.ts       # Theme configurations
├── types.ts              # TypeScript definitions
└── utils.ts              # Theme utilities
Design Tokens (Primitives)
Colors: Primary, secondary, success, warning, error, info
Typography: Font families, sizes, weights
Spacing: Consistent spacing scale
Shadows: Elevation system
Breakpoints: Responsive breakpoints
Styling Technologies Used
Technology	Purpose
Emotion	Primary CSS-in-JS solution
styled-components	Alternative CSS-in-JS
Base Web	Uber's component library
ThemeProvider	React context for theming
Custom Styling Capabilities
Theme Configuration (via config.toml):
[
theme
]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
Inline Styles via st.markdown() with HTML/CSS

Custom Components - Full control over styling

7. Hidden/Undocumented Features
Experimental Features Found
1. ASGI/Starlette Support (Issue #13600)
Experimental in Streamlit 1.53+
Allows mounting Streamlit as ASGI app
Enables custom middleware, routing
Request for feedback status
2. Component v2 System
Newer than documented custom components
Better performance than iframe-based v1
Located in frontend/component-v2-lib/
3. App Testing Framework (AppTest)
Python-based testing framework
Located in lib/
Issue #13909 mentions "src layout" support issues
4. Fragment Decorator (@st.fragment)
Partial reruns for performance
Works with cache_resource
Mentioned in Issue #13634
5. hostComm System
Located in frontend/lib/src/hostComm/
Communication layer between Streamlit and host
Enables embedding scenarios
6. AI Agent Development Support
.claude/, .codex/, .cursor/ directories
AGENTS.md files throughout repo
Optimized for AI-assisted development
7. Undocumented Theme Customization
More theme options than documented
Check theme/primitives/ for full token set
Custom color scales in namedColors.ts
8. Widget State Manager
WidgetStateManager.ts - Handles widget state
Supports complex widget interactions
Session state management
8. Issue Tracker Insights
Current Statistics
1,143 open issues
175 open pull requests
115 releases (latest: 1.54.0, Feb 4, 2026)
Common Issue Categories
Layout/Container Issues
Issue	Description
#13785	st.metric with chart_data wraps unexpectedly
#6004	st.tabs: know and control state (long-standing)
#13633	st.popover with st.date_input dropdown conflict
Custom Components
Issue	Description
#13671	Allow bytes in dict for custom components v2
#13635	AI agent deployment to Community Cloud
Feature Requests (Layout/UI)
st.chat_input extensions - Support embedded controls (#13601)
st.badge type parameter - Different visual styles (#13908)
st.markdown anchors=False - Disable header anchors (#13913)
Widget localStorage binding - Persist widget values (#13609)
Known Bugs
Query params + back button (#13853)
Fragments + cache_resource interactions (#13634)
Data editor + column operations (#13915)
Priority Labels Found
priority:P2 - Medium-high priority (fix within one month)
priority:P3 - Medium priority
status:confirmed - Confirmed by team
status:needs-triage - Not yet reviewed
type:regression - Regression from previous version
Popular Long-standing Requests
Custom HTTP requests (#439) - Open since 2019, 74 comments
Tab state control (#6004) - Open since 2023, 45 comments
Experimental ASGI support - Recently added in 1.53
Key Takeaways for Custom UI Development
Use Custom Components v2 for best performance and modern React patterns

Leverage the Theme System - Extensive design tokens available via Emotion

Consider the New Component Template - Reference component-template repo

Watch Experimental Features - ASGI support could enable new architectures

Test with Playwright - The e2e tests show best practices for testing Streamlit apps

Use TypeScript - Full type definitions available in component-lib

Follow the Monorepo Pattern - For large custom component projects

Resources for Further Exploration
Main Repo: https://github.com/streamlit/streamlit
Component Template: https://github.com/streamlit/component-template
Documentation: https://docs.streamlit.io
Component Gallery: https://streamlit.io/components
Community Forum: https://discuss.streamlit.io

COMPREHENSIVE ANALYSIS: Streamlit Agent Skills Repository
Repository Overview
URL: https://github.com/streamlit/agent-skills
Main Skill: developing-with-streamlit (parent skill with 16 specialized sub-skills)

1. ALL AVAILABLE SKILLS (16 Total)
#	Skill Name	Purpose
1	building-streamlit-chat-ui	Chat interfaces, chatbots, AI assistants, streaming responses
2	building-streamlit-dashboards	KPI cards, metrics, dashboard layouts, bordered cards
3	building-streamlit-multipage-apps	Multi-page app structure and navigation
4	choosing-streamlit-selection-widgets	Choosing between selectbox, radio, segmented control, pills, multiselect
5	connecting-streamlit-to-snowflake	Snowflake connections, queries, Cortex chat
6	creating-streamlit-themes	Theme configuration, colors, fonts, light/dark modes
7	displaying-streamlit-data	Dataframes, column config, charts, sparklines
8	improving-streamlit-design	Icons, badges, spacing, text styling, visual polish
9	optimizing-streamlit-performance	Caching, fragments, forms, static vs dynamic widgets
10	organizing-streamlit-code	Separating UI from business logic, modules
11	setting-up-streamlit-environment	Python environment setup with uv
12	using-streamlit-cli	CLI commands, running apps
13	using-streamlit-custom-components	Third-party components from the community
14	using-streamlit-layouts	Sidebar, columns, containers, dialogs, popovers
15	using-streamlit-markdown	Colored text, badges, icons, LaTeX, markdown features
16	using-streamlit-session-state	Session state, widget keys, callbacks
2. UI/UX PATTERNS
Page Configuration
st.set_page_config(
    page_title="My Dashboard",
    page_icon=":material/analytics:",  # Material icon
    layout="wide",  # or "centered" (default)
)
Logo Display
st.logo("logo.png")  # Adds logo to sidebar/header
Badge Patterns
# Standalone badges
st.badge("Active", icon=":material/check:", color="green")
st.badge("Pending", icon=":material/schedule:", color="orange")
st.badge("Deprecated", color="red")

# Inline badges in markdown
st.markdown(":green-badge[Active] :orange-badge[Pending] :red-badge[Deprecated]")
Icon System (Material Icons)
# Format: :material/icon_name:
st.markdown(":material/settings:")
st.markdown(":material/calendar_today:")
st.markdown(":material/dashboard:")

# Popular icons by category:
# Navigation: home, arrow_back, menu, settings, search
# Actions: send, play_arrow, refresh, download, upload, save, delete, edit
# Status: check_circle, error, warning, info, pending
# Data: table_chart, bar_chart, analytics, query_stats, database
Text Styling Patterns
# Sentence casing (preferred over Title Case)
st.title("Upload your data")  # GOOD
st.title("Upload Your Data")  # BAD

# Caption over info for lightweight text
st.caption("Data last updated 5 minutes ago")  # GOOD
st.info("Data last updated 5 minutes ago")  # BAD - too heavy

# Text alignment
st.title("Centered title", text_alignment="center")
st.write("Right aligned", text_alignment="right")

# Small text
st.markdown(":small[footnote text]")
Callouts with Icons
st.info("Processing complete", icon=":material/check_circle:")
st.warning("Rate limit approaching", icon=":material/warning:")
st.error("Connection failed", icon=":material/error:")
st.success("Saved!", icon=":material/thumb_up:")
3. DATA VISUALIZATION SKILLS
Native Charts (Preferred for Simple Cases)
st.line_chart(df, x="date", y="revenue")
st.bar_chart(df, x="category", y="count")
st.scatter_chart(df, x="age", y="salary")
st.area_chart(df, x="date", y="value")
Altair for Complex Charts
import altair as alt

chart = alt.Chart(df).mark_line().encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("revenue:Q", title="Revenue ($)"),
    color="region:N"
)
st.altair_chart(chart)
Dataframe Column Configuration
st.dataframe(
    df,
    column_config={
        "revenue": st.column_config.NumberColumn(
            "Revenue",
            format="$%.2f"
        ),
        "completion": st.column_config.ProgressColumn(
            "Progress",
            min_value=0,
            max_value=100
        ),
        "url": st.column_config.LinkColumn("Website"),
        "logo": st.column_config.ImageColumn("Logo"),
        "created_at": st.column_config.DatetimeColumn(
            "Created",
            format="MMM DD, YYYY"
        ),
        "sparkline": st.column_config.LineChartColumn("Trend"),
        "internal_id": None,  # Hide column
    },
    hide_index=True,
)
Available Column Types
AreaChartColumn - Area sparklines
BarChartColumn - Bar sparklines
CheckboxColumn - Boolean as checkbox
DateColumn - Date only
DatetimeColumn - Dates with formatting
ImageColumn - Images
JSONColumn - JSON objects
LineChartColumn - Sparkline charts
LinkColumn - Clickable links
ListColumn - Display lists/arrays
MultiselectColumn - Multi-value selection
NumberColumn - Numbers with formatting
ProgressColumn - Progress bars
SelectboxColumn - Editable dropdown
TextColumn - Text with formatting
TimeColumn - Time only
Metrics with Sparklines
weekly_values = [700, 720, 715, 740, 762, 755, 780]

st.metric(
    "Active Users",
    "780k",
    "+3.2%",
    border=True,
    chart_data=weekly_values,
    chart_type="line",  # or "bar"
)
4. LAYOUT SKILLS
Container Patterns
# Bordered container (card style)
with st.container(border=True):
    st.subheader("Section title")
    st.write("Grouped content")

# Horizontal container for button groups
with st.container(horizontal=True):
    st.button("Cancel")
    st.button("Save")
    st.button("Submit")

# Horizontal alignment options
with st.container(horizontal_alignment="center"):
    st.image("logo.png", width=200)
    st.title("Welcome")

with st.container(horizontal_alignment="right"):
    st.button("Settings", icon=":material/settings:")

with st.container(horizontal=True, horizontal_alignment="distribute"):
    st.button("Cancel")
    st.button("Save")
Column Layout
# Basic columns (max 4 recommended)
col1, col2 = st.columns(2)

# Custom width ratios
col1, col2 = st.columns([2, 1])  # 2:1 ratio

# With vertical alignment
cols = st.columns(4, vertical_alignment="center")

# Equal height columns with stretch
cols = st.columns(2)
with cols[0].container(border=True, height="stretch"):
    st.line_chart(data)
with cols[1].container(border=True, height="stretch"):
    st.dataframe(df)
Tabs
tab1, tab2 = st.tabs(["Chart", "Data"])

with tab1:
    st.line_chart(data)
with tab2:
    st.dataframe(df)
Expander (Collapsible Sections)
with st.expander("See details"):
    st.write("Hidden content")
    st.code("print('hello')")

# With icon
with st.expander("Settings", icon=":material/settings:"):
    st.write("Configure preferences")
Popover (Click to Reveal)
with st.popover("Settings"):
    st.checkbox("Dark mode")
    st.slider("Font size", 10, 24)
Dialogs (Modals)
@st.dialog("Confirm deletion")
def confirm_delete(item_name):
    st.write(f"Are you sure you want to delete **{item_name}**?")
    if st.button("Delete", type="primary"):
        delete_item(item_name)
        st.rerun()

if st.button("Delete item"):
    confirm_delete("My Document")
Spacing
# Container gap control
with st.container(gap=None, border=True):  # Remove spacing
    for item in items:
        st.checkbox(item.text)

with st.container(gap="small"):  # Explicit gap sizes

# Vertical space
st.space("small")   # Small gap
st.space("medium")  # Medium gap
st.space("large")   # Large gap
st.space(50)        # Custom pixels
Width and Height Control
# Stretch to fill
st.container(height="stretch")

# Shrink to content
st.container(width="content")

# Fixed sizes
st.container(height=300)
5. INTERACTIVE COMPONENTS
Selection Widgets
# Segmented control (2-5 options, single select)
status = st.segmented_control("Status", ["Draft", "Published"])

# Pills (2-5 options, multi-select)
selected = st.pills(
    "Tags",
    ["Python", "SQL", "dbt", "Streamlit"],
    selection_mode="multi"
)

# Selectbox (many options, single select)
country = st.selectbox("Country", ["USA", "UK", "Canada", ...])

# Multiselect (many options, multi-select)
countries = st.multiselect("Countries", ["USA", "UK", ...])

# With custom options allowed
tickers = st.multiselect(
    "Stock tickers",
    options=["AAPL", "MSFT"],
    accept_new_options=True
)
Toggle vs Checkbox
# Toggle for app settings
dark_mode = st.toggle("Dark mode")
show_advanced = st.toggle("Show advanced options")

# Checkbox for forms
with st.form("signup"):
    agree = st.checkbox("I agree to the terms")
    st.form_submit_button("Sign up")
Forms
# Standard form
with st.form("user_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["Admin", "User"])
    submitted = st.form_submit_button("Submit")

if submitted:
    save_user(name, email, role)

# Inline form without border
with st.form("search", border=False):
    with st.container(horizontal=True):
        query = st.text_input("Search", label_visibility="collapsed")
        st.form_submit_button(":material/search:")
Empty Placeholder
placeholder = st.empty()

# Update the placeholder
placeholder.text("Loading...")
result = load_data()
placeholder.dataframe(result)

# Clear it
placeholder.empty()
Feedback Widget
with st.chat_message("assistant"):
    st.markdown(response)
    feedback = st.feedback("thumbs")  # or "stars", "faces"
    if feedback is not None:
        st.toast(f"Feedback received")
6. NEWS FEED / CARD LAYOUT EXAMPLES
KPI Card Row Pattern
# Horizontal containers for responsive metric rows
with st.container(horizontal=True):
    st.metric("Revenue", "$1.2M", "-7%", border=True)
    st.metric("Users", "762k", "+12%", border=True)
    st.metric("Orders", "1.4k", "+5%", border=True)
Dashboard Card Layout
# KPI row
with st.container(horizontal=True):
    st.metric("Revenue", "$1.2M", "-7%", border=True, 
              chart_data=rev_trend, chart_type="line")
    st.metric("Users", "762k", "+12%", border=True,
              chart_data=user_trend, chart_type="line")

# Charts row
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.subheader("Revenue by Region")
        st.bar_chart(region_data, x="region", y="revenue")

with col2:
    with st.container(border=True):
        st.subheader("Monthly Trend")
        st.line_chart(monthly_data, x="month", y="value")

# Data table card
with st.container(border=True):
    st.subheader("Recent Orders")
    st.dataframe(orders_df, hide_index=True)
Card with Label Pattern
# With subheader
with st.container(border=True):
    st.subheader("Monthly Trends")
    st.line_chart(data)

# With bold label
with st.container(border=True):
    st.markdown("**Top Products**")
    st.dataframe(top_products)
Sidebar Filters Pattern
with st.sidebar:
    date_range = st.date_input("Date range", value=(start, end))
    region = st.multiselect("Region", regions, default=regions)
    st.caption("App v1.2.3")

# Main area is all dashboard content
7. CSS/HTML INJECTION PATTERNS
HTML (Use Very Sparingly!)
# Mix Markdown with HTML
st.markdown(
    "**Status:** <span style='color: coral'>Custom styled</span>", 
    unsafe_allow_html=True
)

# Pure HTML without markdown processing
st.html("<div class='custom'>Pure HTML content</div>")
Theme Configuration (Preferred over CSS)
# .streamlit/config.toml
[
theme
]
primaryColor = "#0969da"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f6f8fa"
textColor = "#1F2328"
font = "Inter:https://fonts.google.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"

# Border and radius
baseRadius = "8px"
buttonRadius = "8px"
showWidgetBorder = true

# Sidebar customization
[
theme.sidebar
]
backgroundColor = "#f6f8fa"
secondaryBackgroundColor = "#eaeef2"
Color Palette in Theme
[
theme
]
redColor = "#cf222e"
orangeColor = "#bf8700"
yellowColor = "#dbab09"
greenColor = "#1a7f37"
blueColor = "#0969da"
violetColor = "#8250df"
grayColor = "#57606a"
Chart Colors
[
theme
]
chartCategoricalColors = ["#0969da", "#1a7f37", "#bf3989", "#8250df", "#cf222e"]
chartSequentialColors = ["#f0f6fc", "#c8e1ff", "#79c0ff", "#58a6ff", "#388bfd", "#1f6feb", "#1158c7", "#0d419d", "#0a3069", "#04244a"]
Typography
[
theme
]
font = "sans-serif"  # or "serif", "monospace"
headingFont = "Inter:https://fonts.google.com/css2?family=Inter:wght@600;700&display=swap"
codeFont = "'JetBrains Mono':https://fonts.google.com/css2?family=JetBrains+Mono:wght@400;500&display=swap"
baseFontSize = 14
headingFontSizes = ["32px", "24px", "20px", "16px", "14px", "12px"]
Custom Fonts (Self-hosted)
[[
theme.fontFaces
]]
family = "CustomFont"
url = "app/static/CustomFont-Regular.woff2"
weight = 400

[[
theme.fontFaces
]]
family = "CustomFont"
url = "app/static/CustomFont-Bold.woff2"
weight = 700

[
theme
]
font = "CustomFont"
8. NAVIGATION PATTERNS
Multi-page App Structure
streamlit_app.py      # Main entry point
app_pages/            # NOT "pages/" (conflicts with old API)
    home.py
    analytics.py
    settings.py
Navigation Setup
# streamlit_app.py
import streamlit as st

# Define navigation
page = st.navigation([
    st.Page("app_pages/home.py", title="Home", icon=":material/home:"),
    st.Page("app_pages/analytics.py", title="Analytics", icon=":material/bar_chart:"),
    st.Page("app_pages/settings.py", title="Settings", icon=":material/settings:"),
])

# Shared title
st.title(f"{page.icon} {page.title}")

page.run()
Top Navigation (Few pages: 3-7)
page = st.navigation([...], position="top")
Sidebar Navigation (Many pages or sections)
page = st.navigation({
    "Main": [
        st.Page("app_pages/home.py", title="Home"),
        st.Page("app_pages/analytics.py", title="Analytics"),
    ],
    "Admin": [
        st.Page("app_pages/settings.py", title="Settings"),
        st.Page("app_pages/users.py", title="Users"),
    ],
}, position="sidebar")
Ungrouped Pages
page = st.navigation({
    "": [  # Empty string for ungrouped
        st.Page("app_pages/home.py", title="Home"),
        st.Page("app_pages/about.py", title="About"),
    ],
    "Analytics": [
        st.Page("app_pages/dashboard.py", title="Dashboard"),
    ],
}, position="top")
Programmatic Navigation
# Navigate to another page
if st.button("Go to Settings"):
    st.switch_page("app_pages/settings.py")

# Navigation links
st.page_link("app_pages/home.py", label="Home", icon=":material/home:")
st.page_link("https://example.com", label="External", icon=":material/open_in_new:")
Conditional Pages
pages = [st.Page("app_pages/home.py", title="Home")]

if st.user.is_logged_in:
    pages.append(st.Page("app_pages/dashboard.py", title="Dashboard"))

if st.session_state.get("is_admin"):
    pages.append(st.Page("app_pages/admin.py", title="Admin"))

page = st.navigation(pages)
page.run()
ADDITIONAL KEY PATTERNS
Session State Management
# Initialize
st.session_state.setdefault("count", 0)

# Alternative check
if "count" not in st.session_state:
    st.session_state.count = 0

# Read
current = st.session_state.count

# Update
st.session_state.count += 1

# Widget-state association
name = st.text_input("Name", key="user_name")
# st.session_state.user_name contains the value
Caching Patterns
# For data
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

# For connections/resources
@st.cache_resource
def get_connection():
    return st.connection("snowflake")

# With TTL
@st.cache_data(ttl="5m")  # 5 minutes
def get_metrics():
    return api.fetch()

# Bounded cache
@st.cache_data(max_entries=100)
def get_user_data(user_id):
    return fetch_user(user_id)
Fragments for Performance
@st.fragment
def live_metrics():
    st.metric("Users", get_count())
    st.button("Refresh")

live_metrics()

# Auto-refresh
@st.fragment(run_every="30s")
def auto_refresh_metrics():
    st.metric("Users", get_count())
Markdown Colored Text Syntax
# Colored text
st.markdown(":red[Error] and :green[Success]")

# Colored background
st.markdown(":blue-background[Highlighted]")

# Inline badges
st.markdown(":green-badge[Active] :red-badge[Inactive]")

# Available colors: red, orange, yellow, green, blue, violet, gray/grey, rainbow, primary

# Small text
st.markdown(":small[footnote]")
LaTeX Support
# Inline math
st.markdown("The formula is $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$")

# Display math
st.markdown("""
$$
\\sum_{i=1}^{n} x_i = x_1 + x_2 + ... + x_n
$$
""")
SUMMARY
The Streamlit Agent Skills repository provides 16 comprehensive skills covering:

UI Components: Cards, metrics, badges, icons, containers
Layout Systems: Columns, horizontal containers, tabs, expanders, dialogs, popovers
Data Display: Native charts, Altair, dataframes with 16+ column types, sparklines
Navigation: Multi-page apps with top/sidebar nav, programmatic navigation
Theming: Complete theme configuration via config.toml (avoiding CSS)
Performance: Caching, fragments, forms, conditional rendering
State Management: Session state, callbacks, widget keys
Chat UI: Full chat interface patterns with streaming
Selection Widgets: Modern patterns (segmented control, pills) vs legacy (radio)
Custom Components: Third-party extensions when core isn't enough

Streamlit Custom Components - Comprehensive Analysis Report
Executive Summary
Based on my analysis of the Streamlit Component Template repository and related documentation, here's a detailed breakdown to help determine whether custom components are needed for your Research Portal's tooltips/hover effects.

1. Template Structure - How to Create a Custom Component
Two API Versions
Version	Python API	Frontend Library	Status
v2 (Recommended)	st.components.v2.component()	@streamlit/component-v2-lib	Modern, actively maintained
v1 (Legacy)	streamlit.components.v1.declare_component()	streamlit-component-lib	Still supported
Directory Structure (v2 Template)
my_component/                          # Python package
├── __init__.py                        # Component declaration & wrapper
├── example.py                         # Example usage
└── frontend/                          # Frontend code
    ├── package.json                   # NPM dependencies
    ├── tsconfig.json                  # TypeScript config
    ├── vite.config.ts                 # Build configuration
    └── src/
        ├── index.tsx                  # Entry point (renders React)
        ├── main.tsx                   # React root creation
        └── MyComponent.tsx            # React component implementation
Python Component Declaration (v2)
import streamlit as st

# Declare the component with st.components.v2.component()
out = st.components.v2.component(
    "streamlit-custom-component.my_component",  # Unique component name
    js="index-*.js",                             # Built JS file pattern
    html='<div class="react-root"></div>',       # Container HTML
)

def my_component(name, key=None):
    """Wrapper function with typed API"""
    component_value = out(
        name=name,
        key=key,
        default={"num_clicks": 0},      # Initial return value
        data={"name": name},            # Data sent to frontend
    )
    return component_value
2. Frontend Technologies
React Template (Recommended)
Tech Stack:

React 18 with TypeScript
Vite for build tooling (replaced Webpack)
ES Modules (modern JavaScript)
Key Dependencies:

{
  "@streamlit/component-v2-lib": "^0.2.0",
  "react": "^18.3.1",
  "react-dom": "^18.3.1"
}
Frontend Entry Point (index.tsx):

import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";

const MyComponentRoot: FrontendRenderer<MyComponentStateShape, MyComponentDataShape> = (args) => {
  const { data, parentElement, setStateValue } = args;
  
  // Access data from Python
  const { name } = data;
  
  // Render React component
  const rootElement = parentElement.querySelector(".react-root");
  // ... React rendering logic
  
  // Send data back to Python
  setStateValue("num_clicks", newValue);
  
  // Cleanup function
  return () => { /* unmount logic */ };
};
React-less Template (TypeScript-only)
For vanilla JavaScript/TypeScript without React:

More boilerplate code required
Manual event listener setup
Manual DOM manipulation
Use when you want minimal bundle size or no React
3. Bi-Directional Communication
Python → Frontend
Data Flow:

# Python sends data via named arguments
result = my_component(
    greeting="Hello",
    name="Streamlit",
    data={"custom": "data"}
)
Frontend receives:

const { data, parentElement, setStateValue } = args;
const { name, greeting } = data;  // "Streamlit", "Hello"
Supported Data Types:

Python Type	JavaScript Type
JSON-serializable data	JavaScript equivalent
numpy.array	ArrowTable
pandas.DataFrame	ArrowTable
dict, list, str, int, float, bool	Native JS types
Frontend → Python
Key API: setStateValue()

// In React component
const onClicked = useCallback((): void => {
    const newNumClicks = numClicks + 1;
    setNumClicks(newNumClicks);
    
    // Send back to Python - triggers script re-run
    setStateValue("num_clicks", newNumClicks);
}, [numClicks, setStateValue]);
Important Pattern:

Calling setStateValue() triggers a full Streamlit script re-run
The component's return value will be the new state on next run
This is asynchronous - the "sleight of hand" makes it appear synchronous
Communication Lifecycle
1. Python: my_component(data=x) 
   ↓ (data serialized, sent to iframe)
2. Frontend: receives via args.data
   ↓ (user interaction)
3. Frontend: setStateValue(key, value)
   ↓ (value sent to Python)
4. Python: script re-executes
   ↓
5. Python: my_component() returns new value
4. Build Process
Development Workflow
Terminal 1 - Frontend Dev Server:

cd my_component/frontend
npm install           # Install dependencies
npm run dev          # Start Vite dev server with watch mode
Terminal 2 - Streamlit App:

cd my_component
pip install -e .     # Editable install
streamlit run example.py
Build Commands
Command	Purpose
npm run dev	Development with hot reload
npm run build	Production build
npm run typecheck	TypeScript validation
npm run clean	Remove build directory
Production Build (Vite Configuration)
// vite.config.ts
export default defineConfig(() => {
  return {
    base: "./",
    build: {
      minify: isDev ? false : "esbuild",
      outDir: "build",
      lib: {
        entry: "./src/index.tsx",
        name: "MyComponent",
        formats: ["es"],           // ES modules only
        fileName: "index-[hash]",  // Hashed filename for caching
      },
      esbuild: {
        drop: ["console", "debugger"],  // Remove in production
      },
    },
  };
});
Packaging for Distribution
# 1. Build frontend assets
cd my_component/frontend
npm run build

# 2. Build Python wheel
cd ../..
uv build

# Output: dist/streamlit_custom_component-0.0.1-py3-none-any.whl
5. Example Components in the Repository
Available Examples (v1 examples, adaptable to v2)
Example	Purpose	Key Features
CustomDataframe	Custom table rendering	DataFrame handling, ArrowTable
SelectableDataTable	Interactive tables	Row selection, click events
Various third-party	ECharts, AG-Grid, etc.	Chart integration
Real-World Community Components
Component	Use Case	GitHub
streamlit-echarts	Interactive charts	andfanilo/streamlit-echarts
streamlit-aggrid	Advanced data grids	Pozzitive/Streamlit-AgGrid
streamlit-option-menu	Navigation menus	victoris93/streamlit-option-menu
streamlit-lottie	Lottie animations	andfanilo/streamlit-lottie
6. Best Practices for Custom Components
Do's
✅ Create Wrapper Functions

def my_component(name: str, key: Optional[str] = None) -> Dict:
    """Documented, typed wrapper with validation."""
    if not name:
        raise ValueError("name is required")
    
    return out(
        name=name,
        key=key,
        default={"num_clicks": 0},
        data={"name": name},
    )
✅ Use TypeScript for type safety across Python/JS boundary

✅ Handle Cleanup in React components

return () => {
    reactRoot.unmount();
    reactRoots.delete(parentElement);
};
✅ Theme Integration - Use Streamlit's CSS variables

/* Automatic CSS variables from Streamlit theme */
color: var(--st-primary-color);
background: var(--st-background-color);
font-family: var(--st-font);
✅ Set Unique Keys when using multiple component instances

component1 = my_component(name="A", key="comp1")
component2 = my_component(name="B", key="comp2")
Don'ts
❌ Avoid Expensive Re-renders - Each setStateValue() triggers full app re-run

❌ Don't Send Large Data without pagination/virtualization

❌ Don't Block the Main Thread with heavy computations

7. When to Use Custom Components vs Native Streamlit
Decision Matrix
Use Case	Native Streamlit	Custom Component
Simple tooltips on buttons/inputs	✅ help= parameter	❌ Overkill
Custom hover effects on tables	⚠️ Limited	✅ Full CSS control
Complex interactive charts	⚠️ Limited	✅ D3, ECharts, etc.
Drag-and-drop interfaces	❌ Not available	✅ Implement in React
Real-time data visualization	⚠️ Limited	✅ WebSocket integration
Third-party JS library integration	❌ Not possible	✅ Wrap any library
Advanced data grids	⚠️ st.dataframe	✅ AG-Grid features
For Your Specific Case: Tooltips/Hover Effects
Option 1: Native Streamlit (Recommended for Basic Tooltips)
# Simple tooltips - native support since v0.79
st.button("Click me", help="This is a tooltip")
st.text_input("Label", help="Hover for more info")
st.metric("Revenue", "$1M", help="Year-over-year growth")
Limitations:

Basic text-only tooltips
No custom styling
No rich content (images, HTML)
Limited positioning control
Option 2: HTML/CSS with st.markdown (Good Middle Ground)
# Pure CSS/HTML tooltips without custom component
tooltip_html = """
<style>
.tooltip {
    position: relative;
    display: inline-block;
}
.tooltip .tooltiptext {
    visibility: hidden;
    background-color: black;
    color: #fff;
    text-align: center;
    padding: 5px;
    border-radius: 6px;
    position: absolute;
    z-index: 1;
}
.tooltip:hover .tooltiptext {
    visibility: visible;
}
</style>
<div class="tooltip">Hover over me
    <span class="tooltiptext">Tooltip text</span>
</div>
"""
st.markdown(tooltip_html, unsafe_allow_html=True)
Pros:

No build process
Works immediately
Custom styling
Cons:

Limited interactivity
No Python ↔ JavaScript communication
Manual state management
Option 3: Custom Component (For Advanced Needs)
When you need:

Complex hover interactions
Dynamic content loading on hover
Integration with external APIs
Custom visualization libraries
Bidirectional state sync
Recommendation for Research Portal
For Tooltips/Hover Effects in Your Use Case:
Feature	Recommended Approach
Simple text tooltips on metrics	Native help= parameter
Table cell tooltips	st.dataframe column config or HTML/CSS
Custom styled tooltips	HTML/CSS with st.markdown(unsafe_allow_html=True)
Interactive hover charts	Custom component with Plotly/D3
Complex hover interactions	Custom component
Verdict
For your Research Portal's tooltips and hover effects, custom components are likely overkill unless you need:

Complex interactive visualizations (custom D3 charts)
Real-time data on hover (API calls when hovering)
Highly customized tooltip UI (images, rich HTML, animations)
Third-party library integration (specialized charting libraries)
Suggested Approach
Start with native help= parameters for basic tooltips
Use HTML/CSS (st.markdown) for custom-styled static tooltips
Use Plotly's built-in hover for chart tooltips (already supported)
Consider custom components only if you need advanced interactivity beyond these options
If You Decide on Custom Components Later
The v2 template with React is well-designed and the build process is streamlined with Vite. The bi-directional communication is straightforward using setStateValue(). You would create a component for:

Advanced data table with custom cell hover
Interactive financial charts with drill-down
Custom UI widgets not available in Streamlit

Streamlit Documentation Repository Analysis Report
Executive Summary
I have thoroughly analyzed the Streamlit Documentation repository at https://github.com/streamlit/docs and the live documentation site at https://docs.streamlit.io/. Below is a comprehensive report of useful findings for building a professional newsroom UI.

1. Documentation Structure
Repository Organization
The documentation is organized as a Next.js application with the following structure:

docs/
├── content/                 # Main documentation content (Markdown files)
│   ├── get-started/         # Installation & fundamentals
│   ├── develop/             # API reference, concepts, tutorials
│   ├── deploy/              # Deployment guides
│   └── kb/                  # Knowledge base
├── components/              # React components for UI elements
├── styles/                  # SCSS/CSS stylesheets
├── pages/                   # Next.js page routing
├── lib/                     # Utility functions
├── public/                  # Static assets (images)
└── python/                  # Python code for API docstrings
Key Content Categories
Section	Purpose
Get Started	Installation, fundamentals, first steps tutorials
Develop	API reference, concepts, advanced tutorials
Deploy	Streamlit Community Cloud, Snowflake, other platforms
Knowledge Base	FAQ, troubleshooting, best practices
2. Code Examples & Patterns
Essential Streamlit Components for Newsroom UI
Text Elements (from API Reference)
import streamlit as st

# Headers and titles
st.title("The app title")
st.header("This is a header")
st.subheader("This is a subheader")

# Markdown support
st.markdown("Hello **world**!")
st.caption("Small caption text")

# Code display
st.code("a = 1234", language="python")

# Divider for visual separation
st.divider()

# Badges for labels/tags
st.badge("New")
Data Display Elements
# Interactive dataframe (perfect for news feeds)
st.dataframe(my_data_frame)

# Static table
st.table(my_data_frame)

# Metrics with delta indicators (great for stock data)
st.metric("Stock Price", "$142.50", "+2.5%")

# JSON display
st.json(my_dict)
Layout Components (Critical for Newsroom Layout)
# Columns for multi-column news layout
col1, col2 = st.columns(2)
col1.write("Main story")
col2.write("Sidebar stories")

# Tabs for categorized news
tab1, tab2 = st.tabs(["Breaking News", "Market Data"])

# Expander for additional content
with st.expander("Read more"):
    st.write("Full article content")

# Popover for quick previews
with st.popover("Quick view"):
    st.write("Summary content")

# Sidebar for navigation/filters
st.sidebar.write("Filters")
st.sidebar.selectbox("Category", ["All", "Business", "Tech"])

# Container for grouping elements
with st.container():
    st.write("Related articles")
Input Widgets (for Newsroom Filters)
# Search
search = st.text_input("Search articles")

# Category selection
category = st.selectbox("Category", ["All", "Business", "Tech", "Sports"])

# Multi-select for tags
tags = st.multiselect("Tags", ["Featured", "Trending", "Premium"])

# Date range
date_range = st.date_input("Date range", [])

# Pills for quick filtering
st.pills("Tags", ["Sports", "AI", "Politics"])

# Segmented control
st.segmented_control("Filter", ["Open", "Closed", "All"])
3. Component Demos & Live Examples
Third-Party Components Gallery
The documentation highlights several community components useful for newsroom UI:

Component	Purpose	Author
Streamlit Aggrid	Advanced data tables with sorting/filtering	@PablocFonseca
Streamlit Elements	Draggable/resizable dashboard layout	@okls
Annotated Text	Highlight important text segments	@tvst
Streamlit Extras	Collection of useful UI extras	@arnaudmiribel
Tags	Add tags/labels to articles	@gagan3012
Streamlit Option Menu	Professional navigation menu	@victoryhb
Stqdm	Progress bars for loading states	@Wirg
Example: AgGrid for Article Listing
from st_aggrid import AgGrid, GridOptionsBuilder

df = pd.DataFrame({
    'Headline': ['Market Rally Continues', 'Tech Earnings Beat'],
    'Category': ['Finance', 'Technology'],
    'Published': ['2 hours ago', '4 hours ago']
})

grid_return = AgGrid(df, editable=False, fit_columns_on_grid_load=True)
4. Tutorial Content
Available Step-by-Step Tutorials
Authentication and Personalization

User authentication with OpenID Connect
Personalized news feeds
Chat and LLM Apps

Building conversational interfaces
AI-powered news summarization
Configuration and Theming ⭐ HIGHLY RELEVANT

Custom fonts
Color schemes
Brand alignment
Connect to Data Sources

Database connections
API integrations
Elements & Layout

Dataframe configurations
Chart customizations
Multipage Apps

Navigation structures
Page organization
Execution Flow

Caching strategies
Performance optimization
5. Advanced Topics
Theming & Configuration (config.toml)
Location: .streamlit/config.toml

Color Customization
[
theme
]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
Font Customization (Advanced)
[
theme
]
# Base font settings
font = "sans-serif"
headingFont = "sans-serif"
codeFont = "monospace"

# Custom Google Fonts with fallbacks
font = "Nunito:https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000, sans-serif"
codeFont = "'Space Mono':https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap, monospace"

# Font sizes
baseFontSize = 16
codeFontSize = "0.875rem"

# Sidebar-specific fonts
[
theme.sidebar
]
font = "sans-serif"
headingFont = "sans-serif"
Custom Font Hosting (Self-hosted)
[
server
]
enableStaticServing = true

[[
theme.fontFaces
]]
family = "noto-sans"
url = "app/static/NotoSans-VariableFont_wdth,wght.ttf"
style = "normal"

[[
theme.fontFaces
]]
family = "noto-mono"
url = "app/static/NotoSansMono-VariableFont_wdth,wght.ttf"

[
theme
]
font = "noto-sans"
codeFont = "noto-mono"
Caching Strategies for News Data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_news_articles():
    return api.get_latest_news()

@st.cache_resource
def get_database_connection():
    return create_db_connection()
Session State for User Preferences
# Initialize session state
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "All"

# Use in widgets
st.selectbox("Category", ["All", "Business", "Tech"], 
             key='selected_category')
6. CSS/Styling Documentation Sources
Documentation Styles Directory (from GitHub)
The docs site itself uses these SCSS files:

File	Purpose
main.scss	Main stylesheet entry
globals.css	Global CSS variables
fonts.scss	Font definitions
text.scss	Typography styles
tables.scss	Table styling
admonition.scss	Callout boxes (notes, warnings)
syntax-highlighting.scss	Code block styling
scrollbars.scss	Custom scrollbar styling
print.scss	Print-specific styles
CSS-in-Streamlit via st.html() and st.markdown()
# Custom CSS injection
custom_css = """
<style>
    .news-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .headline {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    .timestamp {
        font-size: 0.875rem;
        color: #666;
    }
</style>
"""
st.html(custom_css)

# Or use with markdown
st.markdown(custom_css, unsafe_allow_html=True)
HTML Component for Complex UIs
from streamlit.components.v1 import html

html("""
<div class="news-container">
    <article class="featured">
        <h2>Breaking News</h2>
        <p>Article content...</p>
    </article>
</div>
""", height=400)
7. Hidden Gems & Useful Examples
1. st.write_stream for Live Updates
# Typewriter effect for breaking news
def news_stream():
    text = "Breaking: Markets rally as tech stocks surge..."
    for word in text.split():
        yield word + " "
        time.sleep(0.1)

st.write_stream(news_stream)
2. st.status for Loading States
with st.status("Fetching latest news...", expanded=True) as status:
    news = fetch_news()
    st.write("✓ Retrieved headlines")
    st.write("✓ Processed summaries")
    status.update(label="News updated!", state="complete")
3. st.toast for Notifications
st.toast('New articles available!', icon='📰')
4. st.html for Rich Content
# Embed external content
st.html("<p>Foo bar.</p>")
5. Query Parameters for Shareable URLs
# Get URL parameters
category = st.query_params.get("category", "all")

# Set URL parameters
st.query_params["category"] = selected_category
6. st.context for Browser Info
# Access browser cookies/headers
cookies = st.context.cookies
headers = st.context.headers
locale = st.context.locale
7. Column Configuration for Dataframes
import streamlit as st

st.column_config.NumberColumn(
    "Price (in USD)",
    min_value=0,
    format="$%d"
)

st.column_config.DatetimeColumn(
    "Published",
    format="MMM DD, YYYY"
)

st.column_config.LinkColumn(
    "Article URL"
)
8. st.fragment for Partial Updates
@st.fragment(run_every="10s")
def live_ticker():
    st.metric("S&P 500", "4,783.45", "+0.8%")
9. Modal Dialogs (st.dialog)
@st.dialog("Article Details")
def show_article(article):
    st.write(article['title'])
    st.write(article['content'])
    if st.button("Close"):
        st.rerun()
10. Custom Components (V2 API)
import streamlit.components.v2 as components

my_component = components.component(
    html="<button>Click me</button>",
    js="""
    function({ disabled, theme }) {
        return {
            render: (container, { disabled, theme }) => {
                container.innerHTML = html;
            }
        }
    }
    """
)
Recommendations for Professional Newsroom UI
Layout Structure
import streamlit as st

st.set_page_config(
    page_title="News Portal",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for navigation and filters
with st.sidebar:
    st.logo("logo.png")
    st.header("Filters")
    category = st.selectbox("Category", ["All", "Business", "Tech"])
    st.date_input("Date Range")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Breaking News")
    # Featured articles

with col2:
    st.subheader("Trending")
    # Sidebar stories
Performance Best Practices
Use @st.cache_data for API calls
Use @st.fragment for live updating components
Use st.session_state for user preferences
Enable enableStaticServing for custom assets
Use st.columns for responsive layouts
Theming for Professional Look
[
theme
]
primaryColor = "#d62e2f"  # Coresight red
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#323232"
font = "Inter, sans-serif"
baseFontSize = 16
This comprehensive analysis provides all the building blocks needed to create a professional newsroom UI with Streamlit, including layout patterns, theming options, component choices, and advanced features.

STEP 3 FINDINGS: STREAMLIT CAPABILITIES ANALYSIS
Key Components We'll Use
Feature	Streamlit Solution	Status
Custom HTML/CSS	st.markdown(unsafe_allow_html=True) + <style>	✅ Available
Clickable Links	Standard HTML <a href="...">	✅ Available
Hover Tooltips	CSS :hover + title attribute OR custom CSS tooltips	✅ Available
Date Formatting	Python datetime + strftime	✅ Available
Relative Time Calculation	JavaScript (browser time) - new Date()	✅ Via JS injection
Page Layout	st.container(), custom CSS max-width	✅ Available
Database Connection	Existing db_manager + SQLAlchemy	✅ Already implemented
For Tooltips on Tagged Companies
Since Streamlit's native help parameter only works on widgets (not on HTML links), we have two options:

Option A: CSS-only Tooltips (Recommended - Simpler)

<a href="#" class="ticker-link" title="Relevance: 100% | Sentiment: Bearish (-0.42)">MSFT</a>
Uses native browser tooltip via title attribute
Simple, no JavaScript needed
Limited styling but functional
Option B: Custom CSS Tooltips (Better looking)

<div class="tooltip">
  <a href="#" class="ticker-link">MSFT</a>
  <span class="tooltiptext">Relevance: 100%<br>Sentiment: Bearish (-0.42)</span>
</div>
Fully styled custom tooltip
Requires CSS for hover effects
More professional appearance



This is HUGE! I found game-changing features:

st.components.v2.component is MUCH more powerful than I thought! It allows:

Inline HTML, CSS, and JavaScript
Bi-directional communication between Python and JavaScript
setTriggerValue to send data from JS to Python
setStateValue to maintain state
Access to parentElement and DOM manipulation
DatetimeColumn with format="distance" gives relative time like "a few seconds ago", "2 hours ago" automatically!

This changes everything. I can now build:

Custom tooltips with full CSS and JavaScript
Precise pixel-perfect styling
Interactive hover effects
Accurate browser-based time calculation
Click handlers that communicate back to Python
Let me update my approach and start building in stages.


🎯 GAME CHANGER DISCOVERED!

I found powerful features I didn't know existed that solve my limitations:

✅ NEW CAPABILITIES DISCOVERED
Limitation	Solution Found	Impact
Relative time calculation	st.column_config.DatetimeColumn(format="distance") shows "2 hours ago" automatically	✅ Built-in!
Custom tooltips	st.components.v2.component with CSS + JS	✅ Full control!
Pixel-perfect styling	st.components.v2.component accepts inline CSS	✅ Exact styling!
JavaScript execution	st.components.v2.component with JS parameter	✅ Browser-time calculation!
Bidirectional Python↔JS	setTriggerValue, setStateValue	✅ Full interactivity!
🚀 REVISED APPROACH (Much Better!)
I will use st.components.v2.component - a powerful feature that allows:

Custom HTML/CSS/JavaScript in one component
Bidirectional communication between Python and JavaScript
Full styling control (pixel-perfect possible)
Interactive elements (click handlers, hover effects)
📋 BUILDING IN STAGES
Stage 1: Database & Models (No UI)
Create NewsArticle dataclass
Create NewsRepository with SQL queries
Test data retrieval
Stage 2: Basic News Card (HTML/CSS only)
Single news article display
Static styling matching Figma
Screenshot & compare
Stage 3: JavaScript Time Calculation
Add JS for browser-time relative calculation
Format: "(8 hours, 58 minutes ago)"
Screenshot & verify
Stage 4: Hover Tooltips
Custom CSS tooltips for tagged companies
Show: relevance_score, sentiment_label, sentiment_score
Screenshot & verify
Stage 5: Filters
Date calendar filter
Sector dropdown
Company dropdown
Last 7 days default
Stage 6: Full Integration
Combine everything
Full news feed
Final screenshot comparison
I am now 100% confident I can deliver pixel-perfect results.