import streamlit as st
import json
import os
import datetime
import subprocess
from converter import main as convert


def diff_json(a, b, path=""):
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        all_keys = set(a) | set(b)
        for k in sorted(all_keys):
            full_path = f"{path}.{k}" if path else k
            if k not in a:
                diffs.append(("added", full_path, None, b[k]))
            elif k not in b:
                diffs.append(("removed", full_path, a[k], None))
            else:
                diffs.extend(diff_json(a[k], b[k], full_path))
    elif isinstance(a, list) and isinstance(b, list):
        for i, (va, vb) in enumerate(zip(a, b)):
            diffs.extend(diff_json(va, vb, f"{path}[{i}]"))
        for i in range(len(b), len(a)):
            diffs.append(("removed", f"{path}[{i}]", a[i], None))
        for i in range(len(a), len(b)):
            diffs.append(("added", f"{path}[{i}]", None, b[i]))
    else:
        if a != b:
            diffs.append(("changed", path, a, b))
    return diffs

st.set_page_config(page_title="Telemetry Converter", page_icon="📡", layout="wide")

# ── Session defaults ──────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
# ── Theme CSS injection ───────────────────────────────────────────────────────
dark = st.session_state.dark_mode

if dark:
    theme_css = """
        section[data-testid="stMain"] {
            background-color: #0e1117 !important;
            color: #fafafa !important;
        }
        section[data-testid="stSidebar"] { background-color: #161b22 !important; }
        .stTabs [data-baseweb="tab-list"] { background-color: #161b22 !important; }
        .stTabs [data-baseweb="tab"] { color: #cdd9e5 !important; }
        .stTabs [aria-selected="true"] { color: #ffffff !important; }
        div[data-testid="stCodeBlock"] pre { background-color: #1e2530 !important; }
        label, p, span, h1, h2, h3, h4 { color: #fafafa !important; }
        div[data-testid="stMetricValue"] { color: #79c0ff !important; }
        .stExpander { border-color: #30363d !important; }
        div[data-testid="stForm"] { background-color: #161b22 !important; }
    """
else:
    theme_css = ""

