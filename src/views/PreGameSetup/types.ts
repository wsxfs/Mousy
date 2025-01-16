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

export interface PositionChampions {
  top: number[]
  jungle: number[]
  middle: number[]
  bottom: number[]
  support: number[]
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
