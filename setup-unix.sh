echo "Installing Travel-Buddy"
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
OWD=$(pwd)
cd $SCRIPT_DIR

VENV_DIR="$SCRIPT_DIR/.venv"
echo $VENV_DIR
if [ -d $VENV_DIR ]; then
  echo "Deleting old venv."
  rm -rf ./venv
fi

echo "Creating new venv."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing requirements."
python -m pip install -e .
cd $OWD
echo "Setup Complete"

