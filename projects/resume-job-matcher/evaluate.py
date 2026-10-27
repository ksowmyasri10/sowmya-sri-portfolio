"""Run labeled, synthetic skill-extraction and overlap examples."""

from __future__ import annotations

import json
from pathlib import Path

from matcher import compare_resume_to_job, extract_skills


DATASET = Path(__file__).parent / "data" / "evaluation_cases.json"


def micro_metrics(true_positive: int, false_positive: int, false_negative: int) -> dict[str, float]:
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def evaluate() -> int:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    extraction_tp = extraction_fp = extraction_fn = 0
    overlap_tp = overlap_fp = overlap_fn = 0
    failures: list[str] = []

    for case in cases:
        resume_found = {item["name"] for item in extract_skills(case["resume"])}
        job_found = {item["name"] for item in extract_skills(case["job"])}
        expected_resume = set(case["expected_resume_skills"])
        expected_job = set(case["expected_job_skills"])
        result = compare_resume_to_job(case["resume"], case["job"])
        matched = {item["name"] for item in result["matched"]}
        missing = {item["name"] for item in result["missing"]}

        extraction_tp += len(resume_found & expected_resume) + len(job_found & expected_job)
        extraction_fp += len(resume_found - expected_resume) + len(job_found - expected_job)
        extraction_fn += len(expected_resume - resume_found) + len(expected_job - job_found)

        expected_matched = set(case["expected_matched"])
        overlap_tp += len(matched & expected_matched)
        overlap_fp += len(matched - expected_matched) + len(missing - set(case["expected_missing"]))
        overlap_fn += len(expected_matched - matched) + len(set(case["expected_missing"]) - missing)

        if resume_found != expected_resume:
            failures.append(f"{case['name']}: resume extraction expected {sorted(expected_resume)}, got {sorted(resume_found)}")
        if job_found != expected_job:
            failures.append(f"{case['name']}: job extraction expected {sorted(expected_job)}, got {sorted(job_found)}")
        if matched != expected_matched or missing != set(case["expected_missing"]):
            failures.append(f"{case['name']}: match overlap did not equal expected labels")

    print(f"Labeled synthetic cases: {len(cases)}")
    print(f"Skill extraction micro metrics: {micro_metrics(extraction_tp, extraction_fp, extraction_fn)}")
    print(f"Skill overlap micro metrics: {micro_metrics(overlap_tp, overlap_fp, overlap_fn)}")
    if failures:
        print("Evaluation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("All expected labels matched.")
    print("Note: these small hand-labeled examples are implementation checks, not a general benchmark.")
    return 0


if __name__ == "__main__":
    raise SystemExit(evaluate())
