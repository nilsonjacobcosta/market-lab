"""Catálogo de ativos do painel.

Cada item: (secao, nome, ticker_yahoo, valor_captura, var_captura_pct, inverter, destaque)
- valor_captura / var_captura_pct: último valor transcrito da captura de 10/11/2026 (usado só se a coleta falhar).
- inverter: True quando a convenção da captura é o inverso da do Yahoo (ex.: USD/EUR = EUR por USD).
- ticker None: sem fonte automática; a linha aparece com o valor da captura e marcada como tal.
"""

SECOES = [
    "Índices americanos",
    "Índices europeus",
    "Índices asiáticos",
    "Cesta DX",
    "Commodities",
    "Outros ativos",
    "Mundo (USD contra moedas)",
    "Emergentes (USD contra moedas)",
]

ITENS = [
    # Destaques (cartões) -- entradas de "Outros ativos"/"Commodities"/"Cesta DX" marcadas com destaque=True
    ("Destaques", "Índice Futuro (Ibovespa)", "WIN=F", 174900.0, 0.42, False, True),
    ("Destaques", "Índice DX (dólar)", "DX-Y.NYB", 101.698, 0.18, False, True),
    ("Destaques", "S&P 500 Futuro", "ES=F", 7554.0, 0.06, False, True),
    ("Destaques", "Petróleo WTI (US$)", "CL=F", 84.78, -2.36, False, True),
    ("Destaques", "BCOM (Bloomberg Commodity)", None, 131.9261, -1.31, False, True),
    ("Destaques", "CME FedWatch (faixa de juros)", None, None, None, False, True),

    # Índices americanos
    ("Índices americanos", "Ibovespa", "^BVSP", 172817, 0.34, False, False),
    ("Índices americanos", "S&P/TSX", "^GSPTSE", 36446.26, 1.84, False, False),
    ("Índices americanos", "Dow Jones", "^DJI", 52389.75, 2.15, False, False),
    ("Índices americanos", "Nasdaq Composto", "^IXIC", 25253.14, 2.74, False, False),
    ("Índices americanos", "Russell 2000", "^RUT", 2840.81, 3.15, False, False),
    ("Índices americanos", "S&P 500", "^GSPC", 7549.94, 2.35, False, False),
    ("Índices americanos", "S&P 500 VIX", "^VIX", 20.09, 0.85, False, False),
    ("Índices americanos", "S&P/BMV IPC", "^MXX", 71855.64, 0.65, False, False),

    # Índices europeus
    ("Índices europeus", "DAX", "^GDAXI", 26594.74, 1.25, False, False),
    ("Índices europeus", "IBEX 35", "^IBEX", 20038.68, 1.50, False, False),
    ("Índices europeus", "CAC 40", "^FCHI", 8329.38, 1.17, False, False),
    ("Índices europeus", "FTSE MIB", "FTSEMIB.MI", 52042.50, 1.25, False, False),
    ("Índices europeus", "WIG20", "^WIG20", 4180.40, 0.36, False, False),
    ("Índices europeus", "FTSE 100", "^FTSE", 10832.86, 0.46, False, False),
    ("Índices europeus", "MOEX", "IMOEX.ME", 2459.12, -0.57, False, False),
    ("Índices europeus", "OMXS30", "^OMXS30", 3343.05, 1.00, False, False),
    ("Índices europeus", "SMI", "^SSMI", 15061.60, 0.77, False, False),
    ("Índices europeus", "Euro Stoxx 50", "^STOXX50E", 6362.95, 1.15, False, False),

    # Índices asiáticos
    ("Índices asiáticos", "Tadawul All Share", "^TASI.SR", 10168.10, 0.61, False, False),
    ("Índices asiáticos", "S&P/ASX 200", "^AXJO", 9129.00, 1.10, False, False),
    ("Índices asiáticos", "Shanghai", "000001.SS", 3663.72, 0.08, False, False),
    ("Índices asiáticos", "SZSE Component", "399001.SZ", 11241.54, 0.86, False, False),
    ("Índices asiáticos", "KOSPI", "^KS11", 5239.00, 4.39, False, False),
    ("Índices asiáticos", "Hang Seng", "^HSI", 24557.04, 0.44, False, False),
    ("Índices asiáticos", "BSE Sensex", "^BSESN", 81106.65, 0.13, False, False),
    ("Índices asiáticos", "Nikkei 225", "^N225", 60459.58, 2.87, False, False),
    ("Índices asiáticos", "BIST 100", "XU100.IS", 11703.31, -0.08, False, False),

    # Cesta DX
    ("Cesta DX", "DX", "DX-Y.NYB", 101.698, 0.16, False, False),
    ("Cesta DX", "USD/EUR", "EURUSD=X", 0.8921, 0.14, True, False),
    ("Cesta DX", "USD/JPY", "JPY=X", 158.22, 0.20, False, False),
    ("Cesta DX", "USD/GBP", "GBPUSD=X", 0.7452, 0.17, True, False),
    ("Cesta DX", "USD/CAD", "CAD=X", 1.4136, 0.13, False, False),
    ("Cesta DX", "USD/SEK", "SEK=X", 9.8058, 0.20, False, False),
    ("Cesta DX", "USD/CHF", "CHF=X", 0.8209, 0.17, False, False),

    # Commodities
    ("Commodities", "Minério de ferro", None, 684.0, -0.29, False, False),
    ("Commodities", "Cobre", "HG=F", 6.2803, -1.02, False, False),
    ("Commodities", "Prata", "SI=F", 52.285, -0.77, False, False),
    ("Commodities", "Ouro", "GC=F", 4080.97, -0.81, False, False),
    ("Commodities", "Petróleo Brent", "BZ=F", 89.92, -2.84, False, False),
    ("Commodities", "Petróleo WTI", "CL=F", 84.78, -2.35, False, False),

    # Outros ativos
    ("Outros ativos", "S&P 500 Futuro", "ES=F", 7554.0, 0.06, False, False),
    ("Outros ativos", "Nasdaq 100 Futuro", "NQ=F", 27819.9, -0.31, False, False),
    ("Outros ativos", "Dow Futuro", "YM=F", None, 0.39, False, False),
    ("Outros ativos", "Russell 2000 Futuro", "RTY=F", 2840.1, -0.02, False, False),
    ("Outros ativos", "US 2 anos (%)", None, 4.630, 1.83, False, False),
    ("Outros ativos", "US 10 anos (%)", "^TNX", 4.905, 0.86, False, False),
    ("Outros ativos", "GB 10 anos (%)", None, 5.1130, -0.35, False, False),
    ("Outros ativos", "DE 10 anos (%)", None, 3.2412, -0.80, False, False),
    ("Outros ativos", "JP 10 anos (%)", None, 2.695, 1.13, False, False),
    ("Outros ativos", "CN 10 anos (%)", None, 1.584, -1.00, False, False),
    ("Outros ativos", "EWZ (ETF Brasil)", "EWZ", 32.64, 0.09, False, False),
    ("Outros ativos", "Índice Futuro (Ibovespa)", "WIN=F", 174900.0, 0.42, False, False),
    ("Outros ativos", "CDS Brasil 5 anos (pb)", None, 145.6, -1.71, False, False),
    ("Outros ativos", "Bitcoin", "BTC-USD", 74304.8, -0.54, False, False),

    # Mundo (USD contra moedas): ticker USD{CODIGO}=X, convenção CODIGO por USD
    ("Mundo (USD contra moedas)", "NIO", "USDNIO=X", 36.8010, 0.52, False, False),
    ("Mundo (USD contra moedas)", "DOP", "USDDOP=X", 60.657, 0.01, False, False),
    ("Mundo (USD contra moedas)", "UYU", "USDUYU=X", 40.4645, 0.35, False, False),
    ("Mundo (USD contra moedas)", "CRC", "USDCRC=X", 452.28, 1.28, False, False),
    ("Mundo (USD contra moedas)", "PEN", "USDPEN=X", 3.4083, -0.99, False, False),
    ("Mundo (USD contra moedas)", "JMD", "USDJMD=X", 158.722, -0.08, False, False),
    ("Mundo (USD contra moedas)", "PYG", "USDPYG=X", 6173.61, -1.23, False, False),
    ("Mundo (USD contra moedas)", "CZK", "USDCZK=X", 21.7061, 0.18, False, False),
    ("Mundo (USD contra moedas)", "DKK", "USDDKK=X", 6.6685, 0.13, False, False),
    ("Mundo (USD contra moedas)", "HUF", "USDHUF=X", 323.77, 0.42, False, False),
    ("Mundo (USD contra moedas)", "NOK", "USDNOK=X", 9.4719, 0.84, False, False),
    ("Mundo (USD contra moedas)", "NGN", "USDNGN=X", 1348.260, 0.14, False, False),
    ("Mundo (USD contra moedas)", "EGP", "USDEGP=X", 53.25, -1.08, False, False),
    ("Mundo (USD contra moedas)", "PHP", "USDPHP=X", 62.875, -0.29, False, False),
    ("Mundo (USD contra moedas)", "ILS", "USDILS=X", 3.1673, 0.54, False, False),
    ("Mundo (USD contra moedas)", "TWD", "USDTWD=X", 32.954, 0.54, False, False),
    ("Mundo (USD contra moedas)", "HKD", "USDHKD=X", 7.8446, 0.04, False, False),
    ("Mundo (USD contra moedas)", "NZD", "USDNZD=X", 1.7775, 0.09, False, False),

    # Emergentes (USD contra moedas)
    ("Emergentes (USD contra moedas)", "ARS", "USDARS=X", 1545.68, 0.00, False, False),
    ("Emergentes (USD contra moedas)", "AUD", "USDAUD=X", 1.4484, 0.33, False, False),
    ("Emergentes (USD contra moedas)", "BRL", "USDBRL=X", 5.5531, 0.82, False, False),
    ("Emergentes (USD contra moedas)", "CLP", "USDCLP=X", 970.55, 0.37, False, False),
    ("Emergentes (USD contra moedas)", "CNY", "USDCNY=X", 6.6704, -0.03, False, False),
    ("Emergentes (USD contra moedas)", "COP", "USDCOP=X", 3277.34, -0.05, False, False),
    ("Emergentes (USD contra moedas)", "INR", "USDINR=X", 93.722, 0.00, False, False),
    ("Emergentes (USD contra moedas)", "KRW", "USDKRW=X", 1338.23, -0.15, False, False),
    ("Emergentes (USD contra moedas)", "MXN", "USDMXN=X", 18.5553, 0.15, False, False),
    ("Emergentes (USD contra moedas)", "RUB", "USDRUB=X", 82.9066, 0.50, False, False),
    ("Emergentes (USD contra moedas)", "SAR", "USDSAR=X", 3.7534, 0.00, False, False),
    ("Emergentes (USD contra moedas)", "TRY", "USDTRY=X", 50.2326, 0.12, False, False),
    ("Emergentes (USD contra moedas)", "ZAR", "USDZAR=X", 16.3922, 0.13, False, False),
]
