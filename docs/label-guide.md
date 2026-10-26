# Label guide

How to give an Incident Report its Label: one Category, one Urgency and one Destination. Use it
blind: decide from the report text alone, never from who wrote it or how worried they sound.

Work in this order: **Category** (sections 2 and 3), then **Urgency** (section 4, decided on its
own, whatever the Category), then **Destination** (section 5: the default for the Category, then
the exceptions for that Category). Rule codes in brackets (`C3`, `U4`, `X2` …) are what a Seeded
Label's reason cites.

## 1. Quick reference

Category codes: `C1` `vehicle_breakdown`, `C2` `delivery_delay`, `C3` `shipment_damage`,
`C4` `missing_shipment`, `C5` `documentation_issue`, `C6` `safety_incident`.

| Step | Rule | Decide |
|---|---|---|
| Category | `P1` | Anyone hurt or taken ill, staff threatened, a collision, fire, a leak of dangerous goods, an unsafe load, a near miss or a hazard report → `safety_incident`. Always wins. A breakdown in a live lane on its own stays `C1`. |
| | `P2` | A delay caused by something in another Category → that other Category. |
| | `P3` | Goods damaged or missing → that outcome wins over the vehicle fault or paperwork that led to it. |
| | `P4` | Unrelated issues in one report: safety > missing > damage > breakdown > documentation > delay. |
| Urgency | `U1` | Someone hurt (any injury) or a person in danger now. |
| | `U2` | Dangerous goods leaking, spilled or with damaged packaging; any fuel, oil or chemical spill on a road or an uncontained spill on site. |
| | `U3` | Vehicle stopped in a live lane (not a hard shoulder, emergency area or lay-by). |
| | `U4` | Load still in our care. Chilled: refrigeration not working or about to stop. Frozen: same, and not restored within 1 hour. |
| | `U5` | Medical consignment, or one with a flagged deadline, that will miss its window. |
| | `U6` | Theft in progress, a loaded vehicle missing with its driver unreachable, or the load space breached (seal broken, missing or mismatched; curtain slashed; doors forced). |
| | `U0` | None of the above → `routine`. Tone does not count. |
| Destination | `D0` | breakdown → `fleet_support`; delay → `customer_desk`; damage → `claims`; missing → `security_investigations`; documentation → `compliance`; safety → `safety_desk`. |
| | `X1` | Missing, innocent explanation stated, no theft sign → `customer_desk`. |
| | `X2` | Documentation, commercial delivery paperwork only (POD, delivery note) → `customer_desk`. |
| | `X3` | Delay caused by driver availability (hours limit, rest, no driver) → `fleet_support`. |
| | `X4` | Damage with the load space breached or tampered with → `security_investigations`. |
| | `X5` | Breakdown caused by criminal interference (fuel theft, cut lines, vandalism) → `security_investigations`. |
| | `X6` | Delay because an authority holds the vehicle or load, paperwork not at fault → `compliance`. |
| | — | `safety_incident` has no exceptions: always `safety_desk`. |
| Gaps | `I1` | Label from what is stated. A trigger that is not stated or clearly implied does not count. |
| | `I2` | A trigger stated as possible ("I think it's leaking") counts. |
| | `I3` | Report contradicts itself: if either reading meets an Urgency trigger → `urgent`; otherwise specific evidence beats a general assurance. |

## 2. Categories

### C1 `vehicle_breakdown`

**Definition.** The vehicle, trailer or equipment fitted to it has a fault or is immobilised:
mechanical or electrical failure, puncture or blow-out, flat battery, warning light with loss of
power, a failed refrigeration (reefer) unit, a failed tail-lift, a defect that stops the vehicle
at a roadside check, or immobilisation by fuel theft or vandalism.

**Excludes.** Collisions and fires (`safety_incident`). A vehicle fault that has already damaged
or lost goods (`shipment_damage` or `missing_shipment`, by `P3`). A warning light that cleared
with no fault found (whatever caused the report is the Category).

**Borderline.**
- Tail-lift fails at the customer's site; the pallets cannot come off but are undamaged → `C1`.
  If the tail-lift had dropped a pallet and broken the goods → `C3`.
- The vehicle's own diesel tank splits and fuel runs onto the road; no collision, nobody hurt →
  `C1` (urgent by `U2`). A leak from dangerous goods cargo is `C6`.

