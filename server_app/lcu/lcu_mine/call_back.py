from server_app.new_services.lcu import Http2Lcu
from server_app.new_services.user_config.user_config import UserConfig

class CallBack:
    @staticmethod
    def get_auto_accept_match(h2lcu: Http2Lcu, if_auto_accept: bool):
        async def auto_accept_match(json_data):
            print(f"{json_data=}")
            if json_data["data"] == "ReadyCheck":
                await h2lcu.accept_matchmaking()
                print("接受匹配")
        if if_auto_accept:
            return auto_accept_match
        else:
            return None
    
    # def get_auto_champ_select(h2lcu: Http2Lcu, auto_select_champion_id_list: list):
    #     async def auto_champ_select(json_data):
    #         print(f"{json_data=}")
    #         if json_data["data"] == "ChampSelect":
    #             await h2lcu.select_champion(auto_select_champion_id_list)
    #             print("自动选择英雄")

    @staticmethod
    def get_all_call_back(h2lcu: Http2Lcu, user_config: UserConfig):
        auto_accept_match = CallBack.get_auto_accept_match(h2lcu, user_config.get_setting["auto_accept"])
        # auto_champ_select = CallBack.get_auto_champ_select(h2lcu, user_config.settings["auto_select_champion_id_list"])
        return auto_accept_match
