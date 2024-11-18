declare module 'yfinance' {
    interface DownloadOptions {
        start: string;
        end: string;
        interval?: string;
    }
    
    export function download(symbol: string, options: DownloadOptions): Promise<any>;
    export default { download };
} 