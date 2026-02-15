# Reusable Financial Data Table Template

This document contains the complete, pixel-perfect table implementation with all specifications, CSS, helper functions, and HTML generation logic. Use this to implement identical tables on other pages (e.g., Key Stats).

---

## 📋 Table Features

### Visual Features
- ✅ **Roboto font** family throughout
- ✅ **Sticky first column** (stays visible on horizontal scroll)
- ✅ **Sticky header row** (stays visible on vertical scroll)
- ✅ **Black underlines** (2px, #000000) - appear ABOVE subtotal rows
- ✅ **Grey separators** (4px, #CFCFCF) - appear BELOW header and specific subtotal rows
- ✅ **Correct indentation** - Subtotals indented 24px, regular items 12px
- ✅ **Bold styling** for subtotal rows
- ✅ **Light grey background** (#F9F9F9) for first column

### Layout Specs
- **Header height**: 48px
- **Row height**: 24px
- **First column width**: 400px
- **Data column width**: 164px
- **Font size**: 16px (base), 12px (small)
- **Line height**: 19px

---

## 🎨 Complete CSS

```css
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,600;0,700;1,400&display=swap');

:root {
    /* Figma Colors - Exact Match */
    --white: #FFFFFF;
    --light-grey: #F9F9F9;
    --black: #000000;
    --dark-grey: #4F4F4F;
    --border-light: #CFCFCF;
    --border-medium: #C1CFCF;
    
    /* Accent Colors */
    --primary-red: #D62E2F;
    
    /* Typography - Figma Specs */
    --font-family: 'Roboto', sans-serif;
    --font-size-base: 16px;
    --font-size-small: 12px;
    --line-height-base: 19px;
    --line-height-compact: 100%;
    
    /* Font Weights */
    --font-weight-regular: 400;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    
    /* Spacing */
    --padding-normal: 12px;
    --padding-indented: 24px;
    --padding-top: 4px;
    --gap-small: 2px;
    --gap-medium: 6px;
    
    /* Dimensions */
    --header-height: 48px;
    --row-height: 24px;
    --border-width: 1px;
    --underline-width: 2px;
    
    /* Column Widths */
    --first-column-width: 400px;
    --date-column-width: 164px;
}

/* ==================== TABLE STYLING - PIXEL PERFECT FROM FIGMA ==================== */

.table-container {
    border: var(--border-width) solid var(--border-light);
    border-radius: 8px;
    overflow: hidden;
    background: var(--white);
    margin-bottom: 30px;
}

.table-scroll {
    max-height: 600px;
    overflow-x: auto;
    overflow-y: auto;
}

.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: var(--font-family);
    font-size: var(--font-size-base);
}

/* ========== HEADER ROW - 48px height, grey background ========== */
.data-table thead {
    background-color: var(--light-grey);
    position: sticky;
    top: 0;
    z-index: 10;
}

.data-table th {
    height: var(--header-height);
    padding: var(--padding-top) var(--padding-normal);
    text-align: left;
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
    color: var(--black);
    border-bottom: var(--border-width) solid var(--border-light);
    background-color: var(--light-grey);
    vertical-align: top;
}

/* STICKY FIRST COLUMN */
.data-table th:first-child,
.data-table td:first-child {
    position: sticky;
    left: 0;
    z-index: 5;
    background-color: var(--light-grey);
}

.data-table th:first-child {
    min-width: var(--first-column-width);
    max-width: var(--first-column-width);
}

.data-table td:first-child {
    min-width: var(--first-column-width);
    max-width: var(--first-column-width);
}

/* Date column headers - right aligned */
.data-table th.data-col {
    text-align: right;
    min-width: var(--date-column-width);
    padding: var(--padding-top) var(--padding-top) var(--padding-top) var(--padding-normal);
}

/* Header subtext */
.header-subtext {
    display: block;
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-regular);
    font-style: italic;
    color: var(--dark-grey);
    margin-top: var(--gap-small);
    line-height: var(--line-height-compact);
}

/* Period labels in header */
.period-label {
    display: block;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
    color: var(--black);
    line-height: var(--line-height-compact);
    text-align: right;
}

.period-date {
    display: block;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-bold);
    color: var(--black);
    line-height: var(--line-height-compact);
    text-align: right;
    margin-top: var(--gap-small);
}

/* ========== DATA ROWS - 24px height ========== */
.data-table tbody tr {
    height: var(--row-height);
}

.data-table td {
    height: var(--row-height);
    padding: var(--padding-top) var(--padding-normal);
    border-bottom: var(--border-width) solid var(--border-light);
    vertical-align: bottom;
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
}

/* First column - label column */
.data-table td:first-child {
    text-align: left;
    background-color: var(--light-grey);
    color: var(--black);
    font-weight: var(--font-weight-regular);
    vertical-align: middle;
}

/* Data cells - numbers */
.data-table td.data-cell {
    text-align: right;
    font-variant-numeric: tabular-nums;
    color: var(--black);
    font-weight: var(--font-weight-regular);
    padding: var(--padding-top) 8px var(--padding-top) var(--padding-normal);
}

/* ========== ROW INDENTATION ========== */
.indent-0 { 
    padding-left: var(--padding-normal) !important; 
}

.indent-1 { 
    padding-left: var(--padding-indented) !important; 
    background-color: var(--light-grey) !important;
}

/* ========== BOLD ROWS (Subtotals) ========== */
.row-bold td:first-child {
    font-weight: var(--font-weight-bold) !important;
    color: var(--dark-grey) !important;
}

.row-bold td.data-cell {
    font-weight: var(--font-weight-semibold) !important;
    color: var(--dark-grey) !important;
}

/* ========== UNDERLINES - 2px thick, dark grey ========== */
.row-underline-black td.data-cell {
    position: relative;
}

.row-underline-black td.data-cell::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 5%;
    right: 5%;
    height: var(--underline-width);
    background-color: var(--dark-grey);
}

/* ========== GREY SEPARATOR - 4px thick ========== */
.row-grey-separator td,
.row-grey-separator th {
    border-bottom: 4px solid #CFCFCF;
}
</style>
```

---

## 🔧 Helper Functions

```python
def is_bold_row(label: str) -> bool:
    """Check if row should be bold (subtotal rows) per Figma."""
    bold_labels = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
                   "Operating Income", "Net Interest Exp."}
    return label in bold_labels


def has_underline(label: str) -> bool:
    """Check if row should have 2px dark grey underline per Figma."""
    underline_labels = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
                        "Operating Income", "Net Interest Exp."}
    return label in underline_labels


def has_grey_separator(label: str) -> bool:
    """Check if row should have 4px grey separator line below it per Figma."""
    separator_labels = {"Total Revenue", "Gross Profit", "Operating Income"}
    return label in separator_labels


def get_indent_level(label: str) -> int:
    """Get indentation level based on row type - 0=normal (12px), 1=indented (24px)."""
    # Level 1: SUBTOTAL/SUMMARY rows - INDENTED (24px left padding)
    level_1 = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
               "Operating Income", "Net Interest Exp."}
    
    # Level 0: Regular line items - NOT INDENTED (12px left padding)
    if label in level_1:
        return 1  # Subtotals are indented
    else:
        return 0  # Everything else is NOT indented
```

---

## 📝 HTML Table Generation Logic

```python
# Build table HTML
html = '<div class="table-container"><div class="table-scroll"><table class="data-table"><thead>'

# Header row - with grey separator
html += '<tr class="row-grey-separator"><th>For Fiscal Period Ending<span class="header-subtext">Millions of trading currency, except per share items.</span></th>'

# Add period columns
for period in data.periods:
    lines = period.label.split('\n')
    if len(lines) >= 2:
        period_text = lines[0]
        date_text = lines[1]
    else:
        period_text = ""
        date_text = period.label
    
    html += f'<th class="data-col"><span class="period-label">{period_text}</span><span class="period-date">{date_text}</span></th>'

html += '</tr></thead><tbody>'

# Data rows
prev_item_label = None
for i, item in enumerate(data.line_items):
    indent = get_indent_level(item.label)
    is_bold = is_bold_row(item.label)
    needs_grey_sep = has_grey_separator(item.label)
    
    # Check if NEXT row needs underline, if so add it to THIS row
    next_item = data.line_items[i + 1] if i + 1 < len(data.line_items) else None
    needs_underline = has_underline(next_item.label) if next_item else False
    
    # Build row classes
    row_classes = []
    if is_bold:
        row_classes.append("row-bold")
    if needs_underline:
        row_classes.append("row-underline-black")
    if needs_grey_sep:
        row_classes.append("row-grey-separator")
    
    row_class_str = ' '.join(row_classes) if row_classes else ''
    
    html += f'<tr class="{row_class_str}">'
    
    # First column - label with proper indentation
    html += f'<td class="indent-{indent}">{item.label}</td>'
    
    # Data columns with values
    for val in item.values:
        formatted = format_value(val)  # Your formatting function
        html += f'<td class="data-cell">{formatted}</td>'
    
    html += '</tr>'

html += '</tbody></table></div></div>'

# Render the table
st.html(html)
```

---

## 📊 Row Configuration for Income Statement

### Subtotal Rows (Bold + Indented)
- Total Revenue
- Gross Profit
- Other Operating Exp., Total
- Operating Income
- Net Interest Exp.

### Black Underlines (2px) - Appear ABOVE
- Total Revenue
- Gross Profit
- Other Operating Exp., Total
- Operating Income
- Net Interest Exp.

### Grey Separators (4px) - Appear BELOW
- Header row
- Total Revenue
- Gross Profit
- Operating Income

### Regular Rows (Not Indented)
- Revenue
- Other Revenue
- Cost Of Goods Sold
- Selling General & Admin Exp.
- R&D Exp.
- Depreciation & Amort.
- Other Operating Expense/(Income)
- Interest Expense
- Interest and Invest. Income

---

## 🔄 How to Reuse for Key Stats Page

1. **Copy the complete CSS** from above into your Key Stats page
2. **Copy the helper functions** (`is_bold_row`, `has_underline`, `has_grey_separator`, `get_indent_level`)
3. **Modify the helper functions** to match your Key Stats row labels
4. **Copy the HTML generation logic** and adapt for your data structure
5. **Adjust row classifications** based on your specific needs

### Example Modifications for Key Stats

```python
# Update helper functions for your specific row labels
def is_bold_row(label: str) -> bool:
    """Key Stats subtotal rows."""
    bold_labels = {"Total Assets", "Total Liabilities", "Shareholders' Equity"}
    return label in bold_labels

def has_grey_separator(label: str) -> bool:
    """Key Stats grey separator rows."""
    separator_labels = {"Total Assets", "Total Liabilities"}
    return label in separator_labels

# Update indentation logic
def get_indent_level(label: str) -> int:
    level_1 = {"Total Assets", "Total Liabilities", "Shareholders' Equity"}
    return 1 if label in level_1 else 0
```

---

## ✅ Checklist for Implementation

- [ ] Copy CSS variables and table styling
- [ ] Copy helper functions
- [ ] Adapt helper functions for your row labels
- [ ] Copy HTML generation logic
- [ ] Update header text and subtext
- [ ] Test sticky column behavior
- [ ] Test sticky header behavior
- [ ] Verify indentation is correct
- [ ] Verify black underlines appear above subtotals
- [ ] Verify grey separators appear below specific rows
- [ ] Test horizontal scroll
- [ ] Test vertical scroll

---

## 📖 Reference

Original implementation: [`market_data.py`](file:///Users/mohdsaeedafri/Documents/Documents/Code-Base/kimi-sec-10k-1/app/pages/market_data.py)

Created: 2026-02-12
