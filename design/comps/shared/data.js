// Mock data for the design comps. Synthetic: report texts are paraphrases written for the comps
// from build-split Scenario facts only (S-012, S-016, S-030, S-038, S-045, S-063, S-064, S-077,
// S-082, S-085, S-090, S-091, S-100). Probabilities and metrics are placeholders, not results.

window.CAT = {
  vehicle_breakdown: "Vehicle breakdown",
  delivery_delay: "Delivery delay",
  shipment_damage: "Shipment damage",
  missing_shipment: "Missing shipment",
  documentation_issue: "Documentation issue",
  safety_incident: "Safety incident",
};
window.DEST = {
  fleet_support: "Fleet Support",
  customer_desk: "Customer Desk",
  claims: "Claims",
  security_investigations: "Security & Investigations",
  compliance: "Compliance",
  safety_desk: "Safety Desk",
};
window.ROLE = { driver: "Driver", depot: "Depot", customer: "Customer", subcontractor: "Subcontractor" };
window.CHANNEL = { app: "App", email: "Email", phone_transcript: "Phone transcript" };

// status: null (auto-routed) | awaiting | accepted | overridden | escalated
window.REPORTS = [
  {
    id: "R-0142", role: "driver", channel: "phone_transcript", received: "07:58",
    text: [
      "Air leak on the unit and the brakes have locked on.",
      "I'm stopped on the M25 anticlockwise just past junction 27, on the hard shoulder.",
      "Actually cars are having to swerve round the back of the trailer, it's sticking out into lane 1.",
      "I'm out of the cab and behind the barrier.",
      "Load is ambient beverages for Oakhurst, need recovery asap.",
    ],
    category: { top: "vehicle_breakdown", p: 0.94, alt: [["safety_incident", 0.04], ["delivery_delay", 0.02]] },
    urgency: { top: "urgent", p: 0.71, alt: [["routine", 0.29]] },
    destination: { top: "fleet_support", p: 0.95, alt: [["safety_desk", 0.04]] },
    evidence: { category: [0], urgency: [2], destination: [0, 4] },
    mode: "review", status: "awaiting",
    triggers: [
      { name: "Conflicting signals", detail: "Sentence 2 says hard shoulder; sentence 3 says lane 1.", rule: "I3" },
      { name: "Low probability", detail: "Urgency 0.71 is below the Policy v1 threshold of 0.85.", rule: "v1" },
    ],
    history: [
      ["07:58:12", "System", "Received by phone transcript from a driver"],
      ["07:58:12", "Approach C", "Rules not confident, sent to TypeSafe · 238 ms"],
      ["07:58:12", "Policy v1", "Sent to Review · 2 Review Triggers"],
    ],
  },
  {
    id: "R-0175", role: "driver", channel: "app", received: "07:20",
    text: [
      "At Tebay services on the M6, I've hit my 9 hours on the tacho so I have to stop here.",
      "No relief driver sorted yet.",
      "Got the Halcyon Medical reagents on for the hospital lab in Carlisle, due by 18:00.",
      "If nobody comes out we'll miss the 18:00.",
      "Just checking in, nothing else to report.",
    ],
    category: { top: "delivery_delay", p: 0.89, alt: [["vehicle_breakdown", 0.06], ["documentation_issue", 0.05]] },
    urgency: { top: "urgent", p: 0.9, alt: [["routine", 0.1]] },
    destination: { top: "customer_desk", p: 0.61, alt: [["fleet_support", 0.36], ["compliance", 0.03]] },
    evidence: { category: [0, 3], urgency: [2, 3], destination: [0, 1] },
    mode: "review", status: "overridden",
    override: { field: "Destination", from: "customer_desk", to: "fleet_support", reason: "Driver hours limit, relief driver needed (label guide X3)." },
    triggers: [{ name: "Low probability", detail: "Destination 0.61 is below the Policy v1 threshold of 0.80.", rule: "v1" }],
    history: [
      ["07:20:40", "System", "Received by app from a driver"],
      ["07:20:40", "Approach C", "Rules not confident, sent to TypeSafe · 244 ms"],
      ["07:20:40", "Policy v1", "Sent to Review · 1 Review Trigger"],
      ["07:26:03", "Reviewer", "Overrode Destination: Customer Desk → Fleet Support"],
    ],
  },
  {
    id: "R-0254", role: "driver", channel: "app", received: "07:05",
    text: ["running late sorry, be there about 4 instead of 12"],
    category: { top: "delivery_delay", p: 0.84, alt: [["vehicle_breakdown", 0.1]] },
    urgency: { top: "routine", p: 0.9, alt: [["urgent", 0.1]] },
    destination: { top: "customer_desk", p: 0.86, alt: [["fleet_support", 0.1]] },
    evidence: { category: [0], urgency: [0], destination: [0] },
    mode: "review", status: "awaiting",
    triggers: [{ name: "Missing details", detail: "No vehicle, customer or location stated.", rule: "I1" }],
    history: [
      ["07:05:31", "System", "Received by app from a driver"],
      ["07:05:31", "Approach C", "Rules confident · 3 ms"],
      ["07:05:31", "Policy v1", "Sent to Review · 1 Review Trigger"],
    ],
  },
  {
    id: "R-0301", role: "depot", channel: "email", received: "06:55",
    text: [
      "NV20 TCH is held at Dover inbound with the French cheese for Brackenridge Foods.",
      "Port health won't release it because the export health certificate is missing.",
      "Reefer fuel gauge shows about two hours left and they won't let us refuel in the inspection area.",
      "Box is at 4 °C for now.",
    ],
    category: { top: "documentation_issue", p: 0.66, alt: [["delivery_delay", 0.27], ["vehicle_breakdown", 0.05]] },
    urgency: { top: "urgent", p: 0.88, alt: [["routine", 0.12]] },
    destination: { top: "compliance", p: 0.79, alt: [["customer_desk", 0.16]] },
    evidence: { category: [1], urgency: [2], destination: [1] },
    mode: "review", status: "escalated",
    triggers: [
      { name: "Multiple issues", detail: "A missing certificate and a delay are both described.", rule: "P2" },
      { name: "Low probability", detail: "Category 0.66 is below the Policy v1 threshold of 0.75.", rule: "v1" },
    ],
    history: [
      ["06:55:02", "System", "Received by email from a depot"],
      ["06:55:02", "Approach C", "Rules not confident, sent to TypeSafe · 251 ms"],
      ["06:55:02", "Policy v1", "Sent to Review · 2 Review Triggers"],
      ["07:01:44", "Reviewer", "Escalated: reefer fuel under two hours"],
    ],
  },
  {
    id: "R-0033", role: "subcontractor", channel: "email", received: "07:50",
    text: [
      "Ashby Haulage collected 12 pallets of whisky for Northvale yesterday at 15:00.",
      "It hasn't arrived at the bonded warehouse in Daventry this morning.",
      "We can't get hold of our driver and the tractor tracker has been off since 19:00 yesterday.",
      "Probably nothing, just flagging it.",
    ],
    category: { top: "missing_shipment", p: 0.96, alt: [["delivery_delay", 0.03]] },
    urgency: { top: "urgent", p: 0.95, alt: [["routine", 0.05]] },
    destination: { top: "security_investigations", p: 0.97, alt: [["customer_desk", 0.02]] },
    evidence: { category: [1], urgency: [2], destination: [2] },
    mode: "auto", status: null, triggers: [],
    history: [["07:50:19", "System", "Received"], ["07:50:19", "Approach C", "Rules confident · 4 ms"], ["07:50:19", "Policy v1", "Auto-routed to Security & Investigations"]],
  },
  {
    id: "R-0217", role: "driver", channel: "app", received: "07:41",
    text: [
      "Reversing onto bay 3 at Greystone Builders Merchants in Wolverhampton.",
      "Trailer clipped their banksman on the way back.",
      "He's got a graze and some bruising on his forearm, first aid done on site.",
      "All fine really, just a scratch, carrying on with the tip.",
    ],
    category: { top: "safety_incident", p: 0.97, alt: [["shipment_damage", 0.02]] },
    urgency: { top: "urgent", p: 0.93, alt: [["routine", 0.07]] },
    destination: { top: "safety_desk", p: 0.98, alt: [["claims", 0.01]] },
    evidence: { category: [1], urgency: [2], destination: [1] },
    mode: "auto", status: null, triggers: [],
    history: [["07:41:55", "System", "Received by app from a driver"], ["07:41:55", "Approach C", "Rules confident · 3 ms"], ["07:41:55", "Policy v1", "Auto-routed to Safety Desk"]],
  },
  {
    id: "R-0088", role: "driver", channel: "phone_transcript", received: "07:33",
    text: [
      "Trailer's caught fire at the brakes, I'm in the HGV park at Hilton Park services on the M6.",
      "Fire brigade are on their way.",
      "I've got everyone back away from the trailer.",
      "Load is paper products for Marlow & Finch.",
    ],
    category: { top: "safety_incident", p: 0.99, alt: [["vehicle_breakdown", 0.01]] },
    urgency: { top: "urgent", p: 0.99, alt: [["routine", 0.01]] },
    destination: { top: "safety_desk", p: 0.99, alt: [] },
    evidence: { category: [0], urgency: [2], destination: [0] },
    mode: "auto", status: null, triggers: [],
    history: [["07:33:08", "System", "Received"], ["07:33:08", "Approach C", "Rules confident · 3 ms"], ["07:33:08", "Policy v1", "Auto-routed to Safety Desk"]],
  },
  {
    id: "R-0271", role: "driver", channel: "phone_transcript", received: "07:12",
    text: [
      "Rear tyre's gone on the 7.5 tonner on the A30 near Bodmin, I'm in a lay-by.",
      "Spare's missing from the cradle.",
      "Dialysis fluids on for the county hospital renal unit, slot is 11:00.",
      "Tyre service say 90 minutes so we won't make 11.",
    ],
    category: { top: "vehicle_breakdown", p: 0.9, alt: [["delivery_delay", 0.09]] },
    urgency: { top: "urgent", p: 0.92, alt: [["routine", 0.08]] },
    destination: { top: "fleet_support", p: 0.93, alt: [["customer_desk", 0.06]] },
    evidence: { category: [0], urgency: [2, 3], destination: [0] },
    mode: "auto", status: null, triggers: [],
    history: [["07:12:47", "System", "Received"], ["07:12:47", "Approach C", "Rules not confident, sent to TypeSafe · 233 ms"], ["07:12:47", "Policy v1", "Auto-routed to Fleet Support"]],
  },
  {
    id: "R-0063", role: "customer", channel: "email", received: "06:48",
    text: [
      "Our pallet of office chairs for the Reading office never arrived.",
      "Turns out the label had our old address on it and your driver dropped it there.",
      "The new tenant at the old unit has the pallet and is holding it for us.",
    ],
    category: { top: "missing_shipment", p: 0.81, alt: [["documentation_issue", 0.12], ["delivery_delay", 0.07]] },
    urgency: { top: "routine", p: 0.94, alt: [["urgent", 0.06]] },
    destination: { top: "customer_desk", p: 0.83, alt: [["security_investigations", 0.15]] },
    evidence: { category: [0], urgency: [2], destination: [1, 2] },
    mode: "auto", status: null, triggers: [],
    history: [["06:48:30", "System", "Received"], ["06:48:30", "Approach C", "Rules not confident, sent to TypeSafe · 229 ms"], ["06:48:30", "Policy v1", "Auto-routed to Customer Desk"]],
  },
  {
    id: "R-0346", role: "driver", channel: "app", received: "06:40",
    text: [
      "At Fenwick Garden Supplies Bury St Edmunds for the 08:00 slot, gates locked and nobody answering the site phone.",
      "Waited 40 minutes, moving on to the next drop.",
      "Garden furniture still on board and fine.",
    ],
    category: { top: "delivery_delay", p: 0.95, alt: [["missing_shipment", 0.02]] },
    urgency: { top: "routine", p: 0.96, alt: [["urgent", 0.04]] },
    destination: { top: "customer_desk", p: 0.96, alt: [] },
    evidence: { category: [0], urgency: [2], destination: [0] },
    mode: "auto", status: null, triggers: [],
    history: [["06:40:11", "System", "Received"], ["06:40:11", "Approach C", "Rules confident · 2 ms"], ["06:40:11", "Policy v1", "Auto-routed to Customer Desk"]],
  },
  {
    id: "R-0120", role: "driver", channel: "app", received: "06:30",
    text: [
      "Car cut right in front of me on the M1 southbound near Luton, had to slam on.",
      "Honestly nearly killed.",
      "No contact in the end, nobody hurt and the load's fine.",
      "Carried on.",
    ],
    category: { top: "safety_incident", p: 0.92, alt: [["delivery_delay", 0.04]] },
    urgency: { top: "routine", p: 0.86, alt: [["urgent", 0.14]] },
    destination: { top: "safety_desk", p: 0.97, alt: [] },
    evidence: { category: [0], urgency: [2], destination: [0] },
    mode: "auto", status: null, triggers: [],
    history: [["06:30:52", "System", "Received"], ["06:30:52", "Approach C", "Rules not confident, sent to TypeSafe · 241 ms"], ["06:30:52", "Policy v1", "Auto-routed to Safety Desk"]],
  },
  {
    id: "R-0199", role: "depot", channel: "email", received: "06:21",
    text: [
      "NV22 SUV arrived at Tollbridge RDC Lutterworth with the Sable Electronics tablets.",
      "Seal number on the doors doesn't match the CMR or the manifest.",
      "Carton count is right but several cartons have been opened and the devices inside are smashed.",
      "RDC has quarantined the load.",
    ],
    category: { top: "shipment_damage", p: 0.86, alt: [["missing_shipment", 0.11]] },
    urgency: { top: "urgent", p: 0.94, alt: [["routine", 0.06]] },
    destination: { top: "security_investigations", p: 0.88, alt: [["claims", 0.11]] },
    evidence: { category: [2], urgency: [1], destination: [1] },
    mode: "auto", status: null, triggers: [],
    history: [["06:21:05", "System", "Received"], ["06:21:05", "Approach C", "Rules confident · 4 ms"], ["06:21:05", "Policy v1", "Auto-routed to Security & Investigations"]],
  },
  {
    id: "R-0012", role: "driver", channel: "app", received: "06:14",
    text: [
      "DVSA pulled me in on the M6 near Carlisle, my Driver CPC card has expired.",
      "Given advice and let go, delivery still on time.",
    ],
    category: { top: "documentation_issue", p: 0.93, alt: [["delivery_delay", 0.04]] },
    urgency: { top: "routine", p: 0.97, alt: [["urgent", 0.03]] },
    destination: { top: "compliance", p: 0.94, alt: [["customer_desk", 0.04]] },
    evidence: { category: [0], urgency: [1], destination: [0] },
    mode: "auto", status: null, triggers: [],
    history: [["06:14:26", "System", "Received"], ["06:14:26", "Approach C", "Rules confident · 3 ms"], ["06:14:26", "Policy v1", "Auto-routed to Compliance"]],
  },
];

