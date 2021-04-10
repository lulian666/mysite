# coding:utf-8
import configparser
import os

class Read_config:
    def get_value(self, section, item):
        root = os.path.abspath('.') #获取当前工作目录路径
        filepath = os.path.join(root, 'apitest/config/config_kuainiao.ini')
        # print(filepath)
        cf = configparser.ConfigParser()
        cf.read(filepath)

        if item == 'favours':
            return ['MU_YING_YONG_PIN', 'NAN_ZHUANG', 'GE_HU_QING_JIE_NAN']
        elif item == "configs":
            return ["girlSuggestions", "boySuggestions", "prologueSuggestions", "emojis", "questions", "lonelyTags", "titleTags", "outlooksOnLove", "socialActivities", "conversationToasts"]
        elif item == 'sportHobbies':
            return ["1", "2", "3", "4"]
        elif item == 'visitedCities':
            return ["伦敦", "北海道", "大理", "巴塞罗那"]
        elif item == 'favMovies':
            return ["11", "22", "33", "44"]
        elif item == 'socialActivities':
            return ["分享表情包"]
        elif item == 'outlooksOnLove':
            return ["5eb281255cec6c8287024e54", "5eb281255cec6c8287024e4f", "5eb281255cec6c8287024e4c"]
        elif item == 'hometown':
            return {"city": "滁州","province": "安徽"}
        elif item == 'interestedEvents':
            return []
        elif item == 'interestedEvent':
            return []
        elif item == 'photos':
            return []
        elif item == 'file':
            return []
        elif item == 'images':
            return []
        elif item == 'replytocommentid':
            return None
        elif item == 'lonelyTag':
            return {"id": "5eb2cc955cec6c8287024ec0","name": "终于想谈恋爱了"}
        elif item == 'outlooksOnLove':
            return [{
                "id": "5eb281255cec6c8287024e4e",
                "name": "精神物质对等",
                "gender": "FEMALE",
                "iconEmoji": "⚖️"
            }, {
                "id": "5eb281255cec6c8287024e51",
                "name": "大男子主义劝退",
                "gender": "FEMALE",
                "iconEmoji": "👋"
            }, {
                "id": "5eb281255cec6c8287024e50",
                "name": "更倾向颜性恋",
                "gender": "FEMALE",
                "iconEmoji": "👀"
            }]
        elif item == 'title':
            return {
                "prefix": {
                    "id": "5eb2999a5cec6c8287024ebc",
                    "name": "没有技术含量的",
                    "location": "prefix"
                },
                "suffix": {
                    "id": "5ea6d6029dfe1901c6504d89",
                    "name": "摄影爱好者",
                    "location": "suffix"
                }
            }

        else:
            value = cf.get(section, item)  # 获取对应的值
            if value == '10':
                return 10
            elif value == 'true':
                return True
            elif value == 'false':
                return False
            elif value == '0':
                return 0
            elif value == '1':
                return 1
            else:
                return value