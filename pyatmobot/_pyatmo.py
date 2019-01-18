# -*- coding: utf-8 -*-

import slackbot


class Pyatmo(slackbot.Action):
    @staticmethod
    def option_list(name: str) -> slackbot.OptionList:
        return slackbot.OptionList(
            name,
            [])
