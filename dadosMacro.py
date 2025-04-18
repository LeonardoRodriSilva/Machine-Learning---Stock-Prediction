from bcb import sgs
import yfinance as yf
import pandas as pd

def get_macro_data(ticker_symbol, start_date, end_date):
    series_codes = {
        'taxa_cambio': 10813, 
        'selic': 432,
        'ipca': 433,
        'pib': 4380
    }
    
    taxa_cambio = sgs.get({'taxa_cambio': series_codes['taxa_cambio']}, start=start_date, end=end_date)
    selic = sgs.get({'selic': series_codes['selic']}, start=start_date, end=end_date)
    ipca = sgs.get({'ipca': series_codes['ipca']}, start=start_date, end=end_date)
    pib = sgs.get({'pib': series_codes['pib']}, start=start_date, end=end_date)
    
    taxa_cambio.rename(columns={'taxa_cambio': 'Taxa_Cambio'}, inplace=True)
    selic.rename(columns={'selic': 'SELIC'}, inplace=True)
    ipca.rename(columns={'ipca': 'IPCA'}, inplace=True)
    pib.rename(columns={'pib': 'PIB'}, inplace=True)
    
    combined_data = taxa_cambio.join([selic, ipca, pib], how='outer')
    combined_data.ffill(inplace=True)
    combined_data.bfill(inplace=True)
    combined_data.interpolate(method='linear', inplace=True)
    
    ticker = yf.Ticker(ticker_symbol)
    precos_diarios = ticker.history(start=start_date, end=end_date)['Close']
    
    combined_data['Preço'] = precos_diarios
    combined_data['Preço'] = combined_data['Preço'].shift(-1)
    combined_data.dropna(inplace=True)
    
    return combined_data