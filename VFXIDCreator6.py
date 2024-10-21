import streamlit as st
import re

# Function to handle file import and preview
def import_markers(file):
    if file is not None:
        # Read the file and return the content for preview
        content = file.read().decode("utf-8")
        lines = content.split("\n")
        total_markers = len(lines)
        return content, f"Total Markers Detected: {total_markers}"
    return None, "No file selected"

# Function to process the markers and generate VFX IDs
def process_markers(marker_content, show_code, episode_reel, include_descriptions, starting_shot_input):
    # Initialize variables for processing
    processed_output = []
    shot_number = starting_shot_input
    current_scene = None  # Track the current scene
    scene_last_shot = {}  # To track the last shot number for each scene
    total_shots = 0  # To count the number of shots being processed

    # Define regex pattern to detect scene codes (e.g., "SC01 -")
    scene_pattern = re.compile(r"([A-Z0-9]{4}) -")

    # Process each line in the markers content
    lines = marker_content.split("\n")
    for line in lines:
        if line.strip() == "":
            continue
        parts = line.split("\t")
        comment = parts[4].strip() if len(parts) > 4 else ""  # Extract the comment

        # Check for a new scene using regex
        scene_match = scene_pattern.match(comment)
        if scene_match:
            # Extract the scene code
            scene_code = scene_match.group(1)
            description = comment.split(" - ")[1] if " - " in comment else ""

            # Initialize shot numbering for the new scene, using the selected starting shot number
            current_scene = scene_code  # Set the scene code
            if current_scene not in scene_last_shot:  # Only reset for new scenes
                shot_number = starting_shot_input  # Set the shot number to the selected starting value

            scene_last_shot[current_scene] = shot_number  # Track the last shot for this scene

        elif current_scene is not None:
            # If no scene detected but we're in a current scene, continue numbering
            description = comment  # Treat comment as description if no new scene is detected

        else:
            continue  # Skip if no scene is detected and no previous scene to reference

        # Store the last shot number for the scene
        scene_last_shot[current_scene] = shot_number

        # Generate the VFX ID
        if episode_reel:
            vfx_id = f"{show_code}_{episode_reel}_{current_scene}_{str(shot_number).zfill(4)}"
        else:
            vfx_id = f"{show_code}_{current_scene}_{str(shot_number).zfill(4)}"

        # Add description if checkbox is checked and description is available
        if include_descriptions and description:
            vfx_id += f" - {description}"

        # Update the comment with the VFX ID and keep the line formatting intact
        parts[4] = vfx_id if len(parts) > 4 else vfx_id
        processed_output.append("\t".join(parts))  # Keep the same tab-delimited format

        total_shots += 1  # Count the processed shots

        # Now increment shot number AFTER processing this shot
        shot_number += 10

    # Return the processed output and total shots processed
    return "\n".join(processed_output), f"Total Shots Processed: {total_shots}"

# Streamlit UI
st.title("Corey Frost's VFX ID Creator")

# Show Code Input
show_code = st.text_input("Show Code")

# Episode/Reel Number Input
episode_reel = st.text_input("Episode/Reel Number")

# Include Descriptions Checkbox
include_descriptions = st.checkbox("Include Descriptions")

# Starting Shot Number Input
starting_shot_input = st.number_input("Starting Shot Number", value=10)

# File Upload
uploaded_file = st.file_uploader("Import Marker File", type="txt")

# Display the file name and content if a file is uploaded
if uploaded_file:
    marker_content, total_markers = import_markers(uploaded_file)
    st.text_area("Preview of Imported Marker File", value=marker_content, height=300)
    st.write(total_markers)

# Process Markers Button
if st.button("Process Markers"):
    if uploaded_file and show_code:
        # Process markers and show the output
        processed_output, shot_count = process_markers(marker_content, show_code, episode_reel, include_descriptions, starting_shot_input)
        st.text_area("Processed VFX IDs", value=processed_output, height=300)
        st.write(shot_count)

# Save Output Button
if uploaded_file and st.button("Save Output"):
    processed_output, shot_count = process_markers(marker_content, show_code, episode_reel, include_descriptions, starting_shot_input)
    # Download the processed output as a .txt file
    st.download_button(label="Download Processed File", data=processed_output, file_name="processed_markers.txt", mime="text/plain")