### C2 `delivery_delay`

**Definition.** A consignment is late, will be late, or could not be delivered at its booked time,
and the goods are intact and accounted for. Causes include traffic, road closures, weather, late
loading at the consignor, a customer site closed or refusing the slot, driver hours, and holds by
an authority where the paperwork is in order.

**Excludes.** Delays caused by a vehicle fault (`C1`), damage (`C3`), lost goods (`C4`), faulty or
missing paperwork (`C5`) or a collision (`C6`): see `P2`.

**Borderline.**
- Held at Dover for a Border Force examination; the declaration is correct → `C2` (then `X6`). If
  held because the declaration is missing or wrong → `C5`.
- Customer says "our order hasn't arrived" and the report gives an ETA or says it is on its way →
  `C2`. If nobody knows where it is → `C4`.

### C3 `shipment_damage`

**Definition.** Goods are physically damaged, spoiled, wet, contaminated or temperature-abused,
found at any point: loading, transit, cross-dock or delivery. Includes a consignee's damage
reservation written on a POD or CMR.

**Excludes.** Damaged dangerous goods that are leaking (`C6`). Goods not present (`C4`). Damage to
the vehicle only, with the goods intact (`C1`, or `C6` if it was a collision).

**Borderline.**
- Drums of class 3 paint with dented packaging and a cracked lid, no leak seen → `C3` (urgent by
  `U2`). The same drums leaking → `C6`.
- Reefer download at delivery shows the chilled load at 11 °C for three hours and the RDC rejects
  it → `C3` by `P3`: the loss has happened. Reefer failing in transit with the load still
  saveable → `C1`.

### C4 `missing_shipment`

**Definition.** Goods are not where they should be: short on delivery, never loaded, delivered to
the wrong address, put on the wrong vehicle, lost in transit, or stolen. Includes a whole loaded
vehicle or trailer whose whereabouts are unknown.

**Excludes.** Goods that are late but located (`C2`). Paperwork showing the wrong quantity while
the goods themselves are correct (`C5`).

**Borderline.**
- Three pallets short and two crushed in one delivery → `C4` by `P4` (missing beats damage).
- Delivered to the customer's old address because the label was out of date → `C4` by `P3`, not
  `C5`: the goods being in the wrong place is what is acted on.

### C5 `documentation_issue`

**Definition.** Paperwork or records are missing, wrong or disputed: CMR consignment notes,
delivery notes, PODs, customs and transit declarations, health certificates, dangerous goods
notes, tachograph records, driver cards and permits.

**Excludes.** Cases where the paperwork is fine and the goods are missing (`C4`) or damaged
(`C3`). A damage reservation written on a CMR is `C3`.

**Borderline.**
- A chilled load is held at Dover because its health certificate is missing → `C5` by `P2`, even
  though the visible effect is a delay.
- Tachograph download shows a drivers' hours infringement, and yesterday's delivery was late →
  `C5` by `P4` (documentation beats delay).

### C6 `safety_incident`

**Definition.** Anything where a person was hurt, was or is at risk, or could have been: injury,
a driver taken ill at work, collision of any size (including with a bollard or bridge), fire,
leak or spill of dangerous goods cargo, an unsafe or shifting load, threats or violence against
staff, a near miss, or a hazard report about a site or vehicle.

**Excludes.** Nothing outranks it (`P1`), but two cases are not safety incidents: a vehicle's
own fuel leak from a mechanical fault with no collision and nobody hurt is `C1`; and a breakdown
that leaves the vehicle in a live lane, with no collision and nobody hurt, is `C1` (urgent by
`U3`).

**Borderline.**
- Two men try to open the trailer doors at a lay-by while the driver is in the cab → `C6` (threat
  to staff), urgent by `U1` and `U6`. The same theft discovered next morning with the driver
  never confronted → `C4`.
- A car cuts in on the M1 and the driver brakes hard; no contact, nobody hurt → `C6` (near miss),
  routine by `U0`.

## 3. Primary Category for multi-issue reports

Apply in order; stop at the first that fits.

- **P1 Safety always wins.** If any part of the report is a safety incident, the Category is
  `safety_incident`, even if it is not the main subject. *Brake fire on a trailer at services
  → `C6`, not `C1`.*
