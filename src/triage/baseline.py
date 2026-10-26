"""Approach A: transparent keyword and regex rules, one block per label-guide rule.

Every rule carries the label-guide code it implements (C1..C6, P1..P4, U1..U6, X1..X6, I1..I3;
see docs/label-guide.md). Rules match one sentence at a time, so Evidence is simply the
sentences whose rules fired.

Category: weighted rules give each Category a score; the primary-Category rules P1-P3 then
rescale the scores, and the result is normalised into `category_probs` (ties broken by the P4
order). Urgency: 0.95 when a hard U-rule fires, 0.5 when only an ambiguous cue does, else 0.05.
Destination: the D0 default for each Category, overridden by the exception rules X1-X6; the
`destination_probs` are the Category probabilities pushed through that mapping.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass

from triage.schema import (
    DEFAULT_DESTINATION,
    Category,
    Destination,
    Prediction,
    Report,
    split_sentences,
)

RULES_VERSION = "a-v2"

C = Category
D = Destination

HARD_URGENT = 0.95
AMBIGUOUS_URGENT = 0.5
NO_URGENCY = 0.05

# Top two Category probabilities closer than this raise `conflicting_categories`.
CONFLICT_MARGIN = 0.15
# Added to every Category score before normalising, so no probability is exactly 0 or 1.
SMOOTHING = 0.05

# P4: fixed order for unrelated issues; also the tie-break order.
P4_ORDER = [C.SAFETY_INCIDENT, C.MISSING_SHIPMENT, C.SHIPMENT_DAMAGE, C.VEHICLE_BREAKDOWN,
            C.DOCUMENTATION_ISSUE, C.DELIVERY_DELAY]


@dataclass(frozen=True)
class Rule:
    code: str  # label-guide rule it implements
    pattern: re.Pattern
    weight: float = 1.0  # Category rules only; may be negative
    negatable: bool = True  # skip the match if a negation cue sits just before it
    unless: re.Pattern | None = None  # skip the whole sentence if this matches it


def _re(pattern: str, flags: int = re.IGNORECASE) -> re.Pattern:
    return re.compile(pattern, flags)


def _rule(code, pattern, weight=1.0, negatable=True, unless=None, flags=re.IGNORECASE):
    return Rule(code, _re(pattern, flags), weight, negatable,
                _re(unless) if unless else None)


# --- Negation --------------------------------------------------------------------------------
# "nobody hurt", "no leak seen", "not injured", "No deadline": a cue within a few words before
# the match cancels it. "(not ours)" just after a match cancels it too ("crash (not ours)").
_NEG_BEFORE = _re(r"\b(no|not|nobody|no-one|no one|none|never|without|nothing|isn't|wasn't|"
                  r"aren't|weren't|hasn't|haven't)\b[\w\s,'-]{0,20}$")
_NEG_AFTER = _re(r"^[^.]{0,6}\(?(not (ours|us|our \w+|involving us|one of ours)"
                 r"|(we|I) (weren['’]t|wasn['’]t|were not|was not) (involved|part)[^.]{0,10})\)?")
# "somebody else's collision": an incident that happened to someone else is not ours.
_NEG_BEFORE_OTHERS = _re(r"\b(some(body|one) else['’]?s|another (driver|vehicle|firm)['’]?s|other "
                         r"people['’]?s|third[- ]party)\s*(\w+\s)?$")


def _affirmed(sentence: str, m: re.Match, rule: Rule) -> bool:
    if not rule.negatable:
        return True
    return not (_NEG_BEFORE.search(sentence[: m.start()])
                or _NEG_BEFORE_OTHERS.search(sentence[: m.start()])
                or _NEG_AFTER.search(sentence[m.end():]))


# --- Shared vocabulary -----------------------------------------------------------------------
# Leak rules start matching at the cargo word, so "no leak seen" is caught per sentence instead.
_NO_LEAK = r"\b(no|not|without|isn't|wasn't) (\w+ )?(leak|leaking|spill|spilt|spilled)\b"
_DG = r"(UN ?\d{4}|class \d|hazchem|dangerous goods|corrosive|flammable|acid|chemicals?|ADR)"
_BREACH = (r"(\bseals?\b[^.]*\b(broken|missing|cut|tampered|(does ?n[o']t|doesn't|not|no longer)"
           r" match\w*|mismatch\w*|different)"
           r"|\bcurtains?\b[^.]*\b(slashed|cut|ripped)"
           r"|\b(doors?|locks?|padlocks?)\b[^.]*\b(forced|broken open|jemmied|prised)"
           r"|\bcartons? (have been |had been |were )?opened|\bbroken into|\btampered)")
_CRIMINAL_IMMOBILISATION = (r"(\bsiphon\w*|\bfuel (was )?(stolen|theft|drained)|\btank drained"
                            r"|\b(filler|fuel) cap (was )?forced|\b(air )?lines (were |had been )?"
                            r"cut|\bcables? (were |had been )?cut|\btyres? (were |had been )?"
                            r"slashed|\bvandal\w*|\bcut\b[^.]{0,30}\b(air )?(lines|cables?|hoses?|wires?)\b"
                            r"|\bslashed\b[^.]{0,20}\btyres?)")
_DRIVER_HOURS = (r"(\bdriving limit|\b(\d+|nine|ten)-hour|\bhours limit|\bout of hours|\b(daily|"
                 r"weekly) rest|\btake (his|her|my|a) (rest|break)|\b(required|mandatory) break"
                 r"|\bno (relief )?driver|\brelief driver|\bdriver (is )?off sick)")
_AUTHORITY = (r"(\bborder force|\bcustoms\b|\bHMRC\b|\bDVSA\b|\bpolice\b|\bofficers?\b|\bx-ray"
              r"|\bexamination|\bimpounded|\bpulled (us|me|him|her) in)")
_DOC_WORD = (r"(\bPOD\b|proof of delivery|delivery note|\be-?POD\b|\bCMR\b|consignment note"
             r"|paperwork|\bdocuments?\b|documentation|declaration|\bENS\b|\bT1\b|certificate"
             r"|dangerous goods note|\bDGN\b|tachograph|\btacho\b|driver card|\bCPC\b|\bpermit"
             r"|licence|\binvoice|\bsignature|\bsign(ed)?\b)")
_DOC_PROBLEM = (r"(\bmissing|\bwrong|\bincorrect|\bnot (been )?(lodged|signed|stamped|filed)"
                r"|\bunsigned|\bexpired|\binvalid|\brefused to sign|\bno \w+ signature|\blacks"
                r"|\bleft without|\bwithout (a|the|any) (signature|delivery note|paperwork)"
                r"|\binfringement|\bout of date|\bmismatch|\bdoes ?n[o']t match|\bdisputed?|\bnot (captured|"
                r"uploaded))")
_COMMERCIAL_PAPER = r"(\bPOD\b|proof of delivery|delivery (note|documents|paperwork)|\be-?POD\b|\bsignature|\bsign(ed)?\b)"
_REGULATORY_PAPER = (r"(customs|declaration|\bCMR\b|consignment note|certificate|dangerous goods "
                     r"note|\bDGN\b|tachograph|\btacho\b|driver card|\bCPC\b|permit|licence"
                     r"|\bENS\b|\bT1\b|transit|export|import)")

# --- Category rules (section 2) --------------------------------------------------------------
CATEGORY_RULES: dict[Category, list[Rule]] = {
    # C6 safety_incident: hurt, ill, collision, fire, dangerous-goods leak, unsafe load,
    # threats, near miss, hazard report. A breakdown in a live lane or the vehicle's own fuel
    # leak is not C6 (C6 excludes), so neither has a rule here.
    C.SAFETY_INCIDENT: [
        _rule("C6 injury", r"\binjur(y|ies|ed)\b|\bhurt\b|\bgrazed?\b|\bbruis\w*|\bbleeding\b"
              r"|\bfirst aid\b|\bambulance\b|\bparamedics?\b|\bcuts? to\b", 3),
        _rule("C6 taken ill", r"\bchest (pain|is tight|tight)|\bcollaps\w*|\bfaint\w*"
              r"|\bunconscious|\b(arm|leg) (has )?(gone )?numb|\btaken ill|\bheart attack"
              r"|\bfeeling (unwell|ill|faint)", 3),
        _rule("C6 collision", r"\bcollision\b|\bcollided\b|\bcrash(ed)?\b|\bclipped\b|\bbump(ed)?"
              r"\b|\bran into\b|\bhit (a|the|another) (?!limit|traffic|queue|delay)|\bbollard\b"
              r"|\bbridge strike\b|\bstruck (a|the)\b", 3),
        _rule("C6 fire", r"\bfire\b|\bflames?\b|\bblaze\b|\bon fire\b", 3,
              unless=r"fire (brigade|exit|extinguisher)s? (?!called)"),
        _rule("C6 dangerous goods leak", _DG + r".*\b(leak\w*|spill\w*|seep\w*)|\b(leak\w*|"
              r"spill\w*|seep\w*).*" + _DG, 3, unless=_NO_LEAK),
        _rule("C6 drum leak", r"\b(drums?|IBCs?|containers?)\b.*\bleak\w*", 2,
              unless=_NO_LEAK),
        _rule("C6 unsafe load", r"\b(load|coils?|pallets?|cargo|stillages?)\s(has |have )?"
              r"(shifted|shifting|slipped|moved)|\bbulging\b|\bunsafe load\b|\bcould (come|fall)"
              r" (through|off|out)|\b(fall|falling) (off|onto)", 3),
        _rule("C6 threat", r"\bthreat\w*|\bassault\w*|\babusive\b|\battack\w*|\bweapons?\b"
              r"|\bknife\b|\bpunch\w*|\b(trying|tried) to (open|get into|break into)", 3),
        _rule("C6 near miss", r"\bnear miss\b|\bnearly (hit|crashed|killed|ran)|\bcut (in|me up)"
              r"\b|\bbrake[ds]? hard\b|\bhad to brake\b", 2.5, negatable=False),
        _rule("C6 unsafe reversing", r"\bwithout a banksman\b|\bno banksman\b", 2, negatable=False),
        _rule("C6 hazard report", r"\bhazard\b|\bfloodlights?\b|\blighting\b|\bslippery\b"
              r"|\bracking\b|\bpedestrians?\b|\bbanksman\b", 1.5),
    ],
    # C1 vehicle_breakdown: fault or immobilisation of vehicle, trailer, reefer or tail-lift.
    C.VEHICLE_BREAKDOWN: [
        _rule("C1 broken down", r"\bbroken down\b|\bbreakdown\b|\bbroke down\b|\bwon'?t start\b"
              r"|\bwill not start\b|\bimmobilis\w*|\bcan(no|')t be moved\b", 2.5),
        _rule("C1 component failed", r"\b(gearbox|clutch|engine|alternator|turbo|brakes?|air "
              r"(line|leak)|radiator|battery|starter motor|injector|axle|suspension|steering|"
              r"(fan|drive) belt)\b.*\b(fail\w*|gone|went|broke\b|fault\w*|dead|flat|leak\w*|"
              r"locked|overheat\w*|seized|packed up)", 2.5),
        _rule("C1 air leak", r"\bair leak\b", 1.5),
        _rule("C1 tyre", r"\bpunctur\w*|\bblow-?out\b|\bflat tyre|\btyres? (has |have )?(burst|"
              r"blew|gone|blown|flat)|\btyre service\b|\bspare (wheel )?(is )?missing", 2.5),
        _rule("C1 warning light", r"\bwarning light|\blimp mode\b|\bloss of power\b"
              r"|\blost power\b", 1.5),
        _rule("C1 light cleared, no fault (C1 excludes)", r"\bno fault found\b|\bfound no fault|\b(light|warning|"
              r"engine light) (has )?cleared\b|\bcleared (at|after) ", -5, negatable=False),
        _rule("C1 reefer failed", r"\b(reefer|fridge|refrigeration|chiller)( unit)?\b.*\b("
              r"stopped|fail\w*|not working|died|cut out|alarm\w*|packed up|broken|fault)", 2.5),
        _rule("C1 tail-lift failed", r"\btail-?lift\b.*\b(fail\w*|broke\w*|stuck|won'?t|"
              r"not working|jammed)", 2.5),
        _rule("C1 recovery", r"\brecovery\b|\bmechanic\b|\btow(ed|ing)?\b|\bfitter\b", 1),
        _rule("C1 own fuel leak", r"\b(diesel|fuel) tank\b.*\b(split|leak\w*|holed|punctured|"
              r"crack\w*)|\b(split|holed|punctured|cracked)\b.*\b(diesel|fuel) tank\b"
              r"|\bdiesel (is )?(pouring|leaking|everywhere)", 2.5),
        _rule("C1 criminal immobilisation (X5 cause)", _CRIMINAL_IMMOBILISATION, 2.5,
              negatable=False),
        _rule("C1 roadside prohibition for a defect", r"\bprohibition\b|\bdefects?\b", 1.5),
    ],
    # C2 delivery_delay: late or undeliverable at its slot, goods intact and accounted for.
    C.DELIVERY_DELAY: [
        _rule("C2 late", r"\b(running|be|is|are|was|were|arrive|arriving) (\w+ ){0,3}(late|"
              r"behind)\b|\blate (delivery|for|arrival)\b|\bdelay\w*|\bETA\b|\bwill be late\b"
              r"|\bdelivered tomorrow\b|\bmiss(es)? (its|the|our) slot\b", 1.5),
        _rule("C2 road cause", r"\btraffic\b|\bqueues?\b|\b(road|motorway|carriageway) (is |was "
              r")?(closed|shut)\b|\bclosed (eastbound|westbound|northbound|southbound|for)\b"
              r"|\bclosure|\bdiversion|\bsnow\b|\bflooding\b|\bfog\b|\bgridlock", 1),
        _rule("C2 site cause", r"\bgates? (were |was )?(locked|closed)|\bsite (was )?(closed|"
              r"shut)|\brefused (the|our) slot|\bbacklog\b|\b(told|asked) (the driver|me|him|us) "
              r"to wait|\bno answer\b|\bslot (was )?(moved|cancelled)", 1.5),
        _rule("C2 driver availability (X3 cause)", _DRIVER_HOURS, 1.5, negatable=False),
        _rule("C2 authority hold (X6 cause)", _AUTHORITY + r".*\b(held|hold|holding|stopped|"
              r"examin\w*|check\w*|pulled)|\b(held|stopped)\b.*" + _AUTHORITY, 1.5),
        _rule("C2 on its way", r"\bon (its|the) way\b|\bnot arrived yet\b", 1),
    ],
    # C3 shipment_damage: goods damaged, spoiled, wet, contaminated or temperature-abused.
    C.SHIPMENT_DAMAGE: [
        _rule("C3 damaged goods", r"\b(damaged?|crushed|smashed|cracked|dented|torn|ripped|"
              r"soaked|water damage|contaminated|spoil(ed|t)|ruined|holes|broken(?! (down|into))"
              r")\b", 2, unless=r"\b(tyre|tank|lights?|floodlights?|curtain|seal|lid on the "
              r"fuel)\b(?!.*\b(goods|pallets?|cartons?|load|devices|tiles|stock)\b)"),
        _rule("C3 damage reservation or rejection", r"\brejected\b|\brefused (it|delivery|the "
              r"(load|delivery|goods))|\bdamage reservation|\bnoted the damage|\bsigned (for )?"
              r"(as )?damaged", 1.5),
        _rule("C3 temperature abuse", r"\bout of (temp|temperature|spec)\b|\btemperature "
              r"abuse", 1.5),
    ],
    # C4 missing_shipment: short, never loaded, wrong address or vehicle, lost or stolen.
    C.MISSING_SHIPMENT: [
        _rule("C4 goods missing", r"\b(pallets?|cartons?|cases|boxes|parcels?|consignment|goods|"
              r"items?|order|units?|cages?)\b[^.]*\b(short|missing|lost|stolen|not (been )?"
              r"(received|delivered|on the (van|vehicle|trailer|lorry))|has ?n'?t (arrived|turned"
              r" up)|never (arrived|turned up)|isn'?t on the (van|vehicle|trailer|lorry))\b", 2.5,
              negatable=False),
        _rule("C4 short", r"\b(\w+ )?pallets? short\b|\bshort (by|of) \w+|\bshortage\b|\b(missing|lost) (pallets?|cartons?|cases|boxes|parcels?|items?|"
              r"cages?)\b", 2.5,
              negatable=False),
        _rule("C4 wrong place (X1 explanation)", r"\bdelivered (\w+ ){0,4}to the wrong|\bwrong "
              r"(address|store|unit|site|depot|vehicle|trailer|lorry|van)\b|\bmeant for\b"
              r"|\b(old|previous) (address|premises)|\bby mistake\b|\bmis-?pick\w*|\bleft behind"
              r"\b|\bnot loaded\b|\b(delivered|gone|sent|taken) (\w+ ){0,6}to [^.]{0,40}"
              r"\binstead of\b|\bmade an error reading", 2.5, negatable=False),
        _rule("C4 theft", r"\bstolen\b|(?<!fuel )\btheft\b|\bthieves\b", 2.5),
        _rule("C4 whereabouts unknown", r"\btracker\b[^.]*\b(moving|leaving|left|off|heading)"
              r"|\bshowing a move\b|\bmove away\b"
              r"|\bno [^.]{0,25}(move|movement) (is |was )?(scheduled|planned|booked)|\bunplanned "
              r"(move|movement)|\b(can'?t|cannot|unable to) (contact|reach|get hold of)( the| "
              r"our| their)? driver|\bno idea where\b|\bwhereabouts\b|\bnobody knows where", 2,
              negatable=False),
    ],
    # C5 documentation_issue: paperwork or records missing, wrong or disputed.
    C.DOCUMENTATION_ISSUE: [
        _rule("C5 paperwork problem", _DOC_WORD + r"[^.]*" + _DOC_PROBLEM + "|" + _DOC_PROBLEM
              + r"[^.]*" + _DOC_WORD, 3, negatable=False, unless=r"\bseals?\b|\b(pallets?|"
              r"cartons?|goods) (\w+ )?(short|missing)|\bagainst the manifest"),
        _rule("C5 paperwork mentioned", _DOC_WORD, 0.5),
        _rule("C5 paperwork stated fine (I3: X6 needs paperwork not at fault)",
              r"\bin order\b|\b(paperwork|documents|declarations?)('s| is| are| was)? (all )?"
              r"(fine|ok|correct)", -3, negatable=False),
        _rule("C5 check-in refused", r"\b(check-?in|boarding)\b[^.]*\brefused", 1.5),
    ],
}

# --- Urgency rules (section 4). Hard rules give 0.95; ambiguous cues give 0.5. ---------------
# I2: a trigger stated as possible counts, so hedges ("I think") are not negations here.
# I3: if the report contradicts itself, any reading that meets a trigger makes it urgent; the
# hard rules simply fire on either reading.
_MEDICAL = (r"\b([Ii]nsulin|[Vv]accines?|[Mm]edicines?|[Mm]edication|pharmacy|pharmaceuticals|"
            r"[Hh]ospital|clinic|[Bb]lood|[Pp]lasma|[Dd]ialysis|reagents?|lab supplies|"
            r"laboratory|medical|surgical|[Cc]hemotherapy)\b")  # lower-case: "Halcyon Medical"
# is a customer name, and a name alone does not make goods medical (U5).
_DEADLINE = (r"\bline[- ]stop|\bpenalty|\bproduction line|\bferry (cut-?off|booking)|\bmust be "
             r"(there|delivered|on site) by|\b(contract|timed) (slot|deadline)|\bdeadline\b"
             r"|\bcut-?off\b|\bjust-in-time\b|\bJIT\b")
_WILL_MISS = (r"\b(will|going to|gonna|likely to|set to|bound to) miss|\bwon'?t make|\bwill not "
              r"make|\bcan'?t make|\bcannot make|\bnot going to make|\bno way (to|of) (get|make)"
              r"|\bmiss(ed|ing)? (the|its|our|their|his|her) (slot|window|deadline|cut-?off|"
              r"sailing|ferry)|\b(cannot|can'?t) (reach|get there|get it there)[^.]*\bin time"
              r"|\btoo late\b|\bwill be missed|\bwon['’]t be made\b|\b(can['’]?t|cannot|won['’]t) "
              r"(get|reach)\b[^.]{0,60}\b(before|by)\b")
_WILL_MAKE = r"\b(will |should )?still make\b|\bon time\b|\bin time\b(?<!not in time)"

URGENCY_RULES: list[Rule] = [
    # U1 someone hurt (any injury) or a person in danger now.
    _rule("U1 injury", r"\binjur(y|ies|ed)\b|\bhurt\b|\bgrazed?\b|\bbruis\w*|\bbleeding\b"
          r"|\bfirst aid\b|\bambulance\b|\bparamedics?\b|\bcuts? to\b"),
    _rule("U1 taken ill", r"\bchest (pain|is tight|tight)|\bcollaps\w*|\bfaint\w*"
          r"|\bunconscious|\b(arm|leg) (has )?(gone )?numb|\btaken ill|\bheart attack"),
    _rule("U1 in danger now", r"\btrapped\b|\bon foot\b[^.]*\btraffic|\bthreat\w*|\bassault\w*"
          r"|\b(trying|tried) to (open|get into|break into)|\bfire\b|\bflames\b|\bmoved people "
          r"away|\bkept people away|\bcould (come|fall) (through|off|out)|\bbulging\b"
          r"|\b(load|coils?|pallets?) (has |have )?(shifted|shifting)",
          unless=r"\bfire (brigade|exit|extinguisher)s? (?!called)"),
    # U2 dangerous goods leaking or in damaged packaging; fuel/oil/chemical spill on a road.
    _rule("U2 dangerous goods leaking", _DG + r".*\b(leak\w*|spill\w*|seep\w*)|\b(leak\w*|"
          r"spill\w*|seep\w*).*" + _DG, unless=_NO_LEAK),
    _rule("U2 drum leaking", r"\b(drums?|IBCs?)\b.*\bleak\w*", unless=_NO_LEAK),
    _rule("U2 dangerous goods packaging damaged", _DG + r".*\b(dented|cracked|damaged|split|"
          r"punctured|crushed)"),
    _rule("U2 spill on a road", r"\b(diesel|fuel|oil|chemicals?)\b[^.]*\b(pouring|spill\w*|"
          r"leak\w*|running)\b[^.]*\b(road|carriageway|lane|lay-by|junction)|\bspill\w* "
          r"(on|across) the (road|carriageway)"),
    _rule("U2 uncontained spill", r"\bspill\w*\b[^.]*\b(not contained|uncontained|spreading)",
          negatable=False),
    # U3 vehicle stopped in a live lane (not hard shoulder, emergency area or lay-by).
    _rule("U3 live lane", r"\blive lane\b|\blane (1|one|2|two|3|three)\b|\brunning lane|"
          r"\b(inside|outside|middle) lane\b|\bin the (lane|road|carriageway)\b|\bblocking (the|"
          r"a) (lane|road|junction|carriageway)|\bsingle carriageway|\bslip ?road\b|\bon (the|a) "
          r"roundabout|\bin (the|a) junction|\bstraddl\w*|\bunder (the|a) bridge"),
    _rule("U3 traffic passing", r"\btraffic (is )?(going|passing|getting|squeezing) (round|past)"
          r"|\bcars? (are |were )?(having to )?(swerv\w*|go(ing)? round)"),
    # U4 temperature-controlled load still in our care with refrigeration failing.
    _rule("U4 refrigeration failing", r"\b(reefer|fridge|refrigeration|chiller)( unit)?\b.*\b("
          r"stopped|fail\w*|not working|died|cut out|alarm\w*|packed up|broken)",
          unless=r"\b(restarted|back (on|up|running|working)|cleared|running normally|in range)"
          r"\b|\breject\w*"),
    _rule("U4 temperature rising", r"\btemp(erature)? (is |has been )?(rising|climbing|going up|"
          r"out of range)|\bout of range\b", unless=r"\breject\w*|\bdownload"),
    _rule("U4 refrigeration will stop", r"\b(reefer|fridge|unit)( unit)? fuel\b[^.]*\b(run "
          r"out|running out|low|empty|(hours?|minutes?) (left|remaining)|remaining)"
          r"|\bno refuel\w*|\bnot allowed to refuel|\bwon['’]t allow refuell?ing|\brefuell?ing (isn['’]t|is not|not) allowed"),
    # U6 theft in progress, loaded vehicle missing with driver unreachable, load space breached.
    _rule("U6 load space breached", _BREACH, negatable=False),
    _rule("U6 unplanned move", r"\btracker\b[^.]*\b(moving|leaving|heading)|\bshowing a move\b"
          r"|\bmove away\b|\bno [^.]{0,25}(move|movement) (is |was )?(scheduled|planned|booked)|\bunplanned (move|movement)",
          negatable=False),
    _rule("U6 driver unreachable", r"\b(can'?t|cannot|unable to) (contact|reach|get hold of)"
          r"( the| our| their)? driver|\bdriver (is )?not answering|\btracker (has been |is )?off",
          negatable=False),
    _rule("U6 theft in progress", r"\bthieves\b|\bmen (at|around|by|in) the (trailer|lorry|truck|"
          r"cab)", negatable=False),
]
# Ambiguous cues (0.5) that need a fact the report does not settle.
_STOPPED_ON_ROAD = _rule("U3 ambiguous: stopped on a road, position not stated",
                         r"\b(pulled over|stopped|stuck|broken down|broke down)\b[^.]*\b([MA]\d+"
                         r"(\(M\))?)\b", unless=r"\b(in|by) (traffic|a queue|queues)\b|\bby (the )?"
                         r"(police|DVSA|officers|Border Force)")
_OFF_LIVE_LANE = _re(r"\bhard shoulder|\blay-?by|\bemergency (area|refuge)|\bverge\b|\bservices"
                     r"\b|\bdepot\b|\byard\b|\btruck (stop|park)|\bHGV park|\bcar park")
_FROZEN_SOON = _re(r"\bfrozen\b|\bice cream\b|-1[5-9]|-2\d")
_WITHIN_HOUR = _re(r"\b([1-5]?\d) (minutes|mins)\b|\bwithin (the|an|1) hour|\btip(ped)? on "
                   r"arrival|\bcold store\b")
_TIME = _re(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b")
_SLOT_TIME = _re(r"\b(slot|window|due|deadline|by)\b[^.\d]{0,15}(\d{1,2}[:.]\d{2})")
_ETA_TIME = _re(r"\b(ETA|arrive|arriving|there about|there at|get there)\b[^.\d]{0,15}"
                r"(\d{1,2}[:.]\d{2})")

# --- Destination exceptions (section 5); each applies to one Category only. -------------------
_X1_EXPLANATION = _re(r"\bdelivered (\w+ ){0,4}to the wrong|\bwrong (address|store|unit|site|"
                      r"depot|vehicle|trailer|lorry|van)\b|\bmeant for\b|\b(old|previous) "
                      r"(address|premises)|\bby mistake\b|\bmis-?pick\w*|\bleft behind\b"
                      r"|\bnot loaded\b|\bmade an error reading|\bhand them back|\b(left|stayed) in "
                      r"(the|a) (\w+ ){1,2}(store|room|bay|yard)\b"
                      r"|\bcross-?dock\w* (onto|on to) the wrong|\bmoved (with)?in "
                      r"the yard")
_X2_COMMERCIAL = _re(_COMMERCIAL_PAPER)
_X2_REGULATORY = _re(_REGULATORY_PAPER)
_X3_DRIVER = _re(_DRIVER_HOURS)
_X4_BREACH = _re(_BREACH)
_X5_CRIMINAL = _re(_CRIMINAL_IMMOBILISATION)
_X6_AUTHORITY = _re(_AUTHORITY)

# --- Information gaps (section 6): Review Triggers, never a reason to change the Label. -------
_LOCATION = _re(r"\b[MA]\d{1,4}(\(M\))?\b|\bJ\d+\b|\bjunction \d+|\bdepot\b|\bservices\b|\blay-?"
                r"by\b|\byard\b|\bRDC\b|\bwarehouse\b|\bstore\b|\bsite\b|\bdocks?\b|\bport\b"
                r"|\bhard shoulder\b|\btruck (stop|park)\b|\bbay\b|\bbranch\b", re.IGNORECASE)
_PLACE_NAME = re.compile(r"\b(near|at|in|outside|to|from|for) [A-Z][a-z]{2,}")
_CARGO = _re(r"\b(pallets?|cartons?|drums?|cases|boxes|parcels?|consignment|loaded with|carrying"
             r"|cargo|goods|stock|products?|furniture|food|tins|tinned|tiles|flooring|chilled|"
             r"frozen|ambient|insulin|vaccines?|laptops|tablets|devices|wine|whisky|beer|paper|"
             r"parts|cheese|yoghurts?|groceries|homeware|steel|coils?|beverages|chairs|"
             r"televisions?|sofas?|paint|chemicals?|medicines?|fluids|reagents|ice cream|butter|"
             r"cereals?|empty|soup|electronics|clothing|textiles|machinery|timber|bricks|"
             r"cement|fertiliser|meat|fish|fruit|vegetables|dairy|milk)\b")


def _fired(rule: Rule, sentence: str) -> bool:
    if rule.unless is not None and rule.unless.search(sentence):
        return False
    return any(_affirmed(sentence, m, rule) for m in rule.pattern.finditer(sentence))


def _minutes(hhmm: str) -> int:
    h, m = re.split(r"[:.]", hhmm)
    return int(h) * 60 + int(m)


def _u5(text: str) -> float | None:
    """U5: medical or flagged-deadline consignment that will miss its window.

    Arithmetic stays in code: an ETA later than the stated slot is a miss.
    """
    if not (_re(_MEDICAL, 0).search(text) or _fired(_rule("U5", _DEADLINE), text)):
        return None
    if _re(_WILL_MISS).search(text):
        return HARD_URGENT
    slot, eta = _SLOT_TIME.search(text), _ETA_TIME.search(text)
    if slot and eta:
        return HARD_URGENT if _minutes(eta.group(2)) > _minutes(slot.group(2)) else NO_URGENCY
    if _re(_WILL_MAKE).search(text):
        return NO_URGENCY
    if any(_fired(r, text) for r in CATEGORY_RULES[C.DELIVERY_DELAY][:3]):
        return AMBIGUOUS_URGENT  # held up, but the report does not say the window is lost
    return None


def _urgency(sentences: list[str], text: str) -> tuple[float, set[int]]:
    """Return (urgent_prob, indexes of sentences whose urgency rules fired)."""
    hard = {i for i, s in enumerate(sentences) for r in URGENCY_RULES if _fired(r, s)}
    # U4 frozen: not at risk if back in working refrigeration within 1 hour. The rules cannot
    # tell "within the hour" reliably, so a frozen load with a short-time cue is ambiguous.
    u4 = {i for i in hard if any(_fired(r, sentences[i]) for r in URGENCY_RULES
                                 if r.code.startswith("U4"))}
    if u4 and hard == u4 and _FROZEN_SOON.search(text) and _WITHIN_HOUR.search(text):
        return AMBIGUOUS_URGENT, u4
    u5 = _u5(text)
    u5_sentences = {i for i, s in enumerate(sentences)
                    if _re(_MEDICAL, 0).search(s) or _re(_DEADLINE).search(s)}
    if hard:
        return HARD_URGENT, hard | (u5_sentences if u5 == HARD_URGENT else set())
    if u5 == HARD_URGENT:
        return HARD_URGENT, u5_sentences
    stopped = {i for i, s in enumerate(sentences) if _fired(_STOPPED_ON_ROAD, s)}
    if u5 == AMBIGUOUS_URGENT or (stopped and not _OFF_LIVE_LANE.search(text)):
        return AMBIGUOUS_URGENT, stopped | u5_sentences
    return NO_URGENCY, set()


def _destination(category: Category, text: str, theft_sign: bool) -> tuple[Destination, str]:
    """D0 default for the Category, unless that Category's exception applies."""
    if category == C.MISSING_SHIPMENT and _X1_EXPLANATION.search(text) and not theft_sign:
        return D.CUSTOMER_DESK, "X1"
    if (category == C.DOCUMENTATION_ISSUE and _X2_COMMERCIAL.search(text)
            and not _X2_REGULATORY.search(text)):
        return D.CUSTOMER_DESK, "X2"
    if category == C.DELIVERY_DELAY and _X3_DRIVER.search(text):
        return D.FLEET_SUPPORT, "X3"
    if category == C.SHIPMENT_DAMAGE and _X4_BREACH.search(text):
        return D.SECURITY_INVESTIGATIONS, "X4"
    if category == C.VEHICLE_BREAKDOWN and _X5_CRIMINAL.search(text):
        return D.SECURITY_INVESTIGATIONS, "X5"
    if category == C.DELIVERY_DELAY and _X6_AUTHORITY.search(text):
        return D.COMPLIANCE, "X6"
    return DEFAULT_DESTINATION[category], "D0"