st.markdown(
    f"<style>{theme_css}</style>",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
logo_col, title_col, author_col = st.columns([2, 5, 3])

with logo_col:
    st.markdown(
        """
        <div style='padding-top: 14px;'>
            <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 48' height='48' width='160'>
                <text x='0' y='38'
                    font-family='Arial, Helvetica, sans-serif'
                    font-size='38'
                    font-weight='bold'
                    fill='#1a1a1a'
                    letter-spacing='-1'>Deloitte</text>
                <circle cx='193' cy='32' r='7' fill='#86BC25'/>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )

with title_col:
    st.title("Telemetry Converter")

with author_col:
    st.markdown(
        """
        <div style='text-align: right; padding-top: 12px;'>
            <strong>About the Author</strong><br>
            <a href='https://portfolio-sage-two-68.vercel.app/' target='_blank'>
                <button style='
                    margin-top: 6px;
                    padding: 6px 16px;
                    background-color: #4F8BF9;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                '>🌐 View Portfolio</button>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Control bar ───────────────────────────────────────────────────────────────
st.divider()
ctrl_left, ctrl_right = st.columns([6, 4])

with ctrl_left:
    mode_label = "☀️ Light mode" if dark else "🌙 Dark mode"
    if st.button(mode_label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

with ctrl_right:
    st.caption(f"Theme: {'Dark' if dark else 'Light'}")

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    ["Data Converter", "Upload & Convert", "History", "Tests", "Compare", "Validate", "Export", "Playground"]
)

base = os.path.dirname(__file__)

with open(os.path.join(base, "data-1.json")) as f:
    sample1 = json.load(f)
with open(os.path.join(base, "data-2.json")) as f:
    sample2 = json.load(f)
with open(os.path.join(base, "data-result.json")) as f:
    expected = json.load(f)

if "history" not in st.session_state:
    st.session_state.history = []

# ── Tab 1: Data Converter ────────────────────────────────────────────────────
with tab1:
    st.header("Device Data Converter")
    st.write("Convert device telemetry JSON between two raw formats into a unified structure.")

    col_input, col_arrow, col_output = st.columns([5, 1, 5])

    with col_input:
        st.subheader("Input")
        format_choice = st.radio(
            "Choose a sample format",
            ["Format 1 (flat location string)", "Format 2 (nested device object)"],
            horizontal=True,
        )
        default_input = sample1 if "Format 1" in format_choice else sample2
        raw = st.text_area("JSON Input", value=json.dumps(default_input, indent=2), height=320)

    with col_arrow:
        for _ in range(5):
            st.write("")
        st.markdown("### →")

    with col_output:
        st.subheader("Output")
        try:
            parsed = json.loads(raw)
            result = convert(parsed)
            st.code(json.dumps(result, indent=2), language="json")
            if result == expected:
                st.success("Matches expected result")
            else:
                st.warning("Result differs from expected")
        except Exception as e:
            st.error(f"Error: {e}")

    with st.expander("Expected result"):
        st.code(json.dumps(expected, indent=2), language="json")

# ── Tab 2: Upload & Convert ───────────────────────────────────────────────────
with tab2:
    st.header("Upload & Convert")
    st.write("Upload your own JSON file to convert it and optionally validate against an expected result.")

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Input file")
        uploaded_input = st.file_uploader("Upload a JSON file to convert", type=["json"], key="upload_input")
    with col_right:
        st.subheader("Expected result (optional)")
        uploaded_expected = st.file_uploader("Upload an expected result JSON to validate against", type=["json"], key="upload_expected")

    st.divider()

    if uploaded_input is not None:
        try:
            raw_bytes = uploaded_input.read()
            input_data = json.loads(raw_bytes)
            converted = convert(input_data)

            detected_format = "Format 2" if input_data.get("device") else "Format 1"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            validation_status = None

            res_col, info_col = st.columns(2)

            with res_col:
                st.subheader("Converted output")
                st.code(json.dumps(converted, indent=2), language="json")
                st.download_button(
                    label="Download converted JSON",
                    data=json.dumps(converted, indent=2).encode("utf-8"),
                    file_name="converted.json",
                    mime="application/json",
                )

            with info_col:
                st.subheader("Input preview")
                st.code(json.dumps(input_data, indent=2), language="json")

                if uploaded_expected is not None:
                    st.subheader("Validation")
                    try:
                        expected_data = json.loads(uploaded_expected.read())
                        if converted == expected_data:
                            st.success("Output matches the expected result")
                            validation_status = "passed"
                        else:
                            st.error("Output does not match the expected result")
                            validation_status = "failed"
                            with st.expander("Expected"):
                                st.code(json.dumps(expected_data, indent=2), language="json")
                    except Exception as ex:
                        st.error(f"Could not parse expected file: {ex}")

            existing_names = [h["filename"] for h in st.session_state.history]
            if uploaded_input.name not in existing_names:
                st.session_state.history.insert(0, {
                    "filename": uploaded_input.name,
                    "timestamp": timestamp,
                    "format": detected_format,
                    "input": input_data,
                    "output": converted,
                    "validation": validation_status,
                })

        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
        except Exception as e:
            st.error(f"Conversion error: {e}")
    else:
        st.info("Upload a JSON file above to get started.")

# ── Tab 3: History ────────────────────────────────────────────────────────────
with tab3:
    st.header("Conversion History")
    st.write("All files converted during this session.")

    history = st.session_state.history

    if not history:
        st.info("No conversions yet. Upload a file in the Upload & Convert tab to get started.")
    else:
        col_summary, col_clear = st.columns([6, 1])
        with col_summary:
            st.write(f"**{len(history)}** conversion{'s' if len(history) != 1 else ''} this session")
        with col_clear:
            if st.button("Clear history", type="secondary"):
                st.session_state.history = []
                st.rerun()

        st.divider()

        for i, entry in enumerate(history):
            validation_badge = ""
            if entry["validation"] == "passed":
                validation_badge = " ✅"
            elif entry["validation"] == "failed":
                validation_badge = " ❌"

            with st.expander(
                f"**{entry['filename']}**{validation_badge} — {entry['timestamp']} · {entry['format']}",
                expanded=(i == 0),
            ):
                left, right = st.columns(2)

                with left:
                    st.markdown("**Input**")
                    st.code(json.dumps(entry["input"], indent=2), language="json")

                with right:
                    st.markdown("**Converted output**")
                    st.code(json.dumps(entry["output"], indent=2), language="json")
                    st.download_button(
                        label="Re-download",
                        data=json.dumps(entry["output"], indent=2).encode("utf-8"),
                        file_name=f"converted_{entry['filename']}",
                        mime="application/json",
                        key=f"dl_{i}",
                    )

                meta_cols = st.columns(3)
                with meta_cols[0]:
                    st.caption(f"Converted at: {entry['timestamp']}")
                with meta_cols[1]:
                    st.caption(f"Detected format: {entry['format']}")
                with meta_cols[2]:
                    if entry["validation"] == "passed":
                        st.caption("Validation: passed ✅")
                    elif entry["validation"] == "failed":
                        st.caption("Validation: failed ❌")
                    else:
                        st.caption("Validation: not run")

# ── Tab 4: Tests ─────────────────────────────────────────────────────────────
with tab4:
    st.header("Unit Test Runner")
    st.write("Run the three test cases against the converter and see live results.")

    def run_tests():
        results = []

        try:
            r = json.loads(json.dumps(expected))
            assert r == expected
            results.append(("test_sanity", "PASS", "Sanity check: expected JSON round-trips correctly.", None))
        except AssertionError as e:
            results.append(("test_sanity", "FAIL", "Sanity check failed.", str(e)))

        try:
            r = convert(sample1)
            assert r == expected, "Output does not match expected result"
            results.append(("test_dataType1", "PASS", "Format 1 converted correctly.", None))
        except AssertionError as e:
            results.append(("test_dataType1", "FAIL", "Format 1 conversion failed.", str(e)))
        except Exception as e:
            results.append(("test_dataType1", "ERROR", "Unexpected error.", str(e)))

        try:
            r = convert(sample2)
            assert r == expected, "Output does not match expected result"
            results.append(("test_dataType2", "PASS", "Format 2 converted correctly.", None))
        except AssertionError as e:
            results.append(("test_dataType2", "FAIL", "Format 2 conversion failed.", str(e)))
        except Exception as e:
            results.append(("test_dataType2", "ERROR", "Unexpected error.", str(e)))

        return results

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("▶ Run Tests", type="primary"):
            st.session_state["test_results"] = run_tests()
    with col_btn2:
        if st.button("⌘ Run main.py (terminal output)"):
            script_path = os.path.join(base, "main.py")
            proc = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                cwd=base,
            )
            output = proc.stderr if proc.stderr else proc.stdout
            st.session_state["cli_output"] = output
            st.session_state["cli_returncode"] = proc.returncode

    if "cli_output" in st.session_state:
        st.divider()
        st.subheader("Terminal output")
        if st.session_state["cli_returncode"] == 0:
            st.success("All tests passed")
        else:
            st.error("Some tests failed")
        st.code(st.session_state["cli_output"], language="text")
        st.divider()

    if "test_results" in st.session_state:
        results = st.session_state["test_results"]
        passed = sum(1 for r in results if r[1] == "PASS")
        total = len(results)

        if passed == total:
            st.success(f"All {total} tests passed")
        else:
            st.error(f"{passed}/{total} tests passed")

        st.divider()

        for name, status, description, detail in results:
            cols = st.columns([1, 3, 4])
            with cols[0]:
                if status == "PASS":
                    st.markdown("✅ **PASS**")
                elif status == "FAIL":
                    st.markdown("❌ **FAIL**")
                else:
                    st.markdown("⚠️ **ERROR**")
            with cols[1]:
                st.markdown(f"`{name}`")
            with cols[2]:
                st.write(description)
                if detail:
                    st.caption(detail)

# ── Tab 5: Compare ───────────────────────────────────────────────────────────
with tab5:
    st.header("JSON Comparator")
    st.write("Upload two JSON files to compare them side by side and see exactly what differs.")

    cmp_left, cmp_right = st.columns(2)
    with cmp_left:
        file_a = st.file_uploader("File A", type=["json"], key="cmp_a")
    with cmp_right:
        file_b = st.file_uploader("File B", type=["json"], key="cmp_b")

    use_samples = st.checkbox("Use built-in samples (data-1.json vs data-2.json)")

    st.divider()

    json_a = json_b = None
    label_a, label_b = "File A", "File B"

    if use_samples:
        json_a, json_b = sample1, sample2
        label_a, label_b = "data-1.json", "data-2.json"
    else:
        if file_a:
            try:
                json_a = json.loads(file_a.read())
                label_a = file_a.name
            except Exception as e:
                st.error(f"Could not parse File A: {e}")
        if file_b:
            try:
                json_b = json.loads(file_b.read())
                label_b = file_b.name
            except Exception as e:
                st.error(f"Could not parse File B: {e}")

    if json_a is not None and json_b is not None:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader(label_a)
            st.code(json.dumps(json_a, indent=2), language="json")
        with col_b:
            st.subheader(label_b)
            st.code(json.dumps(json_b, indent=2), language="json")

        st.divider()
        st.subheader("Differences")

        diffs = diff_json(json_a, json_b)

        if not diffs:
            st.success("The two files are identical.")
        else:
            st.info(f"Found **{len(diffs)}** difference{'s' if len(diffs) != 1 else ''}")

            for kind, path, val_a, val_b in diffs:
                dcols = st.columns([2, 3, 3])
                with dcols[0]:
                    if kind == "changed":
                        st.markdown("🔄 **changed**")
                    elif kind == "added":
                        st.markdown("➕ **added**")
                    else:
                        st.markdown("➖ **removed**")
                with dcols[1]:
                    st.markdown(f"`{path}`")
                with dcols[2]:
                    if kind == "changed":
                        st.caption(f"{repr(val_a)}  →  {repr(val_b)}")
                    elif kind == "added":
                        st.caption(f"value: {repr(val_b)}")
                    else:
                        st.caption(f"was: {repr(val_a)}")
    elif not use_samples:
        st.info("Upload both files above to start comparing.")

# ── Tab 6: Validate ──────────────────────────────────────────────────────────
with tab6:
    st.header("Schema Validator")
    st.write("Define a schema and check whether a JSON file conforms to it.")

    UNIFIED_SCHEMA = {
        "deviceID": "str",
        "deviceType": "str",
        "timestamp": "int",
        "location": {
            "country": "str",
            "city": "str",
            "area": "str",
            "factory": "str",
            "section": "str",
        },
        "data": {
            "status": "str",
            "temperature": "int | float",
        },
    }

    TYPE_MAP = {
        "str": str,
        "int": int,
        "float": float,
        "int | float": (int, float),
        "bool": bool,
        "list": list,
        "dict": dict,
    }

    def validate_against_schema(doc, schema, path=""):
        errors = []
        checks = []
        if not isinstance(schema, dict):
            return checks, errors

        for key, expected in schema.items():
            full_path = f"{path}.{key}" if path else key
            if key not in doc:
                errors.append(f"Missing field: `{full_path}`")
            elif isinstance(expected, dict):
                if not isinstance(doc[key], dict):
                    errors.append(f"`{full_path}` should be an object, got `{type(doc[key]).__name__}`")
                else:
                    sub_checks, sub_errors = validate_against_schema(doc[key], expected, full_path)
                    checks.extend(sub_checks)
                    errors.extend(sub_errors)
            else:
                expected_type = TYPE_MAP.get(expected)
                actual = doc[key]
                if expected_type and not isinstance(actual, expected_type):
                    errors.append(
                        f"`{full_path}` should be `{expected}`, got `{type(actual).__name__}` ({repr(actual)})"
                    )
                else:
                    checks.append(f"`{full_path}` — {type(actual).__name__} ✓")

        extra_keys = set(doc.keys()) - set(schema.keys())
        for k in sorted(extra_keys):
            full_path = f"{path}.{k}" if path else k
            errors.append(f"Unexpected field: `{full_path}`")

        return checks, errors

    schema_col, doc_col = st.columns(2)

    with schema_col:
        st.subheader("Schema")
        schema_choice = st.radio(
            "Schema source",
            ["Built-in unified format", "Custom JSON schema"],
            horizontal=True,
            key="schema_choice",
        )

        if schema_choice == "Built-in unified format":
            active_schema = UNIFIED_SCHEMA
            st.code(json.dumps(UNIFIED_SCHEMA, indent=2), language="json")
        else:
            default_schema = json.dumps({
                "deviceID": "str",
                "deviceType": "str",
                "timestamp": "int"
            }, indent=2)
            raw_schema = st.text_area(
                "Define schema (field: type)",
                value=default_schema,
                height=260,
                help='Use types: str, int, float, int | float, bool, list, dict',
            )
            try:
                active_schema = json.loads(raw_schema)
                st.caption("Valid JSON schema")
            except Exception as e:
                st.error(f"Invalid schema JSON: {e}")
                active_schema = None

    with doc_col:
        st.subheader("Document to validate")
        doc_source = st.radio(
            "Document source",
            ["Upload file", "Use sample (expected result)"],
            horizontal=True,
            key="doc_source",
        )

        doc_data = None
        if doc_source == "Upload file":
            val_file = st.file_uploader("Upload JSON to validate", type=["json"], key="val_upload")
            if val_file:
                try:
                    doc_data = json.loads(val_file.read())
                    st.code(json.dumps(doc_data, indent=2), language="json")
                except Exception as e:
                    st.error(f"Could not parse file: {e}")
        else:
            doc_data = expected
            st.code(json.dumps(doc_data, indent=2), language="json")

    st.divider()

    if active_schema and doc_data is not None:
        st.subheader("Validation results")
        checks, errors = validate_against_schema(doc_data, active_schema)

        if not errors:
            st.success(f"All {len(checks)} field checks passed — document is valid.")
        else:
            st.error(f"{len(errors)} issue{'s' if len(errors) != 1 else ''} found")

        if checks:
            with st.expander(f"✅ {len(checks)} passing field{'s' if len(checks) != 1 else ''}"):
                for c in checks:
                    st.markdown(f"- {c}")

        if errors:
            st.subheader("Issues")
            for err in errors:
                st.markdown(f"- ❌ {err}")
    else:
        st.info("Configure a schema and select a document above to validate.")

# ── Tab 7: Export ────────────────────────────────────────────────────────────
with tab7:
    st.header("Session Export")
    st.write("Download a complete summary of everything done this session — conversions, test runs, and validations.")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history = st.session_state.get("history", [])
    test_results = st.session_state.get("test_results", [])
    cli_output = st.session_state.get("cli_output", None)

    summary = {
        "exported_at": now,
        "app": "Telemetry Converter",
        "session_summary": {
            "total_conversions": len(history),
            "tests_run": len(test_results) > 0,
            "cli_run": cli_output is not None,
        },
        "conversions": [
            {
                "filename": e["filename"],
                "converted_at": e["timestamp"],
                "detected_format": e["format"],
                "validation": e["validation"],
                "input": e["input"],
                "output": e["output"],
            }
            for e in history
        ],
        "test_results": [
            {
                "name": name,
                "status": status,
                "description": description,
                "detail": detail,
            }
            for name, status, description, detail in test_results
        ],
        "cli_output": cli_output,
    }

    # Preview
    has_data = history or test_results or cli_output

    if not has_data:
        st.info("Nothing to export yet. Run some conversions or tests first, then come back here.")
    else:
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("Conversions", len(history))
        with stat_cols[1]:
            st.metric("Tests", len(test_results) if test_results else 0)
        with stat_cols[2]:
            st.metric("CLI runs", 1 if cli_output else 0)

        st.divider()

        with st.expander("Preview export JSON"):
            st.code(json.dumps(summary, indent=2), language="json")

        export_bytes = json.dumps(summary, indent=2).encode("utf-8")
        filename = f"telemetry_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        st.download_button(
            label="⬇ Download session summary",
            data=export_bytes,
            file_name=filename,
            mime="application/json",
            type="primary",
        )

# ── Tab 8: Playground ────────────────────────────────────────────────────────
with tab8:
    st.header("Interactive Playground")

    st.subheader("Counter")
    if "count" not in st.session_state:
        st.session_state.count = 0

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ Increment"):
            st.session_state.count += 1
    with c2:
        if st.button("➖ Decrement"):
            st.session_state.count -= 1
    with c3:
        if st.button("🔄 Reset"):
            st.session_state.count = 0

    st.metric("Count", st.session_state.count)

    st.divider()

    st.subheader("Text Input")
    name = st.text_input("Enter your name", placeholder="Type here...")
    if name:
        st.success(f"Hello, {name}! 👋")

    st.divider()

    st.subheader("Number Slider")
    value = st.slider("Pick a number", min_value=0, max_value=100, value=50)
    st.write(f"You selected: **{value}**")
    st.progress(value / 100)
