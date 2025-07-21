import { app, BrowserWindow } from 'electron';
import { Logger } from '../utils';

/**
 * 单实例检测管理器类
 * 负责检测和处理应用程序的多实例启动
 */
export class SingleInstanceManager {
  private static logger = Logger.getInstance();
  /**
   * 检查是否为单实例
   * @returns 如果是单实例则返回 true，否则返回 false
   */
  public static checkSingleInstance(): boolean {
    // 请求单实例锁
    const gotTheLock = app.requestSingleInstanceLock();

    // 如果无法获取锁，说明已经有一个实例在运行
    if (!gotTheLock) {
      this.logger.info('应用程序已经在运行，退出当前实例');
      app.quit();
      return false;
    }

    // 设置第二个实例启动时的处理函数
    app.on('second-instance', (_event, _commandLine, _workingDirectory) => {
      this.handleSecondInstance();
    });

    return true;
  }

  /**
   * 处理第二个实例启动的情况
   */
  public static handleSecondInstance(): void {
    try {
      // 获取主窗口
      const windows = BrowserWindow.getAllWindows();
      if (windows.length > 0) {
        const mainWindow = windows[0];

        // 如果窗口最小化或隐藏，则恢复显示
        if (mainWindow.isMinimized()) {
          mainWindow.restore();
        }
        if (!mainWindow.isVisible()) {
          mainWindow.show();
        }

        // 将窗口置于前台
        mainWindow.focus();

        // 提供视觉反馈
        mainWindow.flashFrame(true);
        setTimeout(() => {
          mainWindow.flashFrame(false);
        }, 1000);
      }
    } catch (error) {
      this.logger.error('Error handling second instance:', error);
    }
  }
}