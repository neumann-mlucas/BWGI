### Reconcile Accounts

This script automatically reconciles financial transactions between two data sources. It identifies matching transactions based on Department, Value, and Counterpart, allowing for a 1-day date difference.


#### Usage:

```bash
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
```
