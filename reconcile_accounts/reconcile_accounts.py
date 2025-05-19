"""
This script automatically reconciles financial transactions between two data sources. It identifies matching transactions based on Department, Value, and Counterpart, allowing for a 1-day date difference.

examaple usage:

$ cat inp/transactions1.csv
2020-12-04,Tecnologia,16.00,Bitbucket
2020-12-04,Jurídico,60.00,LinkSquares
2020-12-05,Tecnologia,50.00,AWS

$ cat inp/transactions2.csv
2020-12-04,Tecnologia,16.00,Bitbucket
2020-12-05,Tecnologia,49.99,AWS
2020-12-04,Jurídico,60.00,LinkSquares

$ python reconcile_accounts.py inp/transactions1.csv inp/transactions2.csv
Transactions A:
Transaction: 2020-12-04 |   Tecnologia |    Bitbucket | 16.00 | Status:    FOUND
Transaction: 2020-12-04 |     Jurídico |  LinkSquares | 60.00 | Status:    FOUND
Transaction: 2020-12-05 |   Tecnologia |          AWS | 50.00 | Status:  MISSING

Transactions B:
Transaction: 2020-12-04 |   Tecnologia |    Bitbucket | 16.00 | Status:    FOUND
Transaction: 2020-12-05 |   Tecnologia |          AWS | 49.99 | Status:  MISSING
Transaction: 2020-12-04 |     Jurídico |  LinkSquares | 60.00 | Status:    FOUND
"""

import argparse
import csv
import datetime

from operator import attrgetter
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Self


@dataclass
class Transaction:
    Date: datetime.datetime
    Department: str
    Value: float
    Counterpart: str
    Status: str = "MISSING"

    @classmethod
    def to_transction(cls, line: list[str]) -> "Transaction":
        return Transaction(
            Date=datetime.datetime.strptime(line[0], "%Y-%m-%d"),
            Department=line[1],
            Value=float(line[2]),
            Counterpart=line[3],
        )

    def __str__(self) -> str:
        return f"Transaction: {self.Date:%Y-%m-%d} | {self.Department:>12} | {self.Counterpart:>12} | {self.Value:>4.2f} | Status: {self.Status:>8}"

    def __hash__(self) -> int:
        return hash((self.Department, self.Value, self.Counterpart))

    def is_reconciable(self, other: Self) -> bool:
        # map is one to one, if transactions was already reconciled, ignore
        if self.Status == "FOUND" or other.Status == "FOUND":
            return False

        # Department, Value and Conterparty must be the same
        if hash(self) != hash(other):
            return False

        # Date must be within 1 day
        dt = self.Date - other.Date
        if abs(dt.days) > 1:
            return False

        return True


def read_transactions(file_path: str) -> list[Transaction]:
    """Reads transactions from a file and returns a list of Transaction objects."""
    # assuming no need to validate the input
    with Path(file_path).open("r") as f:
        reader = csv.reader(f)
        return [Transaction.to_transction(line) for line in reader]


def reconcile_accounts(
    accountA: list[Transaction], accountB: list[Transaction]
) -> tuple[list[Transaction], list[Transaction]]:
    """Reconciles transactions between two lists of transactions."""

    # create a dictionary to avoid O(n^2) complexity
    dA = defaultdict(list)
    for ta in accountA:
        dA[ta].append(ta)

    for tb in accountB:
        # must check earlier dates first (eairlier trans has priority)
        for ta in sorted(dA[tb], key=attrgetter("Date")):
            status = tb.is_reconciable(ta)
            if status:
                ta.Status = "FOUND" if status else "NOT FOUND"
                tb.Status = "FOUND" if status else "NOT FOUND"
                break
    return accountA, accountB


def main():
    parser = argparse.ArgumentParser(
        description="This scripts reconciles Account transaction data between two file"
    )
    parser.add_argument(
        "files", metavar="FILE", type=str, nargs=2, help="the file(s) to read"
    )
    args = parser.parse_args()

    accountA = read_transactions(args.files[0])
    accountB = read_transactions(args.files[1])

    outA, outB = reconcile_accounts(accountA, accountB)

    print("Transactions A:")
    for transaction in outA:
        print(transaction)

    print()

    print("Transactions B:")
    for transaction in outB:
        print(transaction)


if __name__ == "__main__":
    main()
