import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from datastore.loader import DataStore
from datastore import query
import pandas as pd


# Point this at your actual folder with the data files
DATA_DIR = "."

def main():
    store = DataStore(DATA_DIR)
    store.load_all()
    print("Loaded feeds rows:", len(store.feeds_df))
    print("Unique FEED_ID:", store.feeds_df['FEED_ID'].nunique())
    print("Encoder params:", store.get_encoder_params().model_dump())
    print("Decoder params:", store.get_decoder_params().model_dump())

    # Example 1: Pacific area best clarity
    if "THEATER" in store.feeds_df.columns:
        try:
            top = query.find_best_clarity_in_theater(store, "Pacific", top_k=5)
            print("\nTop clarity in Pacific:")
            print(top.to_string(index=False))
        except Exception as e:
            print("Ranking example failed:", e)

    # Example 2: Downtown min 60 fps if present
    try:
        df = query.feeds_with_constraints(store, "Downtown", 60)
        print("\nDowntown with min 60 fps:")
        print(df.head(5).to_string(index=False))
    except Exception as e:
        print("Constraint example failed:", e)

if __name__ == "__main__":
    main()
