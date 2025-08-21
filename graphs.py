import os
import json
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend by using Anti-Grain Geometry - renderer for PNGs.
import matplotlib.pyplot as plt
import io

def listens_by_week(track_id_to_check, upload_folder="data"):
    timestamps = []
    for filename in os.listdir(upload_folder):
        if filename.endswith(".json"):
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue

                for entry in data:
                    uri = entry.get("spotify_track_uri")
                    if uri:
                        track_id_from_uri = uri.split(":")[-1]
                        if track_id_from_uri == track_id_to_check:
                            ts = entry.get("ts")
                            if ts:
                                timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))

    if not timestamps:
        return None, None

    weeks = np.array([t.isocalendar()[:2] for t in timestamps])  # (year, week)
    unique_weeks, counts = np.unique(weeks, axis=0, return_counts=True)
    
    # Sort by year, week
    sort_idx = np.lexsort((unique_weeks[:,1], unique_weeks[:,0]))
    return unique_weeks[sort_idx], counts[sort_idx]

def plot_listens_image(unique_weeks, counts):
    labels = [f"{year}-W{week}" for year, week in unique_weeks]

    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(labels, counts, color="#1DB954")
    ax.set_xlabel("Week")
    ax.set_ylabel("Number of Listens")
    ax.set_title(f"Weekly Listens")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save figure to in-memory BytesIO
    img = io.BytesIO()
    fig.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return img
