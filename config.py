fotoboxCfg = {}

fotoboxCfg['window-width']    = 1280
fotoboxCfg['window-height']   = 1024

# Depending on the camera used previews might got smaller than set here
fotoboxCfg['cam-p-width']     = 960
fotoboxCfg['cam-p-height']    = 800
fotoboxCfg['cam-p-x']         = 9
fotoboxCfg['cam-p-y']         = 195
fotoboxCfg['cam-p-hflip']     = 1 # False = Like a camera, True = Like a mirror

# PiCam v1: 2592x1944, v2: 3280x2464
fotoboxCfg['cam-c-width']     = 3280
fotoboxCfg['cam-c-height']    = 2464
fotoboxCfg['cam-c-hflip']     = False # False = Like a camera, True = Like a mirror

fotoboxCfg['nopi']            = False #True = Skip rasperry specific modules

fotoboxCfg['temp']            = '/tmp/fotobox/'
fotoboxCfg['save']            = '/home/niklas/fotobox/images/'

fotoboxCfg['countdown']       = 3 # Seconds

fotoboxCfg['project_dir']     = '~/fotobox'
fotoboxCfg['design_dir']      = 'design/'
fotoboxCfg['layout_file']      = 'design/layout.html'
####### Debug ###########
# fotoboxCfg['project_dir']     = 'E:\Programmieren\Fotobox'
# fotoboxCfg['design_dir']      = 'E:\Programmieren\Fotobox/design/'
# fotoboxCfg['layout_file']      = 'E:\Programmieren\Fotobox/design/layout.html'

fotoboxText = {}

fotoboxText['info-home']    = 'Scanne den QR-Code, da kannst du die Bilder herunterladen'
fotoboxText['info-count']   = 'Los geht es!<hr><span style="font-size: 200%; font-weight: bolder;">${countdown}</span>'
fotoboxText['info-capture'] = '<span style="font-size: 200%; font-weight: bolder;">Bitte lächeln!</span>'
fotoboxText['btn-capture']  = 'Neuer Versuch ▶'
fotoboxText['btn-view']     = 'Ansehen ▶'
fotoboxText['btn-save']     = 'Speichern ▶'
fotoboxText['btn-recapture'] = '<span style="font-size: 75%">Neuer Versuch</span> ▶'
fotoboxText['btn-cancel']   = 'Abbruch ▶'
fotoboxText['btn-next']     = 'Nächstes ▶'
fotoboxText['btn-previous'] = 'Vorheriges ▶'
fotoboxText['btn-back']     = 'Zurück ▶'
fotoboxText['btn-empty']    = ''
