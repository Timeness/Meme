import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = "26850449"
API_HASH = "72a730c380e68095a8549ad7341b0608"
BOT_TOKEN = "8019587694:AAGdOaF3MYGjwRaqgwrqXg1G0S4hXGB2emg"

GECKO_API_URL = "https://api.geckoterminal.com/api/v2"

app = Client("meme_token_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def get_token_details(address_or_name):
    response = requests.get(f"{GECKO_API_URL}/tokens/{address_or_name}")
    if response.status_code == 200:
        data = response.json()
        return data["data"]["attributes"]
    return None

def get_explorer_link(network, token_address):
    explorers = {
        "ethereum": f"https://etherscan.io/token/{token_address}",
        "solana": f"https://solscan.io/token/{token_address}",
        "binance-smart-chain": f"https://bscscan.com/token/{token_address}",
        "polygon": f"https://polygonscan.com/token/{token_address}",
        "avalanche": f"https://snowtrace.io/token/{token_address}",
    }
    return explorers.get(network.lower(), "Explorer not available")

@app.on_message(filters.command("chk"))
async def check_token(client, message):
    query = message.text.split(" ", 1)
    if len(query) < 2:
        await message.reply("Please provide a token address or name.")
        return

    input_data = query[1]
    if input_data.startswith("0x"):
        token_details = await get_token_details(input_data)
        if token_details:
            network = token_details.get("network", "Unknown")
            explorer_link = get_explorer_link(network, input_data)
            reply_text = (
                f"**Token Details**\n"
                f"Name: {token_details['name']}\n"
                f"Symbol: {token_details['symbol']}\n"
                f"Price: ${token_details.get('price', 'N/A')}\n"
                f"Market Cap: ${token_details.get('market_cap', 'N/A')}\n"
                f"24h Volume: ${token_details.get('volume_24h', 'N/A')}\n"
                f"FDV: ${token_details.get('fully_diluted_valuation', 'N/A')}\n"
                f"Holders: {token_details.get('holders', 'N/A')}\n"
                f"Age: {token_details.get('age', 'N/A')} days\n"
                f"Liquidity: ${token_details.get('liquidity', 'N/A')}\n"
                f"Liquidity Locked: {'Yes' if token_details.get('liquidity_locked') else 'No'}\n"
                f"Network: {network.capitalize()}\n"
                f"Check on {network.capitalize()} Explorer: [Here]({explorer_link})\n"
                f"\n**Price Changes**\n"
                f"5m: {token_details.get('price_change_5m', 'N/A')}%\n"
                f"1h: {token_details.get('price_change_1h', 'N/A')}%\n"
                f"6h: {token_details.get('price_change_6h', 'N/A')}%\n"
                f"24h: {token_details.get('price_change_24h', 'N/A')}%\n"
                f"\nAddress: {input_data}"
            )
            buttons = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{input_data}"),
                    InlineKeyboardButton("📊 Go Chart", url=f"https://geckoterminal.com/token/{input_data}"),
                ]
            ]
            await message.reply(reply_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
        else:
            await message.reply("No details found for this address.")
    else:
        tokens = await search_tokens_by_name(input_data)
        if tokens:
            buttons = []
            for idx, token in enumerate(tokens[:10]):
                token_attr = token["attributes"]
                token_address = token_attr["address"]
                buttons.append([
                    InlineKeyboardButton(
                        f"{idx + 1}. {token_attr['name']} ({token_attr['symbol']}) | ${token_attr.get('price', 'N/A')}",
                        callback_data=f"details_{token_address}"
                    )
                ])
            await message.reply(
                "**Search Results**\nChoose a token to see details:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await message.reply("No tokens found with this name.")

@app.on_callback_query()
async def callback_query_handler(client, callback_query):
    if callback_query.data.startswith("refresh_"):
        token_address = callback_query.data.split("_", 1)[1]
        token_details = await get_token_details(token_address)
        if token_details:
            network = token_details.get("network", "Unknown")
            explorer_link = get_explorer_link(network, token_address)
            reply_text = (
                f"**Token Details (Refreshed)**\n"
                f"Name: {token_details['name']}\n"
                f"Symbol: {token_details['symbol']}\n"
                f"Price: ${token_details.get('price', 'N/A')}\n"
                f"Market Cap: ${token_details.get('market_cap', 'N/A')}\n"
                f"24h Volume: ${token_details.get('volume_24h', 'N/A')}\n"
                f"FDV: ${token_details.get('fully_diluted_valuation', 'N/A')}\n"
                f"Holders: {token_details.get('holders', 'N/A')}\n"
                f"Age: {token_details.get('age', 'N/A')} days\n"
                f"Liquidity: ${token_details.get('liquidity', 'N/A')}\n"
                f"Liquidity Locked: {'Yes' if token_details.get('liquidity_locked') else 'No'}\n"
                f"Network: {network.capitalize()}\n"
                f"Check on {network.capitalize()} Explorer: [Here]({explorer_link})\n"
                f"\n**Price Changes**\n"
                f"5m: {token_details.get('price_change_5m', 'N/A')}%\n"
                f"1h: {token_details.get('price_change_1h', 'N/A')}%\n"
                f"6h: {token_details.get('price_change_6h', 'N/A')}%\n"
                f"24h: {token_details.get('price_change_24h', 'N/A')}%\n"
                f"\nAddress: {token_address}"
            )
            buttons = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{token_address}"),
                    InlineKeyboardButton("📊 Go Chart", url=f"https://geckoterminal.com/token/{token_address}"),
                ]
            ]
            await callback_query.message.edit(reply_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
        else:
            await callback_query.answer("Details not found.", show_alert=True)

app.run()
