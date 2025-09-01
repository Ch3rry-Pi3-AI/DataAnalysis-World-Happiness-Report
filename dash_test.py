from src import load_gold_happiness_data
from src.dash_app.data_access import set_gold_df
from src.dash_app.create_app import dashboard

if __name__ == "__main__":
    gold_df = load_gold_happiness_data(verbose=True)
    set_gold_df(gold_df)
    app = dashboard(enable_pages=True)
    app.run(debug=True)