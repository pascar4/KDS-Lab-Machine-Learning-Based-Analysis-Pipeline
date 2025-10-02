"""
This file provides utilities for loading and handling SLEAP tracking using the SLEAP library.
"""

import os
from sleap import load_model
from sleap.io.dataset import Labels
from sleap.io.video import Video


def track_worms_in_video(video_path, model_path, output_path):
    """
    Track worms in a video using a pre-trained SLEAP model and save the results to an H5 file.

    Parameters:
    - video_path: Path to the input video file.
    - model_path: Path to the pre-trained SLEAP model file.
    - output_h5_path: Path to save the output H5 file with tracking results.
    """
    # Load the SLEAP model
    # Or, if you have multiple models for a top-down approach (e.g., centroid and instance models)
    # predictor = sleap.load_model(["path/to/centroid_model", "path/to/instance_model"])
    centroid_model = None
    instance_model = None
    # Search for centroid and instance model folders
    for item in os.listdir(model_path):
        item_path = os.path.join(model_path, item)
        if os.path.isdir(item_path):
            if "centroid" in item.lower():
                centroid_model = item_path
            elif "instance" in item.lower():
                instance_model = item_path
    if not centroid_model or not instance_model:
        raise FileNotFoundError("Could not find both centroid and instance model folders in the specified model_path.")

    # get the number of worms from the video filename example: 2023-08-25_13-00-51_PR_7_microfluidics_m9.mp4 has 7 worms
    #second example: 2024-03-19_16-46-00_PR_14_M9_60v.mp4 has 14 worms
    num_worms = int(video_path.stem.split("_")[3])  # Extract number of worms from filename
    print(f"Number of worms detected from filename: {num_worms}")

    # Load the models and setup the predictor with tracking configuration and number of instances
    predictor = load_model(
        [centroid_model, instance_model], 
        batch_size=4, 
        peak_threshold=.15,
        refinement="integral",
        tracker="simple",
        tracker_window=15, #import for tracking ID
        tracker_max_instances=num_worms, # Adjust this based on your video
        max_instances=num_worms, # Adjust this based on your video
        disable_gpu_preallocation=True,
        progress_reporting="rich",
        resize_input_layer=True,
        )

    # Load video
    video = Video.from_filename(str(video_path)) #make windows file path to str so import works

    predictions = predictor.predict(video, make_labels=True)
    
    # generate a unique filename based on the video name for SLEAP file
    output_filename = os.path.join(output_path, f"{video_path.stem}_simple_tracked.slp")
    # Save predictions to SLEAP file if research wants to look at them later
    Labels.save_file(labels=predictions, filename=output_filename) # type: ignore
    
    #generate a unique filename based on the video name for H5 file
    output_h5_filename = os.path.join(output_path, f"{video_path.stem}_simple_tracked.h5")
    # Export predictions to H5 file for further corrections and analysis
    predictions.export(output_h5_filename) # type: ignore