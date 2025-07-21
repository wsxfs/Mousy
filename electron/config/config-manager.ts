import axios from 'axios';
import { ClosePreference, UserConfig } from './types';
import { Logger } from '../utils';

/**
 * 配置管理器类
 * 负责与后端 API 交互，管理用户配置
 */
export class ConfigManager {
  private static instance: ConfigManager;
  private baseUrl: string = 'http://127.0.0.1:8001';
  private config: UserConfig | null = null;
  private logger = Logger.getInstance();

  private constructor() {
    // 私有构造函数，防止直接实例化
  }

  /**
   * 获取配置管理器实例（单例模式）
   */
  public static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  /**
   * 设置 API 基础 URL
   * @param url API 基础 URL
   */
  public setBaseUrl(url: string): void {
    this.baseUrl = url;
  }

  /**
   * 从后端获取完整配置
   */
  public async fetchConfig(): Promise<UserConfig> {
    try {
      const response = await axios.get<UserConfig>(`${this.baseUrl}/api/user_settings/get`);
      this.config = response.data;
      return this.config;
    } catch (error) {
      this.logger.error('Failed to fetch config:', error);
      throw error;
    }
  }

  /**
   * 获取当前配置（如果尚未加载则从后端获取）
   */
  public async getConfig(): Promise<UserConfig> {
    if (!this.config) {
      return this.fetchConfig();
    }
    return this.config;
  }

  /**
   * 更新配置到后端
   * @param config 更新后的配置
   */
  public async updateConfig(config: UserConfig): Promise<void> {
    try {
      await axios.post(`${this.baseUrl}/api/user_settings/update_all`, config);
      this.config = config;
    } catch (error) {
      this.logger.error('Failed to update config:', error);
      throw error;
    }
  }

  /**
   * 获取关闭偏好设置
   */
  public async getClosePreference(): Promise<ClosePreference | null> {
    try {
      // 强制从后端获取最新配置，不使用缓存
      await this.fetchConfig();
      
      // 如果没有设置或者action为空，返回null
      if (!this.config?.closePreference || !this.config.closePreference.action) {
        return null;
      }
      return this.config.closePreference;
    } catch (error) {
      this.logger.error('Failed to get close preference:', error);
      return null;
    }
  }

  /**
   * 保存关闭偏好设置
   * @param preference 关闭偏好设置
   */
  public async saveClosePreference(preference: ClosePreference): Promise<void> {
    const config = await this.getConfig();
    config.closePreference = {
      ...preference,
      timestamp: Date.now()
    };
    await this.updateConfig(config);
  }

  /**
   * 清除关闭偏好设置
   */
  public async clearClosePreference(): Promise<void> {
    const config = await this.getConfig();
    if (config.closePreference) {
      delete config.closePreference;
      await this.updateConfig(config);
    }
  }
}