/**
 * 关闭偏好设置接口
 */
export interface ClosePreference {
  action: 'minimize' | 'close';
  rememberChoice: boolean;
  timestamp?: number;
}

/**
 * 用户配置接口
 */
export interface UserConfig {
  // 现有配置...
  auto_accept?: boolean;
  auto_accept_swap_position?: boolean;
  auto_accept_swap_champion?: boolean;
  layout?: {
    card_order?: string[];
  };
  ranked?: any;
  normal?: any;
  aram?: any;
  
  // 新增关闭偏好设置
  closePreference?: ClosePreference;
}