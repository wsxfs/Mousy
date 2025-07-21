import { BrowserWindow } from 'electron';
import { ConfigManager } from '../config/config-manager';
import { ClosePreference } from '../config/types';
import { Logger } from '../utils';

/**
 * 关闭行为管理器类
 * 负责处理窗口关闭事件和关闭偏好设置
 */
export class CloseActionManager {
  private static configManager = ConfigManager.getInstance();
  private static logger = Logger.getInstance();

  /**
   * 获取关闭偏好设置
   */
  public static async getClosePreference(): Promise<ClosePreference | null> {
    try {
      return await this.configManager.getClosePreference();
    } catch (error) {
      this.logger.error('Failed to get close preference:', error);
      return null;
    }
  }

  /**
   * 保存关闭偏好设置
   * @param preference 关闭偏好设置
   */
  public static async saveClosePreference(preference: ClosePreference): Promise<void> {
    try {
      this.logger.info('保存关闭偏好设置:', preference);
      await this.configManager.saveClosePreference(preference);
      
      // 记录日志，方便调试
      const savedPreference = await this.getClosePreference();
      this.logger.info('保存后的关闭偏好设置:', savedPreference);
    } catch (error) {
      this.logger.error('Failed to save close preference:', error);
    }
  }

  /**
   * 清除关闭偏好设置
   */
  public static async clearClosePreference(): Promise<void> {
    try {
      await this.configManager.clearClosePreference();
    } catch (error) {
      this.logger.error('Failed to clear close preference:', error);
    }
  }

  /**
   * 处理窗口关闭事件
   * @param event 事件对象
   * @param window 窗口对象
   */
  public static async handleWindowClose(event: Electron.Event, window: BrowserWindow): Promise<void> {
    // 阻止默认关闭行为
    event.preventDefault();

    try {
      // 获取关闭偏好设置
      const preference = await this.getClosePreference();
      this.logger.info('获取到的关闭偏好设置:', preference);

      // 如果有偏好设置且记住选择，则直接执行相应操作
      if (preference && preference.rememberChoice) {
        if (preference.action === 'minimize') {
          this.logger.info('根据偏好设置最小化窗口');
          window.hide();
          return;
        } else if (preference.action === 'close') {
          this.logger.info('根据偏好设置关闭应用程序');
          window.destroy();
          return;
        }
        // 如果 action 是 'ask' 或其他值，继续显示确认对话框
        this.logger.info('偏好设置为询问或未知值，显示确认对话框');
      } else {
        this.logger.info('没有偏好设置或不记住选择，显示确认对话框');
      }

      // 显示确认对话框
      this.showCloseConfirmationDialog(window);
    } catch (error) {
      this.logger.error('Error handling window close:', error);
      // 出错时默认最小化到托盘
      window.hide();
    }
  }

  /**
   * 显示关闭确认对话框
   * @param window 窗口对象
   */
  private static async showCloseConfirmationDialog(window: BrowserWindow): Promise<void> {
    try {
      // 检查窗口是否可见，如果不可见则先显示
      if (!window.isVisible()) {
        window.show();
        // 等待窗口完全显示
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // 检查渲染进程是否已经加载完成
      if (window.webContents.isLoading()) {
        this.logger.warn('WebContents is still loading, defaulting to minimize');
        // 如果渲染进程还在加载，直接最小化到托盘
        window.hide();
        return;
      }

      // 尝试使用渲染进程的对话框
      this.logger.info('Sending show-close-dialog to renderer');
      window.webContents.send('show-close-dialog');
      
      // 移除超时机制，让用户有足够的时间做出选择

      // 注意：不在这里处理结果，结果将由主进程的 IPC 监听器处理
    } catch (error) {
      this.logger.error('Error showing close confirmation dialog:', error);
      // 出错时默认最小化到托盘
      window.hide();
    }
  }
}