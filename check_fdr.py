try:
    import FinanceDataReader as fdr
    print("FinanceDataReader is installed")
    print(fdr.__version__)
except ImportError:
    print("FinanceDataReader is NOT installed")
