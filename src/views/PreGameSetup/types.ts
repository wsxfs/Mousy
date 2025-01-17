export interface Hero {
  id: number
  name: string
  alias: string
  squarePortraitPath: string
}

export interface ChampionSettings {
  enabled: boolean
  delay: number
  champions: number[]
}

// 定义位置类型
export type PositionKey = 'top' | 'jungle' | 'middle' | 'bottom' | 'support';

// 更新 PositionChampions 接口
export interface PositionChampions {
  top: number[];
  jungle: number[];
  middle: number[];
  bottom: number[];
  support: number[];
}

export interface RankedSettings {
  pick: {
    enabled: boolean
    delay: number
    champions: PositionChampions
  }
  ban: {
    enabled: boolean
    delay: number
    champions: PositionChampions
  }
}

export interface NormalSettings {
  pick: ChampionSettings
  ban: ChampionSettings
}

export interface AramSettings {
  pick: ChampionSettings
}

// 修改 PathImpl 类型
type PathImpl<T, K extends keyof T> = K extends string
  ? T[K] extends Record<string, any>
    ? T[K] extends ArrayLike<any>
      ? K | `${K}.${PathImpl<T[K], Exclude<keyof T[K], keyof any[]>>}`
      : K | `${K}.${PathImpl<T[K], keyof T[K]>}`
    : K
  : never;

// 添加一个特殊的类型来处理动态位置路径
type PositionPath = `ranked.pick.champions.${PositionKey}` | `ranked.ban.champions.${PositionKey}`;

type Path<T> = PathImpl<T, keyof T> | keyof T;

// 更新 FormPath 类型以包含位置路径
export type FormPath = Path<FormState> | PositionPath;

export interface FormState {
  // 基础设置
  auto_accept: boolean
  auto_accept_swap_position: boolean
  auto_accept_swap_champion: boolean
  
  // 游戏模式设置
  ranked: RankedSettings
  normal: NormalSettings
  aram: AramSettings
}

export interface ResourceResponse {
  champion_icons?: Record<string, string>
}

export interface Position {
  key: string
  name: string
}
