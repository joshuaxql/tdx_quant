from tqcenter import tq
import pandas as pd
from functools import reduce

tq.initialize(__file__)

ADJUST_NONE = 0
ADJUST_PREV = 1
ADJUST_POST = 2
ADJUST_DICT = {
    ADJUST_NONE:"none",
    ADJUST_PREV:"front",
    ADJUST_POST:"back",
}

def stock_info(symbol: list[str])->dict:
    result = {}
    for stock in symbol:
        fdc = tq.get_stock_info(stock_code=stock, field_list=[])
        result[stock] = fdc
    return result

def daily(symbol: list[str], start_date: str="2025-01-01", end_date: str="", adjust: int=ADJUST_NONE, frequency: str="1d")->pd.DataFrame:
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')
    dividend_type = ADJUST_DICT[adjust]
    df_dict = tq.get_market_data(
        field_list=[],
        stock_list=symbol,
        start_time=start_date,
        end_time=end_date,
        count=-1,
        dividend_type=dividend_type,
        period=frequency,
        fill_data=False
    )
    df_list = []
    for indicator, df in df_dict.items():
        df_reshaped = df.stack().reset_index()
        df_reshaped.columns = ['date', 'symbol', indicator]
        df_list.append(df_reshaped)
    final_df = reduce(
        lambda left, right: pd.merge(left, right, on=['date', 'symbol'], how='inner'),
        df_list
    )
    final_df = final_df.set_index('date')  # 行索引设为日期
    col_order = ['symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount']
    final_df = final_df[col_order]
    final_df.rename(columns={'Open':'open', 'High':'high', 'Low':'low', 'Close':'close', 'Volume':'volume', 'Amount':'amount'}, inplace=True)
    return final_df.dropna()

def financial(symbol: list[str], start_date: str, end_date: str, report_type: str, field: list[str])->dict:
    fd = tq.get_financial_data(
        stock_list=symbol,
        field_list=field,
        start_time=start_date,
        end_time=end_date,
        report_type=report_type)
    return fd

if __name__ == '__main__':
    data = financial(symbol=["000001.SZ", "600000.SH"], start_date='20250101', end_date='20251010', report_type='announce_time', field=['Fn193','Fn194','Fn195','Fn196','Fn197'])
    print(data)