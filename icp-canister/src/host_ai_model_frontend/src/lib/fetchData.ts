import type { TradingData } from "./env";

export enum Api {
    ALPHA_VANTAGE = 1
}

export interface CandleData extends TradingData {
    openTime: Date;
}

interface AlphaVantageDaily {
    'Time Series (Daily)': {
        [key: string]: {
            '1. open': string;
            '2. high': string;
            '3. low': string;
            '4. close': string;
            '5. volume': string;
        }
    }
    'Error Message'?: string;
}

export async function fetchData(
    api: Api,
    symbol: string,
    start: string,
    end: string,
    apiKey: string,
    interval: string = 'Daily'
): Promise<CandleData[]> {
    if (!apiKey?.trim()) {
        throw new Error("API key is required. Get your free key at www.alphavantage.co");
    }

    if (api === Api.ALPHA_VANTAGE) {
        try {
            const response = await fetch(
                `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${symbol}&apikey=${apiKey}&outputsize=full`
            );
            const data = await response.json() as AlphaVantageDaily;
            
            if (data['Error Message']) {
                throw new Error(data['Error Message']);
            }
            
            console.log(data)
            if (!data['Time Series (Daily)']) {
                throw new Error(`No data available for ${symbol}`);
            }

            const startTime = new Date(start).getTime();
            const endTime = new Date(end).getTime();
            
            return Object.entries(data['Time Series (Daily)'])
                .filter(([date]) => {
                    const timestamp = new Date(date).getTime();
                    return timestamp >= startTime && timestamp <= endTime;
                })
                .map(([date, values]) => ({
                    openTime: new Date(date),
                    Open: Number(values['1. open']),
                    High: Number(values['2. high']),
                    Low: Number(values['3. low']),
                    Close: Number(values['4. close']),
                    Volume: Number(values['5. volume']),
                }));

        } catch (e) {
            throw new Error(`Failed to fetch data: ${e instanceof Error ? e.message : String(e)}`);
        }
    } else {
        throw new Error("Invalid API");
    }
}

/**
 * Validates date string format (YYYY-MM-DD)
 * @param dateStr - Date string to validate
 * @returns boolean indicating if the date format is valid
 */
function isValidDateFormat(dateStr: string): boolean {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(dateStr)) return false;
    
    const date = new Date(dateStr);
    return date instanceof Date && !isNaN(date.getTime());
}