- **P2 A delay is never primary when its cause is another Category.** *Breakdown causing a late
  delivery → `C1`. Customs paperwork missing, so the load is held → `C5`.*
- **P3 Damage or loss wins over its cause.** The claim or investigation is what is acted on.
  *Tail-lift drops a pallet of tiles → `C3`. Wrong address on the label, goods delivered
  elsewhere → `C4`. Roof leak soaks flat-pack furniture → `C3`.*
- **P4 Unrelated issues: fixed order.** safety > missing > damage > breakdown > documentation >
  delay. *Pallets short, and the POD was not signed → `C4`.*

A warning light that cleared with no fault found is not a breakdown; if the report is really
about the traffic jam that followed, it is `C2`.

## 4. Urgency

Urgency is decided independently of Category. `urgent` if **any** trigger below is stated or
clearly implied; otherwise `routine` (`U0`). Swearing, capitals and "disaster" do not make a
report urgent; calm phrasing does not make it routine.

- **U1 Someone hurt or at risk.** Any injury to anyone, however minor (a cut that needed first
  aid counts), or a person in danger now: on foot in or beside moving traffic, trapped, threatened,
  taken ill at work (chest pain, collapse), or exposed to a load that may fall where people are.
  A near miss that is over, with nobody hurt and no continuing danger, is not `U1`; nor is a
  hazard report (broken lighting, damaged racking) with nobody hurt and no one in immediate danger.
- **U2 Hazmat or spill.** Dangerous goods (UN number, ADR class, hazard diamonds) that are leaking,
  spilled or in damaged packaging; any spill of fuel, oil or chemical onto a public road; a spill
  on site that has not been contained. Intact, correctly packed dangerous goods are not `U2` by
  themselves.
- **U3 Vehicle stopped in a live lane.** Stationary in a running lane of a public road with traffic
  passing or able to: lane 1 of a smart motorway with no hard shoulder, a single-carriageway
  A-road, a slip road, roundabout or junction, under a bridge, or straddling a lane. Not live:
  hard shoulder, emergency area, lay-by, fully on the verge, services, depot or customer yard.
- **U4 Temperature-controlled cargo at risk within hours.** The load is still on our vehicle or at
  our depot and its refrigeration is not working (failed, alarming with temperature rising, out of
  fuel, doors open) or will stop within hours (unit fuel running out with no refuel possible), or
  its temperature is already out of range.
  - **Chilled** (about 0–8 °C): at risk as soon as refrigeration stops.
  - **Frozen** (about −18 °C or colder): at risk unless the report says the load will be back in
    working refrigeration (unit restored, transferred, or tipped into a cold store) within 1 hour.
  - **Not at risk:** unit fault cleared and temperature in range; empty trailer; ambient goods;
    an excursion found after the goods were handed over or rejected (the loss has happened, see
    `C3`).
- **U5 Time-critical consignment will miss its window.** The consignment is medical (medicines,
  vaccines, blood or lab supplies, medical devices for a hospital, clinic or pharmacy), or the
  report flags a contract deadline (timed slot with a penalty, a production line waiting, a ferry
  cut-off, "must be there by"). Urgent only if it will miss, or is likely to miss, that window.
  The customer's name alone ("Kestrel Pharma") does not make goods medical; the cargo must be
  described as such. An ordinary booked slot is not a flagged deadline.
- **U6 Theft in progress or breached seal.** Thieves present or the load being moved without
  authority now (tracker showing an unplanned move); a loaded vehicle or trailer whose location is
  unknown and whose driver cannot be contacted; or the load space breached: seal broken, missing
  or not matching the paperwork, curtain slashed, doors or locks forced. This applies whenever the
  breach is discovered. Goods short with the seal intact and matching is not `U6`.

**Borderline rulings.**

