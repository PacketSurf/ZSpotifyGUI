#TEST=`python3 source/test.py`
#echo "$TEST"
TEMP="Temp"
mkdir "$TEMP"
cd "$TEMP"
git clone https://github.com/PacketSurf/ZSpotifyGUI.git
source $HOME/ZSpotify/zspot-env/bin/activate
cd $HOME/Programming/ZSpotify/zspotify
cd source
python3 appGui.py
osascript -e 'tell application "Terminal" to close first window' & exit