#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.


#my open ai stuff

import os
import openai
import json
os.environ['OPENAI_API_KEY'] = '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'
openai.api_key = os.getenv("OPENAI_API_KEY")
chat_log = []

def sendChat(text):
    print("sending {}".format(text))
    chat_log.append({"role": "user", "content": "{}.".format(text)})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = chat_log
    )
    response_dict = response.to_dict()
    chat_log.append(response_dict['choices'][0]['message'])
    print(chat_log[-1]['content'])
    
    return

def recipeGetter(dish):

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "user", "content": "I am a beginner cook, teach me how to cook {}.".format(dish)},
        ]
    )
    #print(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content']

def codingGetter(topic):

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "user", "content": "I am a beginner coder, can you code {} for me, provided with explanations like i'm 5".format(topic)},
        ]
    )
    #print(response['choices'][0]['message']['content'])
    return response['choices'][0]['message']['content']

def writingGetter(topic):
    
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": "I am a beginner writer, can you write {} for me, provided with explanations like i'm 5".format(topic)},
            ]
        )
        #print(response['choices'][0]['message']['content'])
        return response['choices'][0]['message']['content']


"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import Dict

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["/Chat", "/Coding"],
    ["/Writing", "/Recipes"],
    ["/start", "/done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(
        "Hi! I transfer your queries to chatGPT!\n"
        "Please choose what you want to do:\n"
        "1. /Chat (normal chat)\n"
        "2. /Coding (preset to help with code)\n"
        "3. /Writing (preset to help with writing)\n"
        "4. /Recipes (preset to help with recipes)\n"
        "5. /done (end the conversation)\n"
        "Please remember to /start me again if you need me again\n",
        reply_markup=markup,
    )

    return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    print("regular choice, {}".format(text))
    if text == "/Recipes":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await update.message.reply_text(f"What kind of food do you want the recipe for")
        context.user_data["choice"] = "Recipes"
        return TYPING_REPLY
    elif text == "/Coding":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await update.message.reply_text(f"What do you want chatGpt to code for you")
        context.user_data["choice"] = "Coding"
        return TYPING_REPLY
    elif text == "/Writing":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await update.message.reply_text(f"What do you want chatGpt to write for you")
        context.user_data["choice"] = "Writing"
        return TYPING_REPLY
    elif text == "/Chat":
        context.user_data["choice"] = "Chat"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await update.message.reply_text(f"Chat mode: Type your message to chatGPT\n"+
                                        "Type /done to end the conversation")
        return TYPING_REPLY
    else:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await update.message.reply_text(f"Please choose a valid option")
        return CHOOSING




async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)}You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )

    return CHOOSING


async def ask_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("[asking chatgpt]...")
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]

    if category != "Chat":
        del user_data["choice"]

    if category == "Recipes":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        print("recipe mode, sending {}".format(text))
        gpt_answer = recipeGetter(text)
        await update.message.reply_text(
            "This is the recipe chatGpt gave me! \n"
            f"{text}, {gpt_answer}\n"
            "What do you want to know about next?",
            reply_markup=markup,
        )

    elif category == "Coding":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        print("coding mode, sending {}".format(text))
        gpt_answer = codingGetter(text)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await update.message.reply_text(
            "This is the explanation about code chatGpt gave me! \n"
            f"{text}, {gpt_answer}\n"
            "What do you want to know about next?",
            reply_markup=markup,
        )
    elif category == "Writing":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        print("writing mode, sending {}".format(text))
        gpt_answer = writingGetter(text)
        await update.message.reply_text(
            "This is the explanation writing chatGpt gave me! \n"
            f"{text}, {gpt_answer}\n"
            "What do you want to know about next?",
            reply_markup=markup,
        )
    elif category == "Chat":
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        print("chat mode, sending {}".format(text))
        sendChat(text)
        reply = chat_log[-1]["content"]
        await update.message.reply_text(
            'chatGPT reply is \n{}'.format(reply)
        )
        return TYPING_REPLY
    else:
        print("invalid category, return to choosing")

    print("SUCCESS")
    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text(
        f"Bye Bye",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5919222931:AAEVX6CJzomN8uKPNNXnJ3q6aSLy6psUkbY").build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(\/Recipes|\/Coding|\/Writing|\/Chat)$"), regular_choice
                ),   
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^\/done$")), regular_choice
                )           
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^\/done$")),
                    ask_chatgpt,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^\/done$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()