import csv
import random
from pathlib import Path

# ---------------- CONFIG ----------------
STUDENTS_CSV = Path("src/database/Students.csv")
SUBJECTS_CSV = Path("src/database/Subjects.csv")
OUTPUT_REGISTERED = Path("src/database/RegisteredSubject.csv")

GRADE_BUCKETS = ["A", "B+", "B", "C+", "C", "D+", "D", "F"]
GRADE_PROBS   = [0.55, 0.15, 0.10, 0.08, 0.07, 0.05, 0, 0]


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["StudentID", "SubjectID", "Grade"])
        w.writerows(rows)


def generate_registered_subject(students, subjects, seed=123):
    if seed:
        random.seed(seed)

    student_ids = [s["StudentID"].strip() for s in students]
    subject_ids = [s["SubjectID"].strip() for s in subjects]

    rows = []
    for sid in student_ids:
        # ให้แต่ละคนลง 4–9 วิชาแบบสุ่ม
        n_subjects = random.randint(4, 9)
        chosen = random.sample(subject_ids, k=n_subjects)
        for subj in chosen:
            grade = random.choices(GRADE_BUCKETS, weights=GRADE_PROBS, k=1)[0]
            rows.append((sid, subj, grade))
    return rows


if __name__ == "__main__":
    students = read_csv(STUDENTS_CSV)
    subjects = read_csv(SUBJECTS_CSV)

    data = generate_registered_subject(students, subjects, seed=42)
    write_csv(OUTPUT_REGISTERED, data)
    print(f"Exported {len(data)} rows -> {OUTPUT_REGISTERED}")
