from __future__ import annotations

import base64
import unittest

from matcher import compare_resume_to_job, extract_skills, validate_text
from server import ClientError, extract_document


class SkillExtractionTests(unittest.TestCase):
    def test_extracts_unique_skills_in_catalog_order(self):
        skills = extract_skills("Python, PYTHON3, sklearn, scikit-learn and SQL")
        self.assertEqual([skill["name"] for skill in skills], ["Python", "SQL", "scikit-learn"])

    def test_does_not_confuse_c_cplusplus_and_csharp(self):
        self.assertEqual(
            [skill["name"] for skill in extract_skills("C, C++ and C#")],
            ["C++", "C#", "C"],
        )
        self.assertNotIn("C", [skill["name"] for skill in extract_skills("C++")])

    def test_expands_common_aliases(self):
        names = {skill["name"] for skill in extract_skills("GenAI, LLMs, RAG, DSA, OOP and NLP")}
        self.assertEqual(
            names,
            {
                "Generative AI",
                "Large Language Models",
                "Retrieval-Augmented Generation",
                "Data Structures and Algorithms",
                "Object-Oriented Programming",
                "Natural Language Processing",
            },
        )

    def test_ignores_phrase_substrings(self):
        names = {skill["name"] for skill in extract_skills("The candidate builds with JavaScript frameworks.")}
        self.assertIn("JavaScript", names)
        self.assertNotIn("Java", names)
        node_names = {skill["name"] for skill in extract_skills("Node.js")}
        self.assertIn("Node.js", node_names)
        self.assertNotIn("JavaScript", node_names)


class MatcherTests(unittest.TestCase):
    def test_transparent_coverage_score(self):
        result = compare_resume_to_job(
            "Python, scikit-learn and pandas",
            "Python, sklearn, SQL and Docker",
        )
        self.assertEqual(result["score"], 50)
        self.assertEqual([item["name"] for item in result["matched"]], ["Python", "scikit-learn"])
        self.assertEqual([item["name"] for item in result["missing"]], ["SQL", "Docker"])
        self.assertEqual([item["name"] for item in result["additional"]], ["pandas"])
        self.assertIn("not an AI judgment", result["disclaimer"])

    def test_no_catalog_skills_yields_no_percentage(self):
        result = compare_resume_to_job("A motivated team player", "Collaborative exciting workplace")
        self.assertIsNone(result["score"])
        self.assertEqual(result["job_skill_count"], 0)

    def test_requires_both_texts(self):
        with self.assertRaisesRegex(ValueError, "Resume"):
            compare_resume_to_job("", "Python")
        with self.assertRaisesRegex(ValueError, "Job description"):
            compare_resume_to_job("Python", " ")

    def test_rejects_non_text_and_oversized_text(self):
        with self.assertRaisesRegex(ValueError, "must be text"):
            validate_text(None, "Resume")
        with self.assertRaisesRegex(ValueError, "60,000"):
            validate_text("x" * 60001, "Resume")


class DocumentExtractionTests(unittest.TestCase):
    def test_extracts_utf8_text_and_markdown(self):
        for filename, text in (("resume.txt", "Python and SQL"), ("posting.md", "# React developer")):
            extracted = extract_document(filename, base64.b64encode(text.encode()).decode())
            self.assertEqual(extracted, text)

    def test_rejects_unexpected_file_types(self):
        with self.assertRaisesRegex(ClientError, "TXT, MD, PDF, and DOCX"):
            extract_document("photo.jpg", base64.b64encode(b"not a resume").decode())

    def test_rejects_invalid_base64(self):
        with self.assertRaisesRegex(ClientError, "decoded"):
            extract_document("resume.txt", "%%%")

    def test_extracts_docx_in_memory(self):
        from docx import Document
        from io import BytesIO

        document = Document()
        document.add_paragraph("Python and TensorFlow")
        buffer = BytesIO()
        document.save(buffer)
        extracted = extract_document(
            "resume.docx",
            base64.b64encode(buffer.getvalue()).decode(),
        )
        self.assertIn("Python and TensorFlow", extracted)


if __name__ == "__main__":
    unittest.main()
