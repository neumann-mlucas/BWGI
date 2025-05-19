import unittest
import datetime

from decimal import Decimal

from reconcile_accounts import Transaction, reconcile_accounts


def gen_transaction(**kwargs):
    default_args = {
        "Date": datetime.date(2020, 12, 4),
        "Department": "Tecnologia",
        "Value": Decimal("16.0"),
        "Counterpart": "Bitbucket",
        "Status": "MISSING",
    }
    return Transaction(**(default_args | kwargs))


class TestReconcileAccounts(unittest.TestCase):
    def test_empty_files(self):
        """Test reconciliation with empty account"""
        out1, out2 = reconcile_accounts([], [])

        self.assertEqual(len(out1), 0, "First output should be empty")
        self.assertEqual(len(out2), 0, "Second output should be empty")

    def test_one_empty_file(self):
        """Test reconciliation with one empty account"""
        account1 = [gen_transaction()]
        account2 = []

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            out1[0].Status, "MISSING", "Transaction should remain as MISSING"
        )
        self.assertEqual(len(out2), 0, "Second output should be empty")

        out1, out2 = reconcile_accounts(account2, account1)

        self.assertEqual(
            out2[0].Status, "MISSING", "Transaction should remain as MISSING"
        )
        self.assertEqual(len(out1), 0, "Second output should be empty")

    def test_exact_match(self):
        """Test exact matches between accounts"""
        account1 = [gen_transaction()]
        account2 = [gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("FOUND", "FOUND"),
            "Transaction in accounts should be marked as FOUND",
        )

    def test_match_with_day_before(self):
        """Test matching with previous day"""
        account1 = [gen_transaction()]
        account2 = [gen_transaction(Date=datetime.date(2020, 12, 3))]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("FOUND", "FOUND"),
            "Transaction in accounts should be marked as FOUND",
        )

        account1 = [gen_transaction(Date=datetime.date(2020, 12, 3))]
        account2 = [gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("FOUND", "FOUND"),
            "Transaction in accounts should be marked as FOUND",
        )

    def test_match_with_day_after(self):
        """Test matching with next day"""
        account1 = [gen_transaction()]
        account2 = [gen_transaction(Date=datetime.date(2020, 12, 5))]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("FOUND", "FOUND"),
            "Transaction in accounts should be marked as FOUND",
        )

        account1 = [gen_transaction(Date=datetime.date(2020, 12, 5))]
        account2 = [gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("FOUND", "FOUND"),
            "Transaction in accounts should be marked as FOUND",
        )

    def test_no_match_two_days_off(self):
        """Test no matching when dates are more than one day apart"""
        account1 = [gen_transaction(Date=datetime.date(2020, 12, 6))]
        account2 = [gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("MISSING", "MISSING"),
            "Transaction in accounts should be marked as MISSING",
        )

        account1 = [gen_transaction()]
        account2 = [gen_transaction(Date=datetime.date(2020, 12, 6))]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("MISSING", "MISSING"),
            "Transaction in accounts should be marked as MISSING",
        )

    def test_no_match_different_values(self):
        """Test no matching when values are different"""
        account1 = [gen_transaction(Counterpart="AWS")]
        account2 = [gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("MISSING", "MISSING"),
            "Transaction in accounts should be marked as MISSING",
        )

        account1 = [gen_transaction()]
        account2 = [gen_transaction(Counterpart="AWS")]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out2[0].Status),
            ("MISSING", "MISSING"),
            "Transaction in accounts should be marked as MISSING",
        )

    def test_duplicate_transactions_in_one_file(self):
        """Test handling of duplicate transactions in one file"""
        account1 = [gen_transaction(), gen_transaction()]
        account2 = [gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out1[1].Status),
            ("FOUND", "MISSING"),
            "First Transaction in account 1 should be marked as FOUND",
        )
        self.assertEqual(
            out2[0].Status,
            "FOUND",
            "Transaction in account 2 should be marked as FOUND",
        )

        account1 = [gen_transaction()]
        account2 = [gen_transaction(), gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out2[0].Status, out2[1].Status),
            ("FOUND", "MISSING"),
            "First Transaction in account 2 should be marked as FOUND",
        )
        self.assertEqual(
            out1[0].Status,
            "FOUND",
            "Transaction in account 1 should be marked as FOUND",
        )

    def test_multiple_possible_matches_earliest_date(self):
        """Test that earliest date is chosen when multiple matches are possible"""
        account1 = [gen_transaction(), gen_transaction(Date=datetime.date(2020, 12, 3))]
        account2 = [gen_transaction()]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out1[1].Status),
            ("MISSING", "FOUND"),
            "Earlier Transaction in account 1 should be marked as FOUND",
        )
        self.assertEqual(
            out2[0].Status,
            "FOUND",
            "Transaction in account 2 should be marked as FOUND",
        )

        account1 = [gen_transaction()]
        account2 = [gen_transaction(), gen_transaction(Date=datetime.date(2020, 12, 3))]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out2[0].Status, out2[1].Status),
            ("FOUND", "MISSING"),
            "Earlier Transaction in account 2 should be marked as FOUND",
        )
        self.assertEqual(
            out1[0].Status,
            "FOUND",
            "Transaction in account 1 should be marked as FOUND",
        )

    def test_real_example(self):
        """Test a real example with two accounts"""
        account1 = [
            Transaction(
                datetime.date(2020, 12, 4), "Tecnologia", "Bitbucket", Decimal("16.0")
            ),
            Transaction(
                datetime.date(2020, 12, 4), "Jurídico", "LinkSquares", Decimal("60.0")
            ),
            Transaction(
                datetime.date(2020, 12, 5), "Tecnologia", "AWS", Decimal("50.0")
            ),
            Transaction(
                datetime.date(2020, 12, 5), "Tecnologia", "Datadog", Decimal("10.0")
            ),
        ]
        account2 = [
            Transaction(
                datetime.date(2020, 12, 4), "Tecnologia", "Bitbucket", Decimal("16.0")
            ),
            Transaction(
                datetime.date(2020, 12, 5), "Tecnologia", "AWS", Decimal("49.99")
            ),
            Transaction(
                datetime.date(2020, 12, 4), "Jurídico", "LinkSquares", Decimal("60.0")
            ),
            Transaction(
                datetime.date(2020, 12, 6), "Tecnologia", "Datadog", Decimal("10.0")
            ),
            Transaction(
                datetime.date(2020, 12, 6), "Tecnologia", "Datadog", Decimal("10.0")
            ),
        ]

        out1, out2 = reconcile_accounts(account1, account2)

        self.assertEqual(
            (out1[0].Status, out1[1].Status, out1[2].Status, out1[3].Status),
            ("FOUND", "FOUND", "MISSING", "FOUND"),
        )
        self.assertEqual(
            tuple(t.Status for t in out2),
            ("FOUND", "MISSING", "FOUND", "FOUND", "MISSING"),
        )


if __name__ == "__main__":
    unittest.main()
