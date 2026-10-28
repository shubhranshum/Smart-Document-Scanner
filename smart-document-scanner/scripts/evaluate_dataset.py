import os
import sys
import json
import time
import csv
import numpy as np
import cv2

# Add backend directory to sys.path so we can import detection logic directly
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
backend_dir = os.path.join(project_root, "backend")
sys.path.insert(0, backend_dir)

from app.services.document_detection import detect_document
from app.services.metrics import compute_corner_errors

def evaluate():
    sample_images_dir = os.path.join(project_root, "dataset", "sample_images")
    ground_truth_path = os.path.join(project_root, "dataset", "ground_truth", "ground_truth.json")
    results_csv_path = os.path.join(project_root, "dataset", "evaluation_results.csv")

    if not os.path.exists(ground_truth_path):
        print(f"Error: Ground truth file not found at {ground_truth_path}")
        print("Please run `python scripts/generate_test_dataset.py` first.")
        return

    with open(ground_truth_path, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    total_images = len(ground_truth)
    if total_images == 0:
        print("No images found in ground truth catalog.")
        return

    print("=" * 80)
    print(" SmartScan IPCV Evaluation Framework: Document Detection Benchmark")
    print(f" Total Evaluation Images: {total_images}")
    print("=" * 80)

    results = []
    successful_detections = 0
    all_mean_errors = []
    all_normalized_errors = []
    all_times = []

    for filename, record in ground_truth.items():
        img_path = os.path.join(sample_images_dir, filename)
        if not os.path.exists(img_path):
            print(f"Warning: Image file not found: {img_path}")
            continue

        # Load RGB image
        img_bgr = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]

        gt_corners_list = record["ground_truth_corners"]
        gt_pts = np.array([[c["x"], c["y"]] for c in gt_corners_list], dtype=np.float32)

        start_t = time.perf_counter()
        detected, detected_pts, method, area, peri, _ = detect_document(img_rgb)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        if detected and detected_pts is not None:
            successful_detections += 1
            all_times.append(elapsed_ms)

            # Compute corner error metrics
            err_dict = compute_corner_errors(detected_pts, gt_pts, (h, w))
            mean_err = err_dict["mean_error"]
            norm_err = err_dict["normalized_mean_error"]

            all_mean_errors.append(mean_err)
            all_normalized_errors.append(norm_err)

            status_str = "PASS"
            fail_reason = ""
        else:
            status_str = "FAIL"
            mean_err = None
            norm_err = None
            fail_reason = "No 4-point convex contour found matching criteria"

        row = {
            "filename": filename,
            "status": status_str,
            "method": method if detected else "none",
            "mean_corner_error_px": round(mean_err, 2) if mean_err is not None else "N/A",
            "normalized_error_pct": round(norm_err * 100, 3) if norm_err is not None else "N/A",
            "time_ms": round(elapsed_ms, 2),
            "failure_reason": fail_reason,
            "description": record.get("description", "")
        }
        results.append(row)

        print(f"[{status_str:4s}] {filename:<34} Method: {row['method']:<18} Error: {str(row['mean_corner_error_px']):<6} px ({str(row['normalized_error_pct'])}%) Time: {elapsed_ms:6.2f} ms")

    # Write results to CSV
    csv_fields = [
        "filename", "status", "method", "mean_corner_error_px",
        "normalized_error_pct", "time_ms", "failure_reason", "description"
    ]
    with open(results_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(results)

    success_rate = (successful_detections / total_images) * 100.0
    avg_mean_err = np.mean(all_mean_errors) if all_mean_errors else 0.0
    avg_norm_err = np.mean(all_normalized_errors) * 100.0 if all_normalized_errors else 0.0
    avg_time = np.mean(all_times) if all_times else 0.0

    print("\n" + "=" * 80)
    print(" QUANTITATIVE BENCHMARK SUMMARY")
    print("=" * 80)
    print(f" Total Test Cases Evaluated : {total_images}")
    print(f" Successful Detections      : {successful_detections} / {total_images}")
    print(f" Detection Success Rate     : {success_rate:.1f}%")
    print(f" Mean Corner Error          : {avg_mean_err:.2f} px")
    print(f" Mean Normalized Error      : {avg_norm_err:.3f}% (Normalized by diagonal)")
    print(f" Average Processing Time    : {avg_time:.2f} ms (per detected image)")
    print(f" Detailed CSV Exported to   : {results_csv_path}")
    print("=" * 80)
    print("\nEvaluation Discussion & Limitations:")
    print(" - Evaluation on synthetic images verifies mathematical consistency and edge detection robustness.")
    print(" - Classical contour detectors rely on sharp contrast between document boundaries and background.")
    print(" - Low contrast backgrounds (e.g. white sheet on white tablecloth), severe crumples, or non-planar folds")
    print("   benefit from SmartScan's interactive Manual Corner Adjustment fallback feature.")
    print("=" * 80)

if __name__ == "__main__":
    evaluate()
