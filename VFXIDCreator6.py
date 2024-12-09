import streamlit as st
import re

# Display a hyperlink at the top
st.markdown("[Visit the Author's Website](https://coreyscottfrost.com)", unsafe_allow_html=True)

# Function to handle file import and preview
def import_markers(file):
    if file is not None:
        content = file.read().decode("utf-8")
        lines = content.split("\n")
        total_markers = len(lines)
        return content, f"Total Markers Detected: {total_markers}"
    return None, "No file selected"

# Function to process the markers and generate VFX IDs
def process_markers(marker_content, show_code, episode_reel, include_descriptions, starting_shot_input, increment_option):
    processed_output = []
    shot_number = starting_shot_input
    current_scene = None
    scene_last_shot = {}
    total_shots = 0

    # Adjust regex pattern to allow 4 or 5 characters for scene code
    scene_pattern = re.compile(r"([A-Z0-9]{2,5}) -")

    lines = marker_content.split("\n")
    for line in lines:
        if line.strip() == "":
            continue
        parts = line.split("\t")
        comment = parts[4].strip() if len(parts) > 4 else ""

        scene_match = scene_pattern.match(comment)
        if scene_match:
            scene_code = scene_match.group(1)
            description = comment.split(" - ")[1] if " - " in comment else ""
            current_scene = scene_code
            if current_scene not in scene_last_shot:
                shot_number = starting_shot_input
            scene_last_shot[current_scene] = shot_number
        elif current_scene is not None:
            description = comment
        else:
            continue

        scene_last_shot[current_scene] = shot_number
        if episode_reel:
            vfx_id = f"{show_code}_{episode_reel}_{current_scene}_{str(shot_number).zfill(4)}"
        else:
            vfx_id = f"{show_code}_{current_scene}_{str(shot_number).zfill(4)}"

        if include_descriptions and description:
            vfx_id += f" - {description}"

        parts[4] = vfx_id if len(parts) > 4 else vfx_id
        processed_output.append("\t".join(parts))

        total_shots += 1
        shot_number += increment_option

    return "\n".join(processed_output), f"Total Shots Processed: {total_shots}"

# Streamlit UI
st.title("Corey Frost's VFX ID Creator")

show_code = st.text_input("Show Code")
episode_reel = st.text_input("Episode/Reel Number")
include_descriptions = st.checkbox("Include Descriptions")

# Custom Starting Shot Number
starting_shot_input = st.number_input("Custom Starting Shot Number", value=10)

# Dropdown for Shot Increment Options
increment_option = st.selectbox("Select Shot Increment", options=[1, 5, 10], index=2)

uploaded_file = st.file_uploader("Import Marker File", type="txt")

if uploaded_file:
    marker_content, total_markers = import_markers(uploaded_file)
    st.text_area("Preview of Imported Marker File", value=marker_content, height=300)
    st.write(total_markers)

if st.button("Process Markers"):
    if uploaded_file and show_code:
        processed_output, shot_count = process_markers(marker_content, show_code, episode_reel, include_descriptions, starting_shot_input, increment_option)
        st.text_area("Processed VFX IDs", value=processed_output, height=300)
        st.write(shot_count)

if uploaded_file and st.button("Save Output"):
    processed_output, shot_count = process_markers(marker_content, show_code, episode_reel, include_descriptions, starting_shot_input, increment_option)
    st.download_button(label="Download Processed File", data=processed_output, file_name="processed_markers.txt", mime="text/plain")
