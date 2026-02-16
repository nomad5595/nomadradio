import vlc
import curses
import os
from pathlib import Path

# --- НАСТРОЙКА ПУТИ ---
# Указываем твою реальную папку "Музыка"
STATIONS_FILE = Path.home() / "Музыка" / "nomad_stations.txt"

instance = vlc.Instance('--network-caching=10000 --quiet')
player = instance.media_player_new()

def load_stations():
    stations = []
    
    # Если папка или файл отсутствуют — создаем их
    STATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if not STATIONS_FILE.exists():
        with open(STATIONS_FILE, 'w', encoding='utf-8') as f:
            f.write("# Название, Ссылка\n")
            f.write("DFM Anapa, http://109.196.197.6\n")
            f.write("Europa Plus, http://ep128.hostingradio.ru\n")
    
    with open(STATIONS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if ',' in line and not line.strip().startswith('#'):
                name, url = line.strip().split(',', 1)
                stations.append({"name": name.strip(), "url": url.strip()})
    return stations

def draw_menu(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Заголовок
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN) # Выбор
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Статус
    
    curses.curs_set(0)
    stdscr.nodelay(0)
    
    stations = load_stations()
    current_row, playing_row = 0, -1
    volume, is_playing = 50, False
    player.audio_set_volume(volume)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Отрисовка интерфейса
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(0, 2, " 📻 NOMAD RADIO V2.1 ")
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        for i, st in enumerate(stations):
            if i == current_row:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(2 + i, 2, f" > {st['name']} ".ljust(30))
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(2 + i, 2, f"   {st['name']}")
            
            if i == playing_row:
                status = " [PLAYING] " if is_playing else " [PAUSED] "
                stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(2 + i, 35, status)
                stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

        stdscr.addstr(h-3, 2, f" Громкость: {volume}% | Файл: ~/Музыка/nomad_stations.txt", curses.A_BOLD)
        stdscr.addstr(h-2, 2, " 8/2: Навигация | 5/Enter: Play | +/-: Громкость | .: Выход ", curses.A_DIM)
        
        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('.'):
            player.stop()
            break
        elif key in [ord('8'), curses.KEY_UP]:
            current_row = max(0, current_row - 1)
        elif key in [ord('2'), curses.KEY_DOWN]:
            current_row = min(len(stations) - 1, current_row + 1)
        elif key == ord('+'):
            volume = min(volume + 10, 100)
            player.audio_set_volume(volume)
        elif key == ord('-'):
            volume = max(volume - 10, 0)
            player.audio_set_volume(volume)
        elif key in [ord('5'), 10, 13]:
            if current_row == playing_row:
                player.pause()
                is_playing = not is_playing
            else:
                playing_row = current_row
                media = instance.media_new(stations[playing_row]['url'])
                player.set_media(media)
                player.play()
                is_playing = True

if __name__ == "__main__":
    curses.wrapper(draw_menu)