// Queue order: awaiting Review first (urgent first), then the rest by time received.
window.QUEUE = (() => {
  const r = window.REPORTS.slice();
  const rank = (x) => (x.status === "awaiting" ? (x.urgency.top === "urgent" ? 0 : 1) : 2);
  return r.sort((a, b) => rank(a) - rank(b) || b.received.localeCompare(a.received));
})();

window.firstLine = (r) => {
  const s = r.text[0];
  return s.length > 92 ? s.slice(0, 90).trimEnd() + "…" : s;
};
window.p2 = (p) => p.toFixed(2);
window.STATUS = { awaiting: "Awaiting review", accepted: "Accepted", overridden: "Overridden", escalated: "Escalated" };

// Placeholder metrics for the Results sketch. Not results: the build reads results/*.json.
window.RESULTS = {
  approaches: [
    { key: "A", name: "Rules baseline", recall: 0.95, missed: 2, review: 0.31, destAcc: 0.86, p95: 6, cost: 0 },
    { key: "B", name: "TypeSafe", recall: 0.98, missed: 1, review: 0.22, destAcc: 0.9, p95: 410, cost: 0.62 },
    { key: "C", name: "Cascade", recall: 0.98, missed: 1, review: 0.19, destAcc: 0.91, p95: 280, cost: 0.34 },
  ],
};
