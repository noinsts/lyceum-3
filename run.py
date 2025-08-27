import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import LyceumBot
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
    
    bot = LyceumBot()
    asyncio.run(bot.run())