_EXCEPTION_PATTERNS = {"X1": _X1_EXPLANATION, "X2": _X2_COMMERCIAL, "X3": _X3_DRIVER,
                       "X4": _X4_BREACH, "X5": _X5_CRIMINAL, "X6": _X6_AUTHORITY}


def _category_scores(sentences: list[str]) -> tuple[dict[Category, float], dict[Category, set]]:
    scores = {c: 0.0 for c in C}
    fired_in: dict[Category, set[int]] = {c: set() for c in C}
    for c, rules in CATEGORY_RULES.items():
        for rule in rules:
            for i, s in enumerate(sentences):
                if _fired(rule, s):
                    scores[c] += rule.weight
                    if rule.weight > 0:
                        fired_in[c].add(i)
    scores = {c: max(0.0, v) for c, v in scores.items()}
    # P2: a delay is never primary when its cause is another Category.
    if max(scores[c] for c in C if c != C.DELIVERY_DELAY) >= 2:
        scores[C.DELIVERY_DELAY] *= 0.25
    # P3: damage or loss wins over the vehicle fault or paperwork that led to it.
    if max(scores[C.SHIPMENT_DAMAGE], scores[C.MISSING_SHIPMENT]) >= 2:
        scores[C.VEHICLE_BREAKDOWN] *= 0.4
        scores[C.DOCUMENTATION_ISSUE] *= 0.4
    # P1: safety always wins once a strong safety cue is present.
    if scores[C.SAFETY_INCIDENT] >= 2.5:
        scores[C.SAFETY_INCIDENT] *= 2
    return scores, fired_in


