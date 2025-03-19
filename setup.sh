# establish environment name
ENV_NAME="gmail-bot-env"

# create environment
echo "Creating virtual environment: $ENV_NAME"
# if you run into issues on windows, use the alternative command
python3 -m venv $ENV_NAME        #python -m venv $ENV_NAME

# activate environment
echo "Activating virtual environment..."
source $ENV_NAME/bin/activate

# install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! To activate the environment, run:"
echo "source $ENV_NAME/bin/activate"
echo "For windows, run:"
echo "source $ENV_NAME\Scripts\activate"
echo "To deactivate the environment, run:"
echo "deactivate"