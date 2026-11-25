# -*- coding: utf-8 -*-
"""底栏离线渲染仿真：按布局 XML 的真实 dp 值 + density 画出来，
用于装机前判断「汉字会不会被裁、底边是否同线、格宽是否一致」。
文案用运行时的真实值（Java 会 setText 覆盖 XML 初始值）。"""
import sys, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

XML = sys.argv[1] if len(sys.argv) > 1 else 'work/qu/app/src/main/res/layout/player_vod_control_view.xml'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'work/bar_render.png'
DENS = float(sys.argv[3] if len(sys.argv) > 3 else 2.0)

A = '{http://schemas.android.com/apk/res/android}'
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

LABEL = {'play_pre': '上集', 'play_next': '下集', 'play_retry': '重播', 'play_refresh': '刷新',
         'play_scale': '默认', 'play_speed': '1.0x', 'play_player': 'EXO', 'play_ijk': '硬解',
         'play_time_reset': '重置', 'play_cast': '投屏', 'zimu_select': '字幕',
         'audio_track_select': '音轨', 'danmu_setting': '弹幕',
         'landscape_portrait': '旋屏', 'screen_display': '屏显'}

def dp(v): 
    try: return float(str(v).replace('dp','')) * DENS
    except: return 0.0
def FT(px, idx=2): return ImageFont.truetype(FONT, max(6, int(round(px))), index=idx)
def tw(s, dp_size):
    f = FT(dp(dp_size)); bb = f.getbbox(s or ' ')
    return bb[2] - bb[0]

TEXT_DP, TIME_DP, ICON_DP, PAD_T, GAP_DP, PAD_LR = 8.0, 12.0, 23.0, 4.0, 3.0, 6.0
LINE = TEXT_DP * 1.34

root = ET.parse(XML).getroot()
group = [n for n in root.iter() if (n.get(A+'id') or '').endswith('play_btn_group')][0]

cells = []
for c in group:
    cid = (c.get(A+'id') or '').split('/')[-1]
    if not cid:
        if any((k.get(A+'id') or '').endswith(('tk_slot_start','tk_slot_end')) for k in list(c)):
            cid = 'tk_time_box'
        else:
            continue
    if c.get(A+'layout_width') == '0dp' or c.get(A+'layout_height') == '0dp': continue
    kids = list(c)
    is_dual = any((k.get(A+'id') or '').endswith(('tk_slot_start','tk_slot_end')) for k in kids)
    if is_dual:
        slot = [k for k in kids if (k.get(A+'id') or '').endswith(('tk_slot_start','tk_slot_end'))][0]
        han  = [k for k in kids if k is not slot][0]
        box_lr = dp(c.get(A+'paddingLeft'))
        w = max(dp(slot.get(A+'layout_width')), tw(han.get(A+'text'), TEXT_DP)) + 2*box_lr
        off = han.get(A+'layout_marginTop')
        nudge = dp(off) if off else 0.0
        cells.append(dict(kind='dual', id=cid, w=w, time=slot.get(A+'text') or '00:00',
                          han=han.get(A+'text') or '', lr=box_lr, nudge=nudge))
    else:
        lab = LABEL.get(cid, c.get(A+'text') or cid)
        w = max(dp(ICON_DP), tw(lab, TEXT_DP)) + 2*dp(PAD_LR)
        cells.append(dict(kind='icon', id=cid, w=w, han=lab))

row_h = dp(PAD_T) + dp(ICON_DP) + dp(LINE)
tot = sum(c['w'] + dp(GAP_DP) for c in cells) + dp(20)
W, TOP = int(max(tot + 40, 1500)), int(row_h + 200)
img = Image.new('RGB', (W, TOP), '#0b0b0e'); d = ImageDraw.Draw(img)
F_han, F_tm, F_note, F_t = FT(dp(TEXT_DP)), FT(dp(TIME_DP)), FT(19), FT(25)
x, y0 = dp(20), dp(62)
ic = y0 + dp(PAD_T); hn = ic + dp(ICON_DP)
for c in cells:
    cx = x + c['w']/2
    if c['kind'] == 'icon':
        d.rounded_rectangle([cx-dp(ICON_DP)/2, ic+2, cx+dp(ICON_DP)/2, ic+dp(ICON_DP)-2], radius=3, outline='#7c7c86', width=2)
    else:
        bb = d.textbbox((0,0), c['time'], font=F_tm)
        d.text((cx, ic + (dp(ICON_DP)-(bb[3]-bb[1]))/2), c['time'], font=F_tm, fill='#fff', anchor='ma')
    d.text((cx, hn + c.get('nudge', 0.0)), c['han'], font=F_han, fill='#ececf2', anchor='ma')
    x += c['w'] + dp(GAP_DP)

base = hn + dp(LINE)
d.line([(dp(10), base), (x, base)], fill='#ff4d6a', width=2)
d.line([(dp(10), ic+dp(ICON_DP)/2), (x, ic+dp(ICON_DP)/2)], fill='#37d67a', width=2)
d.text((dp(20), dp(14)), '底栏离线渲染  density=%.1f  按布局真实 dp 计算（不是截图）' % DENS, font=F_t, fill='#fff')
d.text((dp(20), base+dp(12)), '红线＝所有汉字底边（含片头/片尾）   绿线＝00:00 与图标同中线', font=F_note, fill='#b0b0ba')
d.text((dp(20), base+dp(40)), '整排宽 %.0fdp / %d 格（含 2 格双层）' % (tot/DENS, len(cells)), font=F_note, fill='#7f7f8a')

img.save(OUT); print('saved', OUT, img.size, 'cells', len(cells), [c['id'] for c in cells])
