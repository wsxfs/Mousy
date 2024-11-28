// 基础统计数据接口
interface PlayerStats {
  assists: number
  deaths: number
  kills: number
  goldEarned: number
  totalMinionsKilled: number
  win: boolean
  item0: number
  item1: number
  item2: number
  item3: number
  item4: number
  item5: number
  item6: number
  totalDamageDealtToChampions?: number
  [key: string]: any
}

// 参与者接口
interface Participant {
  championId: number
  participantId: number
  spell1Id: number
  spell2Id: number
  stats: PlayerStats
  teamId: number
}

// 参与者身份接口
interface ParticipantIdentity {
  participantId: number
  player?: {
    puuid: string
    gameName: string
  }
}

// 队伍接口
interface Team {
  teamId: number
  win: string
  towerKills?: number
}

// 游戏接口
interface Game {
  gameId: number
  gameCreation: number
  gameDuration: number
  gameMode: string
  mapId: number
  participants: Participant[]
  participantIdentities: ParticipantIdentity[]
  teams: Team[]
}

// 资源响应接口
interface ResourceResponse {
  champion_icons?: Record<string | number, string>
  spell_icons?: Record<string | number, string>
  item_icons?: Record<string | number, string>
}

// 标签页项接口
interface MatchTab {
  title: string
  name: string
  gameId?: number
  puuid?: string
}

// 游戏模式映射类型
type GameModeMap = Record<string, string>

// 导出所有类型
export type {
  PlayerStats,
  Participant,
  ParticipantIdentity,
  Team,
  Game,
  ResourceResponse,
  MatchTab,
  GameModeMap
}