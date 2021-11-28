echo "nice"
source $HOME/ZSpotify/zspot-env/bin/activate
cd $HOME/ZSpotify/zspotify/
python3 appGui.py
osascript -e 'tell application "Terminal" to close first window' & exit