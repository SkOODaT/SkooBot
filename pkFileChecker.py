import os
import sys
import glob
from pathlib import Path

from pythonnet import load
load("coreclr")

import clr
from System import Array, Byte, Memory

os.path.abspath("PKHeX.Core.dll")
clr.AddReference("PKHeX.Core")

from PKHeX.Core import (
    PKM,
    PK7,
    PB7,
    PK8,
    PA8,
    PB8,
    PK9,
    PA9,
    Gender,
    Ball,
    Ability,
    Nature,
    Species,
    Move,
    MoveType,
    LanguageID,
    SaveFile,
    LegalityAnalysis
)

filetypes = {
    '**/*.pk*',
    '**/*.pa*',
    '**/*.pb*',
}

targets = [
    "pk7",
    "pb7",
    "pk8",
    "pa8",
    "pb8",
    "pk9"
]

def load_pk(ctarget: str, path: str) -> PKM:
    """Load a .pk9 file into a PKHeX PK9 object."""
    data = Path(path).read_bytes()
    byte_array = bytearray(data)
    net_array = Array[Byte](byte_array)
    dotnet_memory = Memory[Byte](net_array)
            
    pk = str
    if ctarget == "pk7":
        pk = PK7(dotnet_memory)
    elif ctarget == "pb7":
        pk = PB7(dotnet_memory)
    elif ctarget == "pk8":
        pk = PK8(dotnet_memory)
    elif ctarget == "pa8":
        pk = PA8(dotnet_memory)
    elif ctarget == "pb8":
        pk = PB8(dotnet_memory)
    elif ctarget == "pk9":
        pk = PK9(dotnet_memory)
 
    return pk

def check_legality(pk: PKM) -> dict:
    """Run PKHeX legality analysis and return a summary dict."""
    la = LegalityAnalysis(pk)
    #report = la.Report(verbose=True)   # full human-readable report
    return {
        "valid":   la.Valid,
        "report":  str(la.Parsed),
        "checks":  [(str(list.Identifier), list.Valid, str(list.Judgement), str(list.Result))
                    for list in la.Results],
    }

def summarise_pk(ctarget: str, pk: PKM) -> dict:
    """Extract key fields from a PKM object."""
    return {
        "species":       int(pk.Species),
        "species_name":  str(Species(int(pk.Species))),         # e.g. "Charizard"
        "nickname":      str(pk.Nickname),
        "level":         int(pk.CurrentLevel),
        "pid":           f"{int(pk.PID):#010x}",
        "tid":           int(pk.TID16),
        "sid":           int(pk.SID16),
        "ot":            str(pk.OriginalTrainerName),
        "gender":        int(pk.Gender),               # 0=M 1=F 2=Unknown
        "nature":        str(pk.Nature),               # e.g. "Timid"
        "stat_nature":   str(pk.StatNature),           # after mints
        "ability":       str(Ability(int(pk.Ability))),
        #"tera_type":     str(pk.TeraType),             # SV-exclusive
        #"tera_orig":     str(pk.TeraTypeOriginal),
        "held_item":     str(pk.HeldItem),       # item name
        "ball":          str(Ball(int(pk.Ball))),
        "met_level":     int(pk.MetLevel),
        "met_location":  str(pk.MetLocation),         # location name
        "is_egg":        bool(pk.IsEgg),
        #"shiny":         bool(pk.IsvShiny),
        #"shiny_type":    "Star" if pk.ShinyXor == 1 else
        #                 "Square" if pk.IsShiny else "None",
        "ivs": {
            "HP":  int(pk.IV_HP),  "Atk": int(pk.IV_ATK),
            "Def": int(pk.IV_DEF), "SpA": int(pk.IV_SPA),
            "SpD": int(pk.IV_SPD), "Spe": int(pk.IV_SPE),
        },
        "evs": {
            "HP":  int(pk.EV_HP),  "Atk": int(pk.EV_ATK),
            "Def": int(pk.EV_DEF), "SpA": int(pk.EV_SPA),
            "SpD": int(pk.EV_SPD), "Spe": int(pk.EV_SPE),
        },
        "moves": [
            str(Move(int(pk.Move1))), str(Move(int(pk.Move2))),
            str(Move(int(pk.Move3))), str(Move(int(pk.Move4))),
        ]
        #"ribbons": int(pk.RibbonCount),
    }

def print_result(ctarget: str, path: str, summary: dict, legality: dict):
    status = "✅ LEGAL" if legality["valid"] else "❌ ILLEGAL"
    print(f"\n{'─'*55}")
    print(f"  {status}  {path}")
    print(f"{'─'*55}")
    s = summary
    #print(f"  Species   : #{s['species']} {s['species_name']}"
         # f"  Lv.{s['level']}  {'★ ' if s['shiny'] else ''}"
         # f"{s['shiny_type']}")
    print(f"  Nickname  : {s['nickname']}")
    print(f"  OT        : {s['ot']}  TID={s['tid']}  SID={s['sid']}")
    print(f"  Nature    : {s['nature']}"
          + (f"  (stat: {s['stat_nature']})" if s['stat_nature'] != s['nature'] else ""))
    print(f"  Ability   : {s['ability']}")
    #print(f"  Tera Type : {s['tera_type']}"
    #      + (f"  (orig: {s['tera_orig']})" if s['tera_orig'] != s['tera_type'] else ""))
    print(f"  Ball      : {s['ball']} Ball  Held: {s['held_item']}")
    print(f"  Met       : Lv.{s['met_level']} @ {s['met_location']}")
    iv = s['ivs'];  ev = s['evs']
    print(f"  IVs       : HP={iv['HP']:2} Atk={iv['Atk']:2} Def={iv['Def']:2}"
          f" SpA={iv['SpA']:2} SpD={iv['SpD']:2} Spe={iv['Spe']:2}")
    print(f"  EVs       : HP={ev['HP']:3} Atk={ev['Atk']:3} Def={ev['Def']:3}"
          f" SpA={ev['SpA']:3} SpD={ev['SpD']:3} Spe={ev['Spe']:3}")
    print(f"  Moves     : {' / '.join(m for m in s['moves'] if m)}")

    flag = False
    info = ""
    for ident, Valid, judgement, Result in legality["checks"]:
        if judgement != 'Valid':
            flag = True
            info += f"     [{ident}] {judgement} {Result} \n"
    if flag == True:
        print("\n  ⚠  Legality issues:")
        print(info, end="")

def main(patterns):
    files = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))
    if not files:
        print("No .pk files found.")
        return
    ok = bad = 0
    for path in files:
        try:
            ctarget = str
            for t in targets:
                index = path.find(t)
                if index != -1:
                    ctarget = t
            pk = load_pk(ctarget, path)
            summary = summarise_pk(ctarget, pk)
            legality = check_legality(pk)
            print_result(ctarget, path, summary, legality)
            if legality["valid"]: ok += 1
            else: bad += 1
        except Exception as e:
            print(f"\n  ERROR reading {path}: {e}")

    print(f"\n{'═'*55}")
    print(f"  Total: {ok+bad}  ✅ {ok} legal  ❌ {bad} illegal")

if __name__ == "__main__":
    files = []
    args = sys.argv[1:] or files
    if args == []:
        for u in filetypes:
            files += glob.glob(u, recursive=True)
            args = files
    main(args)
