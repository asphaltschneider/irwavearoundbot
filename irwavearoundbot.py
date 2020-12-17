import irsdk
import time
from datetime import datetime
from pyautogui import press, typewrite, hotkey, write


# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_car_setup_tick = -1

# here we check if we are connected to iracing
# so we can retrieve some data
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset your State variables
        state.last_car_setup_tick = -1
        # we are shutting down ir library (clearing all internal variables)
        ir.shutdown()
        print('irsdk disconnected')
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected')
        if ir['WeekendInfo']:
            if ir['WeekendInfo']['Category'] == "Oval":
                print("The next event is an Oval race at ",ir['WeekendInfo']['TrackDisplayName'], ", ",ir['WeekendInfo']['TrackCountry'])


def loop(lastflag, wavedone):
    cur_effect=lastflag
    wavearound = wavedone


    # datetime object containing current date and time
    now = datetime.now()
    dt_string = now.strftime("%y-%m-%d %H:%M:%S")

    ir.freeze_var_buffer_latest()

    currentSession = ir['SessionNum']

    if wavearound == "possible":
        print(dt_string,"we could do the wave around now")
        time.sleep(10)
        if ir['SessionInfo']:
            if ir['SessionInfo']['Sessions'][currentSession]['SessionName'] == "RACE":
                for position in ir['SessionInfo']['Sessions'][currentSession]['ResultsPositions']:
                    if position['Lap'] > 0:
                        carIdx = position['CarIdx']
                        carNumber = ir['DriverInfo']['Drivers'][carIdx]['CarNumber']
                        driverName = ir['DriverInfo']['Drivers'][carIdx]['UserName']
                        if ir['CarIdxTrackSurface'][carIdx] == 3:
                            print(dt_string,"Car #", carNumber, " ", driverName, ", ", position['Lap']," lap(s) down. is on track. yes! he will get a wave around.")
                            ir.chat_command(1)
                            time.sleep(1)
                            message = '!waveby '
                            typewrite(message, interval=0.05)
                            time.sleep(10/60)
                            hotkey('altright','3')
                            time.sleep(10/60)
                            message = carNumber+' you received a wave around.'
                            typewrite(message, interval=0.05)
                            press('enter')
                        elif ir['CarIdxTrackSurface'][carIdx] == 1 or ir['CarIdxTrackSurface'][carIdx] == 2:
                            print(dt_string,"Car #", carNumber, " is doing a pit stop. No wave around")
                        elif ir['CarIdxTrackSurface'][carIdx] == -1:
                            print(dt_string,"Car #", carNumber, " is dead. No need to wave around a dead man.")

        wavearound = "done"

    if ir['SessionFlags'] & 0x00008000:
        if not cur_effect == "caution_wave":
            print(dt_string,"A caution is coming out!")
            cur_effect = "caution_wave"
    elif ir['SessionFlags'] & 0x00004000:
        if not cur_effect == "caution":
            print(dt_string,"We have a caution!")
            cur_effect = "caution"
            if (wavearound == "false"):
                wavearound = "possible"
    elif ir['SessionFlags'] & 0x00000200:
        if not cur_effect == "one to green":
            print(dt_string,"one lap to green")
            cur_effect = "one to green"
            wavearound = "false"
    elif ir['SessionFlags'] & 0x0004:
        if not cur_effect == "green flag":
            print(dt_string,"green flag")
            cur_effect = "green flag"
    elif ir['SessionFlags'] & 0x00000002:
        if not cur_effect == "white flag":
            print(dt_string,"white flag")
            cur_effect = "white flag"
    elif ir['SessionFlags'] & 0x00000001:
        if not cur_effect == "checkered":
            print(dt_string,"checkered....")
            cur_effect = "checkered"

    return cur_effect,wavearound



if __name__ == '__main__':
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()
    lastflag="none"
    wavedone="false"
    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing()
            # if we are, then process data
            if state.ir_connected:
                (lastflag,wavedone) = loop(lastflag,wavedone)
            # sleep for 1 second
            # maximum you can use is 1/60
            # cause iracing updates data with 60 fps
            time.sleep(10/60)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass