SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

VENV_DIR="$SCRIPT_DIR/.venv"

if ! [ -d $SCRIPT_DIR ]; then
  echo "Error: No .venv folder! Make sure to run $SCRIPT_DIR/setup-unix.sh!"
  return
fi

$VENV_DIR/bin/python $SCRIPT_DIR/src/TravelBuddy/main.py