#!/usr/bin/env python3

import ast
import os
from datetime import datetime

import TrelloToolbox as trello
import pytz
from dateutil.relativedelta import *

# Global variables
now = datetime.now(pytz.utc)
team = ast.literal_eval(os.environ['TEAM'])
_myToken = os.environ.get('trello_token')

apiContext = trello.ApiContext(_myToken)

boardsHelper = trello.Boards(apiContext)
cardsHelper = trello.Cards(apiContext)
membersHelper = trello.Members(apiContext)


def print_cards(cards, header=""):
    "Print a list of cards in a nice neat summary view"
    if cards:
        print(header)
        print('\t {} {} {} {}'.format("Card Name", "Due Date", "Card Member", "Card Short Link"))
        for c in cards:
            print('\t {} {} {} {}'.format(c['name'], c['due'][0:10],
                                          membersHelper.get_member_names_from_list(c['idMembers']), c['url']))
    else:
        print("No Overdue Cards Found")


def set_trello_due_date():
    boardId = boardsHelper.get_single_by_member_and_name("weshayutin1", "OSP-director Infrastructure")
    member_list = [membersHelper.get_member_id(team[member]['trello']) for member in team]
    listId = boardsHelper.get_single_list_by_name(boardId, "In Progress")

    card_list = []
    card_list = cardsHelper.get_cards(listId)
    overdue_cards = []

    in_one_week = now + relativedelta(weeks=+1)
    in_one_week = in_one_week.strftime('%Y-%m-%dT%H:%M:%S')
    # print(in_one_week)
    for card in card_list:
        if card['idMembers']:
            if card['idMembers'] is not None:
                if set(card['idMembers']).issubset(member_list) and card['due'] is None:
                    cardsHelper.add_due_date_to_card(card, in_one_week)
                if set(card['idMembers']).issubset(member_list) and card['due'] is not None:
                    if cardsHelper.check_card_overdue(card['id']):
                        overdue_cards.append(card)

        else:
            cardsHelper.add_comment_to_card(card['id'], "Please add a member to this card")

    return overdue_cards

if __name__ == "__main__":
    print_cards(set_trello_due_date(), "Overdue Card List:")
