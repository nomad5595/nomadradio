#!/bin/bash

# Цвета для красоты в терминале
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Начинаем установку Nomad Radio V2 для пользователя $USER...${NC}"

# 1. Пути (теперь без жесткой привязки к имени)
INSTALL_DIR="$HOME/.local/share/nomad-radio"
BIN_PATH="/usr/local/bin/nomadradio"

# 2. Создаем папку программы
mkdir -p "$INSTALL_DIR"

# 3. Копируем код (ищем файл nomad_v2.py в текущей папке)
if [ -f "nomad_v2.py" ]; then
    cp nomad_v2.py "$INSTALL_DIR/main.py"
else
    echo "❌ Ошибка: Файл nomad_v2.py не найден в этой папке!"
    exit 1
fi

# 4. Настройка окружения
echo -e "${BLUE}📦 Настройка виртуального окружения...${NC}"
python -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install python-vlc --quiet

# 5. Создаем универсальный запускатор
# Мы используем прямой путь к интерпретатору внутри venv, так надежнее
echo "#!/bin/bash
$INSTALL_DIR/venv/bin/python $INSTALL_DIR/main.py" > nomadradio_launcher

# 6. Установка в систему
chmod +x nomadradio_launcher
sudo mv nomadradio_launcher "$BIN_PATH"

echo -e "${GREEN}✅ Готово! Запускай командой: nomadradio${NC}"
echo -e "${GREEN}📂 Твой плейлист: ~/Музыка/nomad_stations.txt${NC}"
