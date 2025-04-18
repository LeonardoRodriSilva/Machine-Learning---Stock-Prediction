import yfinance as yf
import pandas as pd

def get_micro_data(ticker_symbol, start_date, end_date):
    ticker = yf.Ticker(ticker_symbol)
    
    dados = {
        'Preço': yf.download(tickers=ticker_symbol, start=start_date, end=end_date),
        'Info': ticker.info,
        'Financeiros': {
            'Balanço': ticker.balance_sheet,
            'DRE': ticker.financials,
            'Fluxo_Caixa': ticker.cashflow
        }
    }
    
    lucro_liquido = dados['Financeiros']['DRE'].loc['Net Income']
    patrimonio_liquido = dados['Financeiros']['Balanço'].loc['Total Equity Gross Minority Interest']
    total_ativos = dados['Financeiros']['Balanço'].loc['Total Assets']
    num_acoes = dados['Financeiros']['Balanço'].loc['Ordinary Shares Number']
    receita_total = dados['Financeiros']['DRE'].loc['Total Revenue']
    precos_diarios = dados['Preço']['Close']
  
    pl_medio = pd.Series(index=patrimonio_liquido.index)
    for i in range(len(patrimonio_liquido)):
        if i == 0:
            pl_medio.iloc[i] = patrimonio_liquido.iloc[1]
        else:
            pl_medio.iloc[i] = patrimonio_liquido.iloc[i:i+2].mean()
    
    indicadores = pd.DataFrame(index=lucro_liquido.index)
    
    indicadores['ROE'] = lucro_liquido / pl_medio
    indicadores['ROA'] = lucro_liquido / total_ativos
    indicadores['VP'] = patrimonio_liquido / num_acoes
    indicadores['ML'] = lucro_liquido / receita_total
    
    precos_diarios.index = pd.to_datetime(precos_diarios.index)
    precos_anuais = precos_diarios.groupby(precos_diarios.index.year).last()
    precos_anuais.index = pd.to_datetime(precos_anuais.index.astype(str) + '-12-31')
    precos_anuais = precos_anuais.reindex(lucro_liquido.index)
    
    lpa = lucro_liquido / num_acoes
    indicadores['P/L'] = precos_anuais / lpa
    indicadores['P/VPA'] = precos_anuais / indicadores['VP']
    
    # Ajuste: Deslocar os indicadores em 1 dia
    indicadores_shifted = indicadores.shift(1)  # Shift de 1 dia
    
    # Combinar preços diários com indicadores deslocados
    dados_combinados = pd.DataFrame({
        'Preço': precos_diarios,
        'ROE': indicadores_shifted['ROE'],
        'ROA': indicadores_shifted['ROA'],
        'VP': indicadores_shifted['VP'],
        'ML': indicadores_shifted['ML'],
        'P/L': indicadores_shifted['P/L'],
        'P/VPA': indicadores_shifted['P/VPA']
    })
    
    # Remover linhas com valores NaN (devido ao shift)
    dados_combinados.dropna(inplace=True)
    
    return dados_combinados

# Exemplo de uso
dados = get_micro_data('PETR4.SA', '2015-01-01', '2020-01-01')
print(dados)