def predict(report: Report) -> Prediction:
    start = time.perf_counter()
    text = report.text
    sentences = split_sentences(text)
    scores, fired_in = _category_scores(sentences)
    no_match = all(v == 0 for v in scores.values())
    total = sum(scores.values()) + SMOOTHING * len(scores)
    probs = {c: (scores[c] + SMOOTHING) / total for c in C}
    # With no rule fired nothing was observed, so P4's safety-first tie-break must not decide;
    # fall back to the most common routine Category (C2) and let the Review Triggers flag it.
    order = ([C.DELIVERY_DELAY] + [c for c in P4_ORDER if c != C.DELIVERY_DELAY]
             if no_match else P4_ORDER)
    ranked = sorted(order, key=lambda c: -probs[c])  # stable: ties follow the order
    category = ranked[0]

    urgent_prob, urgency_sentences = _urgency(sentences, text)
    theft_sign = any(_fired(r, s) for s in sentences for r in URGENCY_RULES
                     if r.code.startswith("U6"))
    dest_of = {c: _destination(c, text, theft_sign) for c in C}
    destination, exception = dest_of[category]
    dest_probs = {d.value: 0.0 for d in D}
    for c in C:
        dest_probs[dest_of[c][0].value] += probs[c]

    evidence_ids = set(fired_in[category]) | urgency_sentences
    if exception != "D0":
        evidence_ids |= {i for i, s in enumerate(sentences)
                         if _EXCEPTION_PATTERNS[exception].search(s)}

    triggers = []
    if no_match:
        triggers.append("no_rule_matched")
    elif probs[ranked[0]] - probs[ranked[1]] < CONFLICT_MARGIN:
        triggers.append("conflicting_categories")
    if not (_LOCATION.search(text) or _PLACE_NAME.search(text)):
        triggers.append("location_missing")
    if not _CARGO.search(text):
        triggers.append("cargo_missing")

    return Prediction(
        report_id=report.report_id,
        approach="A",
        category=category,
        category_probs={c.value: probs[c] for c in C},
        urgent_prob=urgent_prob,
        destination=destination,
        destination_probs=dest_probs,
        evidence=[sentences[i] for i in sorted(evidence_ids)],
        triggers=triggers,
        latency_ms=(time.perf_counter() - start) * 1000,
        input_tokens=0,
        output_tokens=0,
        attempts=1,
        error=None,
        model=None,
        version=RULES_VERSION,
    )