| Report | Ruling |
|---|---|
| Blow-out on the M1 hard shoulder, driver behind the barrier, "terrifying bang" | `routine` (`U0`): hard shoulder is not a live lane; tone does not count. |
| Gearbox fails on a single-carriageway A-road, traffic going round; driver calm | `urgent` (`U3`). |
| Reefer stops on a frozen load 2 hours from delivery, no fix in sight | `urgent` (`U4` frozen, more than 1 hour). |
| Reefer stops on a frozen load 30 minutes from the RDC, doors shut, tipping on arrival | `routine` (`U4` not met: working refrigeration within 1 hour). |
| Reefer fault code, driver restarts it, box at −19 °C | `routine` (fault cleared, in range). |
| Banksman grazed by a reversing trailer, "just a scratch, all fine" | `urgent` (`U1`: any injury). |
| Dangerous goods note missing for intact drums of class 8, vehicle still in the depot | `routine` (`U2` not met: nothing leaking or damaged). |
| Pharmacy supplies held up in traffic, will still make the 15:00 slot | `routine` (`U5` needs a missed window). |
| One pallet short at delivery, seal intact | `routine` (`U6` not met). |

## 5. Destination

### D0 Defaults

| Category | Destination |
|---|---|
| `vehicle_breakdown` | `fleet_support` |
| `delivery_delay` | `customer_desk` |
| `shipment_damage` | `claims` |
| `missing_shipment` | `security_investigations` |
| `documentation_issue` | `compliance` |
| `safety_incident` | `safety_desk` |

### Exceptions

Decide the Category first, using section 3. Then check only the exceptions listed for that
Category; at most one can apply. If none applies, use the default. Exceptions never change the
Category.

- **X1 Missing with an innocent explanation → `customer_desk`.** Category is `missing_shipment`;
  the report states an innocent explanation (delivered to the wrong address or unit, mis-picked
  or not loaded at the consignor or depot, cross-docked onto the wrong vehicle, moved within a
  yard); and there is no theft sign (no `U6` breach, no unplanned tracker move, driver reachable).
  "Short, don't know why" is not an explanation: default `security_investigations`.
- **X2 Commercial delivery paperwork → `customer_desk`.** Category is `documentation_issue`; the
  problem is only the consignee's delivery paperwork (POD missing, unsigned or disputed; delivery
  note wrong; e-POD not captured); and no regulatory document (customs or transit declaration,
  CMR on an international job, health certificate, dangerous goods note, tachograph record,
  driver card or permit) is involved. If one is, `compliance`.
- **X3 Delay caused by driver availability → `fleet_support`.** Category is `delivery_delay` and
  the stated cause is the driver: driving or duty-time limit reached, a required break or rest, or
  no driver available for the shift.
- **X4 Damage with a breach → `security_investigations`.** Category is `shipment_damage` and the
  load space was breached or tampered with (seal broken, missing or mismatched; curtain slashed;
  cartons opened). Such reports are also urgent by `U6`.
- **X5 Breakdown by criminal interference → `security_investigations`.** Category is
  `vehicle_breakdown` and the cause is deliberate: fuel siphoned, lines or cables cut, tyres
  slashed, vandalism.
- **X6 Delay from an authority hold → `compliance`.** Category is `delivery_delay` and the vehicle
  or load is held by an authority (Border Force, customs, DVSA, police) with the paperwork not
  stated to be at fault. A DVSA prohibition for a defect is `C1` (`fleet_support`); a hold for
  missing or wrong paperwork is `C5` (`compliance`).

`safety_incident` has no exceptions. A safety incident involving theft, hazmat or a breakdown
still goes to `safety_desk`.

## 6. When the report lacks information

- **I1 Label from what is stated.** Every report gets a full Label, however thin. A trigger that
  is not stated or clearly implied does not count: "broken down, waiting for recovery" with no
  location is `routine`; "had an accident at Doncaster, call me" with no mention of injury is
  `C6`, `routine`. Do not guess at facts that would change the Label.
- **I2 Possible triggers count.** "I think the drum's leaking", "might be in the lane" → treat the
  trigger as present.
- **I3 Contradictions.** If the report contradicts itself on a fact that decides Urgency and
  either reading meets a trigger → `urgent`. For Category and Destination, use the more specific
  statement: evidence such as a photo, count, reading, seal number or a named authority's
  decision beats a general assurance ("all fine", "paperwork's OK").
- **Category unclear.** Choose the most specific Category the stated facts support; "goods not
  arrived, nobody knows where" is `C4`; "running late, there about 4" is `C2`.

A Scenario tagged `incomplete` is one whose reports leave out something a team would want (where,
what cargo, why, whether anyone is hurt). It still has a full Label, given by `I1`. In Review,
missing information is a Review Trigger, not a reason to change the Label.
