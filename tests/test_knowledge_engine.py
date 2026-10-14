import unittest
from datetime import date

from knowledge_engine import KnowledgeEngine


class KnowledgeEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = KnowledgeEngine(today=date(2026, 10, 14))

    def test_same_question_returns_company_specific_answers(self):
        question = "Quy định nghỉ phép của tôi như thế nào?"
        pay = self.engine.ask("user-an", question)
        ads = self.engine.ask("user-binh", question)

        self.assertEqual(pay.status, "answered")
        self.assertEqual(ads.status, "answered")
        self.assertIn("14 ngày", pay.answer)
        self.assertIn("12 ngày", ads.answer)
        self.assertNotEqual(pay.citations[0]["document_id"], ads.citations[0]["document_id"])

    def test_expired_version_is_not_used(self):
        result = self.engine.ask("user-an", "Tôi có bao nhiêu ngày phép năm?")
        self.assertEqual(result.citations[0]["version"], "2.0")
        self.assertNotEqual(result.citations[0]["document_id"], "PAY-LEAVE-OLD")

    def test_department_policy_is_available_to_matching_department(self):
        result = self.engine.ask("user-an", "Tôi được làm từ xa mấy ngày?")
        self.assertEqual(result.status, "answered")
        self.assertIn("2 ngày", result.answer)

    def test_restricted_document_does_not_leak(self):
        result = self.engine.ask("user-an", "Quy trình chốt bảng lương thế nào?")
        self.assertEqual(result.status, "refused")
        self.assertEqual(result.citations, [])
        serialized = str(result.as_dict())
        self.assertNotIn("C&B-07", serialized)
        self.assertNotIn("GRP-PAYROLL-ADMIN", serialized)

    def test_authorized_hr_admin_can_access_restricted_document(self):
        result = self.engine.ask("user-chi", "Quy trình chốt payroll thế nào?")
        self.assertEqual(result.status, "answered")
        self.assertEqual(result.citations[0]["document_id"], "GRP-PAYROLL-ADMIN")

    def test_conflicting_current_documents_trigger_safe_refusal(self):
        result = self.engine.ask("user-binh", "Mức công tác phí là bao nhiêu?")
        self.assertEqual(result.status, "refused")
        self.assertEqual(result.trace["reason"], "CONFLICTING_EVIDENCE")
        self.assertEqual(len(result.citations), 2)

    def test_missing_knowledge_triggers_refusal(self):
        result = self.engine.ask("user-an", "Quy định mua laptop cá nhân thế nào?")
        self.assertEqual(result.status, "refused")
        self.assertEqual(result.trace["reason"], "INSUFFICIENT_EVIDENCE")

    def test_unknown_identity_is_refused(self):
        result = self.engine.ask("attacker", "Quy trình chốt bảng lương thế nào?")
        self.assertEqual(result.status, "refused")
        self.assertEqual(result.trace["reason"], "UNKNOWN_USER")


if __name__ == "__main__":
    unittest.main()
