import vlc
import curses
import os
from pathlib import Path

# --- НАСТРОЙКИ ---
STATIONS_FILE = Path.home() / "Музыка" / "nomad_stations.txt"
instance = vlc.Instance('--network-caching=10000 --quiet')
player = instance.media_player_new()

def make_volume_bar(volume, width=20):
    """Создает строку вида [##########----------]"""
    filled_len = int(width * volume // 100)
    bar = '█' * filled_len + '░' * (width - filled_len)
    return f"[{bar}] {volume}%"

def load_catalog():
    """Загружает станции и разбивает их на группы по [КАТЕГОРИЯМ]"""
    catalog = {}
    current_cat = "Разное"
    
    if not STATIONS_FILE.exists():
        STATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATIONS_FILE, 'w', encoding='utf-8') as f:
            f.write("[RADIO]\nDFM, http://109.196.197.6\n")

    with open(STATIONS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            
            # Если строка в скобках - это новая категория
            if line.startswith('[') and line.endswith(']'):
                current_cat = line[1:-1]
                catalog[current_cat] = []
            elif ',' in line:
                name, url = line.split(',', 1)
                if current_cat not in catalog: catalog[current_cat] = []
                catalog[current_cat].append({"name": name.strip(), "url": url.strip()})
    return catalog

def get_now_playing():
    """Вытягивает название песни из потока (метаданные)"""
    media = player.get_media()
    if media:
        meta = media.get_meta(12) # 12 - ID для 'Now Playing'
        return meta if meta else "Эфир..."
    return "Ожидание потока"

def draw_menu(stdscr):
    # Цвета
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Заголовок
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN) # Выбор
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Песня
    
    curses.curs_set(0)
    stdscr.nodelay(1) # Позволяет обновлять экран без нажатия кнопок
    
    catalog = load_catalog()
    categories = list(catalog.keys())
    
    # Состояние интерфейса
    view = "categories" # Либо 'categories', либо 'stations'
    sel_cat_idx = 0
    sel_st_idx = 0
    volume = 50
    player.audio_set_volume(volume)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        
        # 1. Заголовок (Теперь точно 2.4!)
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(0, 2, f" 📻 NOMAD RADIO V2.4 | {view.upper()} ")
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # 2. Список (Папки или Станции)
        if view == "categories":
            items = categories
            current_idx = sel_cat_idx
        else:
            items = [s['name'] for s in catalog[categories[sel_cat_idx]]]
            current_idx = sel_st_idx

        for i, item in enumerate(items):
            if i + 2 >= h - 5: break
            if i == current_idx:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(2 + i, 2, f" > {item} ".ljust(35))
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(2 + i, 2, f"   {item}")

        # 3. Инфо-панель (Метаданные)
        song_info = get_now_playing()
        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(h-4, 2, f" 🎵 : {song_info}"[:w-5])
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
        
        # 4. Подвал (рисуем по порядку снизу вверх)
        vol_bar = make_volume_bar(volume)
        stdscr.addstr(h-4, 2, f" 🎵 : {get_now_playing()}", curses.color_pair(3)) # Название песни
        stdscr.addstr(h-3, 2, f" Громкость: {vol_bar} ", curses.A_BOLD)         # Твой крутой ползунок
        stdscr.addstr(h-2, 2, " 5:Играть | 0:Назад | +/-:Громкость | .:Выход ", curses.A_DIM) # Подсказки


        
        stdscr.refresh()
        curses.napms(100) # Обновляем экран 10 раз в секунду

        key = stdscr.getch()
        if key == -1: continue

        if key == ord('.'):
            player.stop()
            break
        elif key in [ord('8'), curses.KEY_UP]:
            if view == "categories": sel_cat_idx = max(0, sel_cat_idx - 1)
            else: sel_st_idx = max(0, sel_st_idx - 1)
        elif key in [ord('2'), curses.KEY_DOWN]:
            if view == "categories": sel_cat_idx = min(len(categories)-1, sel_cat_idx + 1)
            else: sel_st_idx = min(len(catalog[categories[sel_cat_idx]])-1, sel_st_idx + 1)
        elif key in [ord('5'), 10, 13]: # Enter
            if view == "categories":
                view = "stations"
                sel_st_idx = 0
            else:
                st = catalog[categories[sel_cat_idx]][sel_st_idx]
                media = instance.media_new(st['url'])
                player.set_media(media)
                player.play()
        elif key == ord('0'): # Назад к категориям
            view = "categories"
        elif key == ord('+'):
            volume = min(volume + 10, 100); player.audio_set_volume(volume)
        elif key == ord('-'):
            volume = max(volume - 10, 0); player.audio_set_volume(volume)

if __name__ == "__main__":
    curses.wrapper(draw_menu)
