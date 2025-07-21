/**
 * 日志级别枚举
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error'
}

/**
 * 日志工具类
 */
export class Logger {
  private static instance: Logger;
  private logLevel: LogLevel = LogLevel.INFO;
  private appName: string = 'Mousy';

  private constructor() {
    // 私有构造函数，防止直接实例化
  }

  /**
   * 获取日志工具实例（单例模式）
   */
  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /**
   * 设置日志级别
   * @param level 日志级别
   */
  public setLogLevel(level: LogLevel): void {
    this.logLevel = level;
  }

  /**
   * 设置应用程序名称
   * @param name 应用程序名称
   */
  public setAppName(name: string): void {
    this.appName = name;
  }

  /**
   * 记录调试级别日志
   * @param message 日志消息
   * @param data 附加数据
   */
  public debug(message: string, ...data: any[]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(`[${this.appName}] [DEBUG] ${message}`, ...data);
    }
  }

  /**
   * 记录信息级别日志
   * @param message 日志消息
   * @param data 附加数据
   */
  public info(message: string, ...data: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(`[${this.appName}] [INFO] ${message}`, ...data);
    }
  }

  /**
   * 记录警告级别日志
   * @param message 日志消息
   * @param data 附加数据
   */
  public warn(message: string, ...data: any[]): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(`[${this.appName}] [WARN] ${message}`, ...data);
    }
  }

  /**
   * 记录错误级别日志
   * @param message 日志消息
   * @param error 错误对象
   * @param data 附加数据
   */
  public error(message: string, error?: any, ...data: any[]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      console.error(`[${this.appName}] [ERROR] ${message}`, error, ...data);
    }
  }

  /**
   * 判断是否应该记录指定级别的日志
   * @param level 日志级别
   * @returns 是否应该记录
   */
  private shouldLog(level: LogLevel): boolean {
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
    const currentLevelIndex = levels.indexOf(this.logLevel);
    const targetLevelIndex = levels.indexOf(level);
    return targetLevelIndex >= currentLevelIndex;
  }
}