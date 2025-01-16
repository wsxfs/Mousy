export interface Hero {
  id: number
  name: string
  alias: string
  squarePortraitPath: string
}

export interface FormState {
  auto_accept: boolean
  auto_pick_champions: number[]
  auto_ban_champions: number[]
  auto_accept_swap_position: boolean
  auto_accept_swap_champion: boolean
  aram_auto_pick_enabled: boolean
  aram_auto_pick_champions: number[]
  aram_auto_pick_delay: number
  auto_pick_enabled: boolean
  auto_pick_delay: number
  auto_ban_enabled: boolean
  auto_ban_delay: number
  ranked_auto_ban_enabled: boolean
  ranked_auto_ban_champions: number[]
  ranked_pick_enabled: boolean
  ranked_pick_delay: number
  ranked_pick_champions: number[]
  ranked_ban_enabled: boolean
  ranked_ban_delay: number
  ranked_ban_champions: number[]
  ranked_pick_champions_top: number[]
  ranked_pick_champions_jungle: number[]
  ranked_pick_champions_middle: number[]
  ranked_pick_champions_bottom: number[]
  ranked_pick_champions_support: number[]
  ranked_ban_champions_top: number[]
  ranked_ban_champions_jungle: number[]
  ranked_ban_champions_middle: number[]
  ranked_ban_champions_bottom: number[]
  ranked_ban_champions_support: number[]
}

export interface ResourceResponse {
  champion_icons?: Record<string, string>
}

export interface Position {
  key: string
  name: string
}
