"""
Main entry point for worm behavior analysis pipeline.

This module provides the main interface for running the complete worm behavior
analysis pipeline, from SLEAP tracking data to behavioral insights.

Author: Worm Behavior Analysis Pipeline
Date: July 2025
Version: 1.0
"""

import argparse
import sys
import time
from pathlib import Path # For path manipulations

from io_utils import find_videos
from tracking_with_sleapai import track_worms_in_video
#from tracking_corrections_main import tracking_error_detections_and_corrections

def main():
    parser = argparse.ArgumentParser(description="Worm Behavior Analysis Pipeline")
    parser.add_argument("--output_folder", type=str, help="Path to the output folder for results", default="Worm_Behavior_Analysis_Pipeline_2025/Output")
    parser.add_argument("--use_video_folder", action='store_true', help="Flag to indicate using video folder", default=True)
    parser.add_argument("--input_video_folder", type=str, help="Path to the input folder containing videos", default="Worm_Behavior_Analysis_Pipeline_2025/Input")
    parser.add_argument("--model_path", type=str, help="Path to the pre-trained SLEAP model file", default="Worm_Behavior_Analysis_Pipeline_2025/Model")
    args = parser.parse_args()

    if args.use_video_folder:
        videos = find_videos(args.input_video_folder)
        if not videos:
            print("No new videos found in the input folder.")
        for video in videos:
            print(f"processing video: {video.name}")
            #create output folder for individual videos inside the output folder
            video_output_folder = Path(args.output_folder) / video.stem
            video_output_folder.mkdir(parents=True, exist_ok=True)
            video_out_path = Path(str(video_output_folder / video.name).replace("\\", "/"))  # Path to the moved video with forward slashes
            print(f"Moving video to: {video_out_path}")
            video.rename(video_out_path) #moves the video to the output folder
            #check if h5 file already exists for this video by checking if there is with h5 extension in the output folder
            if any(file.suffix == '.h5' for file in video_output_folder.iterdir()):
                print(f"H5 file already exists for {video.name}. Skipping tracking.")
            else:
                #start tracking
                track_worms_in_video(video_out_path, args.model_path, video_output_folder) #naming will be handled inside the function

            #move onto tracking corrections


if __name__ == "__main__":
    main()