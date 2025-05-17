type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
    timestamp: string;
    level: LogLevel;
    message: string;
    data?: any;
}

class Logger {
    private static instance: Logger;
    private logs: LogEntry[] = [];
    private readonly maxLogs: number = 1000;

    private constructor() {}

    static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    private log(level: LogLevel, message: string, data?: any) {
        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            level,
            message,
            data
        };

        // Add to in-memory logs
        this.logs.push(entry);
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }

        // Format console output
        const formattedMessage = `[${entry.timestamp}] ${level.toUpperCase()}: ${message}`;
        
        // Log to console with appropriate level and styling
        switch (level) {
            case 'debug':
                console.debug(formattedMessage, data || '');
                break;
            case 'info':
                console.info('%c' + formattedMessage, 'color: #0066cc', data || '');
                break;
            case 'warn':
                console.warn(formattedMessage, data || '');
                break;
            case 'error':
                console.error(formattedMessage, data || '');
                break;
        }
    }

    debug(message: string, data?: any) {
        this.log('debug', message, data);
    }

    info(message: string, data?: any) {
        this.log('info', message, data);
    }

    warn(message: string, data?: any) {
        this.log('warn', message, data);
    }

    error(message: string, data?: any) {
        this.log('error', message, data);
    }

    getLogs(): LogEntry[] {
        return [...this.logs];
    }

    clearLogs() {
        this.logs = [];
    }
}

export const logger = Logger.getInstance(); 