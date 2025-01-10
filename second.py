import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = "26850449"
API_HASH = "72a730c380e68095a8549ad7341b0608"
BOT_TOKEN = "8019587694:AAGdOaF3MYGjwRaqgwrqXg1G0S4hXGB2emg"

GECKO_API_URL = "https://api.geckoterminal.com/api/v2"

NETWORKS = [
    "Solana", "Ethereum", "Polygon", "Binance Chain", "Base", "Sui", "Ton",
    "Arbitrum", "Avalanche", "zkSync", "Tron", "Aptos", "Blast", "Optimism",
    "Linea", "Mantle", "Near"
]

app = Client("meme_token_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def search_tokens_by_name_and_network(name, network):
    response = requests.get(f"{GECKO_API_URL}/search", params={"query": name, "network": network})
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

@app.on_message(filters.command("chk"))
async def check_token(client, message):
    query = message.text.split(" ", 1)
    if len(query) < 2:
        await message.reply("Please provide a token name.")
        return

    token_name = query[1]
    buttons = [
        [InlineKeyboardButton(network, callback_data=f"network_{network.lower()}_{token_name}")]
        for network in NETWORKS
    ]
    await message.reply(
        f"Choose the network where you want to search for tokens named **{token_name}**:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query()
async def callback_query_handler(client, callback_query):
    data = callback_query.data

    if data.startswith("network_"):
        _, network, token_name = data.split("_", 2)
        tokens = await search_tokens_by_name_and_network(token_name, network)
        if not tokens:
            await callback_query.message.edit(f"No tokens found for **{token_name}** on {network.capitalize()}.")
            return

        await show_token_results(callback_query.message, tokens, network, token_name)

    elif data.startswith("page_"):
        _, network, token_name, page = data.split("_", 3)
        page = int(page)
        tokens = await search_tokens_by_name_and_network(token_name, network)
        await show_token_results(callback_query.message, tokens, network, token_name, page)

async def show_token_results(message, tokens, network, token_name, page=1):
    per_page = 10
    total_tokens = len(tokens)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_tokens = tokens[start_idx:end_idx]

    buttons = [
        [InlineKeyboardButton(f"{token['attributes']['name']} ({token['attributes']['symbol']})", callback_data=f"details_{token['attributes']['address']}")]
        for token in current_tokens
    ]

    if start_idx > 0:
        buttons.append([InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{network}_{token_name}_{page - 1}")])
    if end_idx < total_tokens:
        buttons.append([InlineKeyboardButton("➡️ Next", callback_data=f"page_{network}_{token_name}_{page + 1}")])

    await message.edit(
        f"**Tokens for {token_name} on {network.capitalize()}** (Page {page}):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query()
async def token_details_callback(client, callback_query):
    if callback_query.data.startswith("details_"):
        token_address = callback_query.data.split("_", 1)[1]
        token_details = await get_token_details(token_address)
        if token_details:
            network = token_details.get("network", "Unknown")
            explorer_link = get_explorer_link(network, token_address)
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
