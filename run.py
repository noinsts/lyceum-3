import os
import sys

# Додаємо поточну директорію до Python Path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Імпортуємо та запускаємо бота з src
from src.main import LyceumBot, FlaskServer
import asyncio

ascii_art = r"""
                     __                        __              
                    /  |                      /  |             
 _______    ______  $$/  _______    _______  _$$ |_    _______ 
/       \  /      \ /  |/       \  /       |/ $$   |  /       |
$$$$$$$  |/$$$$$$  |$$ |$$$$$$$  |/$$$$$$$/ $$$$$$/  /$$$$$$$/ 
$$ |  $$ |$$ |  $$ |$$ |$$ |  $$ |$$      \   $$ | __$$      \ 
$$ |  $$ |$$ \__$$ |$$ |$$ |  $$ | $$$$$$  |  $$ |/  |$$$$$$  |
$$ |  $$ |$$    $$/ $$ |$$ |  $$ |/     $$/   $$  $$//     $$/ 
$$/   $$/  $$$$$$/  $$/ $$/   $$/ $$$$$$$/     $$$$/ $$$$$$$/  
                                                               
                                                               
                                                               
"""

if __name__ == "__main__":
    print(ascii_art)
    
    """
    server = FlaskServer(port=8080)
    server.run_in_background()
    """
    
    bot = LyceumBot()
    asyncio.run(bot.run())
