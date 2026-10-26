"""Assemble authored Incident Report passages; shuffle and number deterministically.

Each Scenario has two independently phrased versions of three passages. Four reports
mix those versions and use different ordering and channel framing. No labels enter
the report text. Run from the repository root with Python's standard library.
"""

import json
import random
from pathlib import Path

MODEL = "gpt-6.1-sol"
PASSAGES = {}


def add(number, first, second):
    versions = (first.split("|"), second.split("|"))
    assert all(len(v) == 3 for v in versions), number
    PASSAGES[f"S-{number:03d}"] = versions


add(1,
    "NV22 HPL has tipped at Brackenridge RDC Doncaster, three pallets short.|Driver says the seal was intact when he opened the artic. Goods-in say the number on the doors doesn't match the manifest.|Nobody has an explanation for those missing pallets.",
    "Three pallets haven't turned up on the NV22 HPL delivery to Brackenridge RDC Doncaster.|The driver insists he opened an intact seal, but the RDC have checked the door seal number against the manifest and it is different.|We can't account for the shortage.")
add(2,
    "NV17 AJD collected mixed pallets at Pennine Paints in Huddersfield.|Their loaders stacked tile adhesive bags over boxed light fittings. The driver didn't see them loading.|At Greystone Builders Merchants in Oxford the cartons underneath were crushed; goods-in put that on the POD.",
    "This is about the mixed load on artic NV17 AJD from Pennine Paints' Huddersfield warehouse.|Loading was done without the driver watching: pallets of bagged tile adhesive were double-stacked onto light-fitting boxes.|Greystone Builders Merchants' Oxford branch found the lower cartons crushed at delivery and recorded it on the POD.")
add(3,
    "NV16 KCR has ambient tins for Brackenridge Foods and is going to miss the slot.|An engine light came on near Cambridge, but cleared after a stop at services; no fault was found.|Since then the A14 westbound has shut for somebody else's collision. Three hours stuck there, no special deadline on this job.",
    "Brackenridge Foods' tins are on artic NV16 KCR, ambient load, ordinary booking with no deadline flagged.|The earlier engine warning near Cambridge cleared at services and checks found no fault.|The problem now is the westbound A14 closure after a collision we weren't involved in. We've lost three hours and won't make the booked time.")
add(4,
    "Redgate Logistics have delivered our Northvale freight to Greystone Builders Merchants in Norwich.|The Redgate driver went without leaving a delivery note or obtaining a POD signature.|Greystone confirm they've got the goods and are happy with them; it's the delivery documents we need to sort.",
    "Following up the Northvale delivery handled by Redgate Logistics at Greystone Builders Merchants, Norwich.|Nothing wrong with the goods according to Greystone, they've accepted them.|However their driver left no delivery note and didn't get the POD signed. Can someone sort the missing copies and signature please.")
add(5,
    "NV20 EAG was in a lay-by on the A1 near Grantham overnight.|At 06:00 the driver found the offside curtain slashed. All pallets are there but Pennine Paints' emulsion tins are pierced and dented.|This emulsion isn't dangerous goods. Nothing has been taken, just the damaged tins and curtain to report.",
    "Morning check on curtainsider NV20 EAG, parked overnight off the A1 near Grantham in a lay-by.|At six this morning the offside curtain was found cut open, with pierced and dented emulsion paint tins on the Pennine Paints pallets.|Count is correct, nothing missing. The emulsion is non-dangerous goods.")
add(6,
    "Ashby Haulage's AH15 KLM has a Northvale trailer on, ambient household goods for Tollbridge Retail tomorrow.|The clutch failed and the driver limped into Corley services on the M6, now parked in the HGV park.|Ashby are asking if Northvale can send another tractor to pick up the trailer.",
    "Can Northvale provide a tractor for the trailer on Ashby Haulage unit AH15 KLM please?|Clutch has gone; it made Corley services, M6, and is parked in the lorry park.|It's carrying ambient household stock for Tollbridge Retail, delivery tomorrow. Ashby have asked about collecting the trailer with a replacement unit.")
add(7,
    "Paperwork's wrong on the Rotterdam job, can somebody ring the driver please.|That's the report we've got about it and the request is for a call back.|Please pick this up and talk it through rather than leave it sitting here.",
    "Can someone call back about the Rotterdam job please, driver says the paperwork isn't right.|I'm passing on the request in those words so it gets picked up.|Would appreciate somebody speaking to the driver about it and coming back to us.")
add(8,
    "Redgate Logistics delivered ten cartons for Fenwick Garden Supplies on the Swindon industrial estate.|Fenwick say they've received nothing, but Redgate's POD photo shows the cartons at the neighbouring unit.|That unit has confirmed it's got them. We need to get these over to the right unit please.",
    "Fenwick Garden Supplies are chasing ten cartons at their industrial estate in Swindon, saying nothing arrived.|The delivery was by Redgate Logistics; their POD photograph is of the unit next door.|The neighbours have confirmed the cartons are with them, so this looks to be the wrong unit on that delivery.")
add(9,
    "Scania R450 NV19 KTX has pulled into a lay-by on the A38 near Burton after debris split its own diesel tank.|Diesel is pouring across the lay-by onto the carriageway. Engine switched off, nobody hurt and no collision.|Load is ambient flat-pack furniture for Tollbridge Retail.",
    "NV19 KTX, the Scania R450 carrying Tollbridge Retail flat-pack furniture at ambient, is stopped in the A38 lay-by near Burton.|Debris hit and split the vehicle's diesel tank, with fuel still running out over the lay-by and onto the road.|No collision or injuries; the driver has shut the engine down.")
add(10,
    "NV23 MLE is on the M5 hard shoulder near J14.|Driver says he's fine and only needs a few minutes, but also says his chest feels tight and his left arm has gone numb.|The artic has an ambient load with no deadline. That's what he's telling us.",
    "The artic on the hard shoulder near M5 J14 is NV23 MLE, ambient load, no deadline.|He says 'I'm fine, just give me a few minutes'. In the same account he's describing chest tightness and numbness down his left arm.|Please pick up the driver's account as given.")
add(11,
    "DVSA have stopped NV16 DKS at their A1 check site near Grantham.|Inspector found a defective brake chamber and issued an immediate prohibition. It can't leave the check site until repaired; paperwork and tachograph were both in order.|The 11:00 ambient stock delivery for Marlow & Finch will be late.",
    "Marlow & Finch's ambient delivery booked for eleven is held up on artic NV16 DKS.|At the DVSA roadside site on the A1 near Grantham, an inspector prohibited it immediately for a faulty brake chamber.|The vehicle is immobilised there pending repair. They checked the driver's paperwork and tacho too, both fine.")
add(12,
    "Just flagging this, probably nothing: Ashby Haulage collected twelve pallets of whisky for Northvale at 15:00 yesterday.|They haven't reached the Daventry bonded warehouse this morning. Ashby can't get hold of their driver and the tractor tracker has been off since 19:00 yesterday.|We don't know where the loaded vehicle is.",
    "A quiet update on yesterday's Ashby Haulage collection for Northvale, twelve whisky pallets picked up at three in the afternoon.|Nothing has arrived at the bonded warehouse in Daventry this morning. Their tractor stopped tracking at seven last night; Ashby can't contact the driver.|Probably nothing, but the vehicle's whereabouts aren't known.")
add(13,
    "Empty curtainsider NVT 3302 is on the perimeter at Northvale Thurrock depot.|This morning both red and yellow air lines were found cut and two tyres slashed. There's a gap in the fence nearby.|Nothing taken, trailer was empty, but we can't move it until it's repaired.",
    "NVT 3302 cannot be moved pending repairs, parked along the Northvale Thurrock depot perimeter.|Found this morning: cut red and yellow air lines, plus two slashed tyres. The nearby perimeter fence has a gap.|It's an empty curtainside trailer and nothing has been taken from it.")
add(14,
    "We're two pallets short against the delivery note on the Pennine Paints customer delivery.|Pennine Paints' warehouse have found both pallets there: they were mis-picked and never loaded.|Seal was intact. Can we arrange to get the pallets from the warehouse to the customer please.",
    "Pennine Paints have located the two pallets their customer is short, still at their warehouse.|It was a mis-pick; those pallets never went on the vehicle. The delivery note listed them so the delivery came up two short.|The seal was intact on arrival.")
add(15,
    "At 02:30 the tracker for loaded trailer NVT 5120 showed it leaving Northvale Thurrock depot towards the A13.|No driver is booked on it and there's no scheduled move. Night security can't see it on the yard cameras.|The trailer has Sable Electronics laptops on board.",
    "NVT 5120, loaded with Sable Electronics laptops, is showing a move away from Northvale Thurrock yard towards the A13.|It's half two in the morning, no driver or trailer movement scheduled.|Security on nights have checked the yard cameras and cannot see the trailer there.")
add(16,
    "DVSA checked the driver's Driver CPC card on the M6 near Carlisle and found it expired.|They gave advice and let the vehicle carry on, with Northvale required to evidence renewal.|Ambient load, delivery still on time. Please follow up the card renewal evidence for this check.",
    "The vehicle was allowed to continue after the DVSA check near Carlisle on the M6.|Driver's CPC card was out of date; advice given and Northvale have to provide evidence of renewal.|It is carrying ambient goods and remains on time for delivery. Can somebody pick up the card point please.")
add(17,
    "NV21 HRD, Northvale Freight DAF XF artic with curtainsider, lost drive in lane 1 on the M6 NB between J10 and J8.|It's 05:40, dark, no hard shoulder on this smart motorway stretch. Hazards on, driver behind the barrier and National Highways called.|26 ambient grocery pallets for Brackenridge Foods RDC Doncaster; recovery needed.",
    "Recovery requested for Northvale Freight artic NV21 HRD, DAF XF with a curtainside trailer, 26 pallets of ambient groceries for Brackenridge Foods RDC Doncaster.|Lost drive and stopped in the running lane, lane one, M6 northbound between J10 and J8, no hard shoulder.|At 5.40am it's still dark. Hazards on; driver behind barrier, National Highways already called.")
add(18,
    "NV18 SRA wouldn't start at 06:10 after the night at the truck stop off the A5 near Hinckley.|Tank empty, filler cap forced, diesel smell around it; driver thinks it was siphoned overnight.|The trailer seal is intact and matches the paperwork, ambient tinned food untouched.",
    "Morning start on artic NV18 SRA failed at ten past six, truck stop near Hinckley off the A5.|There's no fuel, the filler cap has been forced and it smells of diesel round the tank. Driver believes somebody siphoned it during the night.|Tinned food load untouched, ambient, and trailer seal intact with the correct number.")
add(19,
    "NV66 JHN delivered kitchen units to the Marlow & Finch site in Reading.|The account says the load was checked and fine on delivery, but also says the customer sent tailgate photos showing two crushed carcass boxes.|Nothing missing; this was the curtainsider, seal not relevant here.",
    "On the Reading kitchen-unit delivery for Marlow & Finch, rigid NV66 JHN, the driver says it was all checked and fine when delivered.|That same account includes customer photographs taken at the tailgate of two crushed carcass boxes.|It's a curtainsider so no relevant seal, and the delivery has nothing missing.")
add(20,
    "HUGE problem with NV22 PTD, customer going mad! Ambient groceries for Tollbridge RDC Lutterworth booked ten o'clock.|Heavy traffic on the M62 J22 to J24 means ETA 12:00. We're missing the slot!|RDC will rebook it, no special deadline flagged, but please get back to us about this.",
    "This is a huge problem, the customer is going mad over the Tollbridge RDC Lutterworth booking!|Artic NV22 PTD with ambient groceries is caught in heavy M62 traffic between J22 and J24, now due noon instead of 10:00.|No flagged deadline and RDC are rebooking, but we need this picked up please.")
add(21,
    "Six cages of Marlow & Finch stationery are missing from the Bristol trailer.|Northvale Daventry hub have traced the mistake: they cross-docked them onto the Warrington trailer.|All six are at Northvale Warrington depot untouched. Can someone arrange to get them onto the correct run please.",
    "Daventry hub have found where the six missing Marlow & Finch stationery cages went.|They should have been on the Bristol trailer but were cross-docked to the Warrington one by mistake.|Northvale Warrington depot have the cages, untouched. That's the explanation for the Bristol shortage.")
add(22,
    "01:00 at Holyhead and check-in have refused the Dublin sailing.|The ENS safety and security declaration hasn't been lodged for the Tollbridge Retail ambient stock load.|Driver is parked up waiting for the broker. Next sailing is four hours away; please get the declaration sorted.",
    "Driver is waiting parked up at Holyhead for the broker after Dublin sailing check-in was refused at one this morning.|Tollbridge Retail ambient stock on board, but the load's safety and security declaration, ENS, hasn't been submitted.|There's another sailing in four hours.")
add(23,
    "The pallet for Fenwick isn't on the van, no idea where it's gone.|Can somebody pick this up please and come back to the driver about it.|I'm passing on the report as it stands; we need someone to look into that missing pallet.",
    "Can someone get back to the driver please, Fenwick's pallet is not on the van.|There's no idea where it's gone, that's the report we've been given.|Please look into this and come back to us so we can follow it up.")
add(24,
    "We're unloading at Northvale Thurrock depot and an IBC valve has split.|It's UN1824 sodium hydroxide solution, ADR class 8, leaking onto the trailer floor and out into the yard.|Area cordoned off and spill kit in use, but it's still leaking. Please pick this up.",
    "Leak during unloading at Northvale Thurrock depot: an IBC of sodium hydroxide solution UN1824, class 8.|The split valve is letting it run across the trailer floor and onto the yard.|We've cordoned the area and used a spill kit; that hasn't stopped the leak.")
add(25,
    "Some of today's delivery arrived damaged, please advise what we should do about it.|Could somebody get back to us about this please.|I'm raising it here so it gets picked up and we can speak to someone about the delivery.",
    "Please can you advise us about damage to some of the delivery received today.|We'd appreciate somebody responding about it and telling us how to follow this up.|This is to report the damage and ask for someone to get back to us.")
add(26,
    "Greystone Builders Merchants Leicester say the delivery note has the wrong product codes.|The goods themselves match their order; it's only the note that's wrong.|They won't pay the invoice until they get a corrected delivery note. Can somebody send the corrected version please.",
    "Please correct the delivery note for Greystone Builders Merchants in Leicester.|They have checked the actual goods against their order and those are right, but the product codes printed on the note aren't.|They are holding payment of the invoice until a corrected note comes through.")
add(27,
    "The tachograph download for a Northvale Daventry driver shows yesterday's daily rest was too short, an hours infringement.|His Tollbridge RDC Lutterworth delivery yesterday was also ninety minutes late.|He's on his rest day now. Please pick up what's shown on the download.",
    "Yesterday's late delivery to Tollbridge RDC Lutterworth was the Northvale Daventry driver's, ninety minutes behind.|His tacho download also records a drivers' hours infringement yesterday: insufficient daily rest.|The driver is currently on a rest day. Sending the record issue over for somebody to follow up.")
add(28,
    "Delivery made to Fenwick Garden Supplies in Chelmsford, but there's no POD signature.|Goods-in supervisor wouldn't sign until her manager checked the load, and the manager wasn't available.|The driver left the goods there and came away unsigned. Can someone follow up the signature please.",
    "Fenwick Garden Supplies' Chelmsford store have the goods, but the driver has no signed POD.|Their goods-in supervisor wanted her manager to check the load before she signed; manager unavailable.|Driver left the delivery there. We need someone to follow this up with the store.")
add(29,
    "Monthly tachograph download for a driver at Northvale Warrington depot has a gap in the records.|Please can someone pick this up and go through it.|I'm forwarding the report about the gap so somebody can get back to us and follow it through.",
    "There's a gap showing in the monthly tacho records for a Northvale Warrington depot driver.|Could somebody look at the download and come back to us please.|This is the record issue we're raising, and we'd appreciate someone picking it up.")
add(30,
    "Running late, it'll be about 16:00 instead of 12:00.|Can somebody pick this up and come back to the driver please.|Just passing the arrival time on here so somebody can follow up the change and get back to us.",
    "Please pass on that arrival is now about four in the afternoon rather than noon.|The driver is running late and wants this picked up.|Can someone get back to us about the changed arrival time please, that's the update to pass on.")
add(31,
    "NV23 BDE has come into Holyhead from Dublin with chilled cheese for Brackenridge Foods.|Customs picked it for a documentary check; documents are in order, but release is expected in two hours.|Reefer working normally, box 3 °C. The Brackenridge RDC slot will be missed and rebooked.",
    "Brackenridge RDC will need to rebook the cheese delivery on chilled trailer NV23 BDE, inbound Holyhead from Dublin.|Customs are holding it for their document check although the documents have been found correct; two hours to release.|Unit is running as normal and the box reads three degrees.")
add(32,
    "NV71 TLF was delivering ceramic tiles to Greystone Builders Merchants, Stoke-on-Trent.|Tail-lift dropped suddenly while lowering, tipping the pallet and cracking about a third of the tiles.|Nobody near the lift and nobody hurt. The tail-lift now needs checking, but the tiles are already broken.",
    "About a third of the ceramic tiles on the pallet for Greystone Builders Merchants in Stoke-on-Trent have cracked.|Rigid NV71 TLF's tail-lift suddenly dropped mid-lower and tipped the pallet.|No one was near it, no injuries. Please arrange for the lift to be checked as well.")
add(33,
    "NV18 LMD spent the night at the secure truck park on the A1 near Markham Moor.|At next-day delivery to Wrenfield Dairies' ambient warehouse, the count was one pallet short.|Seal intact and its number matched. There's no explanation for the missing pallet at the moment.",
    "One pallet missing on delivery at Wrenfield Dairies' ambient warehouse, from artic NV18 LMD.|The artic had stopped overnight in the secure truck park near Markham Moor on the A1.|The seal was still intact and matching when checked. We can't explain the shortage.")
add(34,
    "Night shunter's report, NVT 4471 in Northvale Warrington yard, chilled trailer with Thermo King unit.|At 22:15 the reefer alarmed, shut down and won't restart. Box was 3 °C at 21:30, now 7 °C and climbing.|Wrenfield Dairies yoghurts and cream on board for 05:00 departure. No engineer here.",
    "NVT 4471 has Wrenfield Dairies chilled dairy, yoghurt and cream, due out of Northvale Warrington depot at five in the morning.|The night shunter says its Thermo King reefer stopped after an alarm at quarter past ten tonight and won't start again.|Box up from 3 °C at 21:30 to 7 °C now, still rising, no engineer on site.")
add(35,
    "NV19 ADR is still at Northvale Thurrock depot with drums of UN1824 sodium hydroxide solution, ADR class 8.|The dangerous goods note is missing from the paperwork pack.|Drums are intact and correctly labelled, nothing leaking, and the rigid hasn't left the depot. Please sort the missing note.",
    "Before NV19 ADR leaves Northvale Thurrock depot we need its dangerous goods note, which isn't in the pack.|The rigid is loaded with class 8 UN1824 sodium hydroxide solution drums.|All drums intact, labels correct, no leaks. Vehicle hasn't departed; this is about the absent document.")
add(36,
    "NV21 LJC has just-in-time parts for Corvid Automotive's assembly plant, line-side slot 14:00.|The job sheet flags a line stop penalty. A50 eastbound is closed near Uttoxeter for somebody else's fuel spill; diversion via A515.|ETA now 15:30, so it won't make that contract slot.",
    "Corvid Automotive's assembly parts on artic NV21 LJC won't reach the plant until half three.|It is a just-in-time job with a two o'clock line-side contract slot and 'line stop penalty' on the sheet.|Our diversion is via A515 because the eastbound A50 near Uttoxeter is closed after a fuel spill, not ours.")
add(37,
    "Marlow & Finch homeware delivery to the Cardiff store is three pallets short against the delivery note.|There are also two crushed pallets on the delivery.|The seal was intact, but we haven't got an explanation for the shortage yet. Please pick up both points with this delivery.",
    "Cardiff store have counted the Marlow & Finch homeware against the note and three pallets are missing.|Two of the pallets that did arrive are crushed as well.|Seal intact on arrival. We don't yet know why those other three pallets haven't arrived with the delivery.")
add(38,
    "Nearly killed us! NV20 PNK was on the M1 southbound near Luton when a car cut right in.|Driver braked hard, no contact and nobody hurt. Load fine and he carried on.|Still shocked at how close that was, please get this picked up.",
    "What a shock, that car nearly killed the driver on the M1 SB near Luton!|Artic NV20 PNK had to brake hard when it cut sharply in front, but there was no contact.|Nobody hurt, load fine, and the driver continued. He is still shaken by it.")
add(39,
    "Two-person home delivery in Swindon for Tollbridge Retail, a 65-inch television.|The outer box looked fine but when it was opened in front of the crew the screen was cracked.|Customer refused the television and the crew took it back. Please follow up the damaged set.",
    "Tollbridge Retail's customer in Swindon has refused the 65-inch TV on the two-person home delivery.|Screen was cracked when unboxed with the crew watching, despite the outside of the carton looking fine.|The crew have taken the set back with them, so it hasn't been left at the house.")
add(40,
    "Ashby Haulage delivered Northvale's laminate flooring to the Greystone branch in Derby.|Customer reports forklift-tine holes through the packs on four pallets.|Ashby's driver says it happened during loading at their cross-dock. Can somebody pick this up with the delivery and the loading account please.",
    "Four flooring pallets have holes through the packs from forklift tines, according to Greystone's Derby branch.|It was Northvale freight delivered by Ashby Haulage, laminate flooring.|The Ashby driver says the packs were damaged when loading at their cross-dock. Please follow this up.")
add(41,
    "NV68 BRW delivered beer and glass bottles to an Oakhurst Brewery customer pub in Leeds.|One pallet arrived with broken bottles and torn shrink-wrap.|The consignee wrote 'one pallet damaged' on the POD when signing. Please pick up that reservation and the broken goods on this delivery.",
    "The signed POD for rigid NV68 BRW has a reservation, 'one pallet damaged'.|This was the beer and glass-bottle delivery to Oakhurst Brewery's customer pub in Leeds.|On arrival a pallet had torn wrapping and broken bottles. Can someone follow up that pallet please.")
add(42,
    "Delivery at Tollbridge RDC Lutterworth has come up one pallet short against the manifest.|Please can somebody pick up the shortage and get back to us.|That's the delivery count being reported, and we need someone to follow it through with the people involved.",
    "Tollbridge RDC Lutterworth have counted the delivery and there's one pallet missing against the manifest.|Can somebody look into the missing pallet please.|Passing this count on so it gets picked up, and would appreciate a response about how to follow it through.")
add(43,
    "NV21 TRN is inbound at Dover with Marlow & Finch kitchenware.|Border Force are holding the artic because the commodity code on the T1 transit document is wrong.|The Marlow & Finch warehouse delivery will be late, no special deadline flagged. Please get the transit document looked at.",
    "Marlow & Finch's kitchenware on artic NV21 TRN is being held at Dover by Border Force.|They've identified an incorrect commodity code on the T1 transit paperwork.|It's making the warehouse delivery late. There isn't a flagged deadline on the job, but the document needs sorting to get it moving.")
add(44,
    "Had a bump this morning, all ok.|Can someone get back to the driver please, just passing on what's been reported.|Please pick this up and speak to the driver about it so somebody can follow it through from here.",
    "Driver's report is 'had a bump this morning, all ok'.|Would somebody call back about it please, that's the account being passed on.|I'm putting it here for someone to pick up and come back to us about the bump.")
add(45,
    "NV20 TCH inbound Dover with chilled French cheese for Brackenridge Foods is held for a missing export health certificate.|Reefer fuel shows about two hours left and refuelling isn't allowed in the inspection area.|Box still at 4 °C for now, but the fuel won't keep it going beyond that.",
    "The inspection area at Dover won't allow refuelling of chilled trailer NV20 TCH's reefer.|It's inbound with Brackenridge Foods French cheese, held because the export health certificate isn't there.|Box reading four degrees currently; the reefer tank only has around two hours of fuel remaining.")
add(46,
    "NVT 2218 is at Northvale Avonmouth depot after the heavy rain.|The roof sheet is torn and water has got into Tollbridge Retail's flat-pack furniture cartons and soaked them.|Please pick up the wet cartons and the torn sheet on this trailer.",
    "Tollbridge Retail flat-pack furniture cartons in trailer NVT 2218 have been soaked by rainwater.|Trailer is at Northvale Avonmouth depot following heavy rain, with a tear in the roof sheet where the water got in.|Can somebody follow up this load please.")
add(47,
    "NV20 KHL got to Brackenridge RDC Doncaster at 06:00 for the 06:30 slot.|Goods-in have a backlog and told the driver there's about a four-hour wait.|Ambient cereals on the artic. Waiting here will make him late for his afternoon collection as well.",
    "Brackenridge RDC Doncaster are asking NV20 KHL to wait roughly four hours because of their goods-in backlog.|It arrived at six this morning for half six, with ambient cereals.|Driver is now going to run late for the afternoon collection. Please pass on the knock-on to that collection.")
add(48,
    "At 09:30 during trans-shipping at Northvale Daventry depot, a forklift crushed two Halcyon Medical insulin cartons.|The insulin pens inside are broken; nobody hurt.|They were for a hospital pharmacy by 16:00 today and replacement stock can't reach it by then. Please pick up the failed delivery window as well.",
    "We can't get replacement insulin to the hospital pharmacy before today's four o'clock window.|Two Halcyon Medical cartons were crushed by a forklift while being trans-shipped at Northvale Daventry at half nine; the pens inside are broken.|No one was hurt. That's the damage behind the missed window.")
add(49,
    "NV19 RRT has export furniture for a Dublin customer, booked on Holyhead's 20:15 sailing.|Job flagged 'ferry cut-off, next sailing breaches contract'. Check-in closes 19:30 but sat-nav now says 19:55.|Caught in A55 roadworks near Conwy. Customs paperwork all correct; it's the traffic holding us up.",
    "The furniture export on artic NV19 RRT won't reach Holyhead check-in until 7.55pm, according to the sat-nav.|Roadworks near Conwy on the A55 have held it up. The 20:15 Dublin sailing closes check-in at 19:30.|Paperwork for customs is in order. Job specifically flags the ferry cut-off and a contract breach if we take the next sailing.")
add(50,
    "NV68 DYE clipped a bollard reversing at Tollbridge RDC Lutterworth.|The bollard is bent and the rigid has a small scrape on the rear corner.|Nobody hurt and goods fine. Please record what happened on the reverse and come back to us if you need to speak to the driver.",
    "A reversing manoeuvre at Tollbridge RDC Lutterworth ended with rigid NV68 DYE catching a bollard.|Only a minor scrape on the rear vehicle corner, but the bollard has bent.|No injuries, and the goods are fine. Passing the account on for follow-up please.")
add(51,
    "Sable Electronics speakers delivered to the consignee in Lille, France, on the export job.|They signed the CMR but added '6 cartons crushed'.|The rest of the CMR is complete and signed. Please pick up the crushed cartons recorded by the consignee rather than just filing the signed document away.",
    "The consignee in Lille has recorded six crushed cartons of Sable Electronics speakers on the CMR.|It's the export delivery to France; CMR otherwise complete and signed.|Can somebody follow up the goods mentioned in that reservation please, the signature came with that damage note.")
add(52,
    "NV20 RXC has rear-ended a car in slow traffic on the A34 near Oxford.|The car driver is complaining of neck pain; both vehicles are stopped in lane 1. Police on the way.|Northvale driver unhurt and the ambient grocery load is intact. Passing this through now.",
    "Both vehicles are in lane one on the A34 near Oxford following NV20 RXC running into the back of a car in slow traffic.|The car driver says their neck hurts. Police are coming.|Our Northvale driver isn't hurt, and the ambient groceries on the artic are intact.")
add(53,
    "NV69 GFE, 18-tonne rigid, couldn't unload bagged cement at Greystone Builders Merchants in Stoke-on-Trent.|Tail-lift won't lower, motor dead. Pallets and goods undamaged.|Customer is happy to rebook tomorrow morning; driver returning to the depot with the load. Can somebody arrange to check the lift please.",
    "The driver is bringing the bagged cement back on NV69 GFE after the tail-lift failed at Greystone Builders Merchants, Stoke-on-Trent.|Motor is dead and it won't lower, so the pallets can't come off the 18-tonne rigid.|No damage to the goods. Customer has agreed tomorrow morning instead.")
add(54,
    "Our order hasn't arrived and nobody can tell us where it is.|Please can someone pick this up and get back to us.|We keep asking where the order is, but haven't been given its whereabouts. We'd appreciate somebody looking into this and replying.",
    "Can somebody please come back to us about the order that hasn't arrived.|Nobody can tell us where it is, and that's what we're asking you to look into.|Please pick this up so we can speak to someone about the missing order.")
add(55,
    "10:20 at Northvale Daventry depot loading bank, a forklift reversed into a warehouse operative.|He's got a suspected broken leg. Ambulance has been called and the first-aider is with him.|Forklift isolated. Passing the loading bank's account through for somebody to pick up now.",
    "An operative at the Northvale Daventry loading bank is with the first-aider, suspected broken leg after a forklift reversed into him.|This happened at 10.20; an ambulance has been called.|The forklift has been isolated. Please pick up this account from the depot.")
add(56,
    "NV72 AXB has Kestrel Pharma vaccines in validated passive shippers for a hospital pharmacy in Taunton.|Booked nine this morning, now ETA after 11:00 because the M5 is closed J19 to J20 after a collision involving other vehicles.|We're stationary in the queue; our vehicle and load are fine.",
    "Taunton hospital pharmacy's 09:00 vaccine delivery won't arrive until after eleven.|Rigid NV72 AXB is stationary on the M5, shut between J19 and J20 after somebody else's collision, not ours.|Kestrel Pharma vaccines are in validated passive shippers; no problem with our vehicle or the load, just stuck in the queue.")
add(57,
    "NV21 BRG's double-deck trailer has hit a low railway bridge on an A-road in Oxford.|Roof is wedged under the bridge and the vehicle is stuck blocking the carriageway. Driver uninjured.|Railway operator hasn't been told yet. Cages of Tollbridge Retail clothing on board the artic.",
    "Bridge strike in Oxford, on an A-road, artic NV21 BRG with the double-deck trailer.|The trailer roof is wedged under the low railway bridge, blocking the road with the vehicle stuck there.|No injury to the driver. Railway operator not yet notified; load is cages of Tollbridge Retail clothes.")
add(58,
    "NV23 KPX is at Holyhead with Kestrel Pharma prescription medicines for a Dublin hospital, due 08:00 tomorrow.|Check-in refused it because the export declaration MRN is missing from the papers.|Last sailing that gets it there in time is 02:40 and the broker isn't answering. Driver and load fine.",
    "The hospital medicines for Dublin on artic NV23 KPX need to arrive by eight tomorrow morning.|Holyhead check-in won't accept it without the missing export declaration MRN; the 02:40 boat is the last one that makes that window.|Broker isn't answering. It's Kestrel Pharma prescription medicines, driver and load both fine.")
add(59,
    "NV22 YAC is at Calais for Dover with Pennine Paints export returns.|The report says all customs paperwork is fine, but also that the French broker has rejected the declaration for a wrong EORI number.|Driver is waiting in the lorry park. Please pick up that declaration rejection.",
    "Driver waiting in the Calais lorry park, artic NV22 YAC heading to Dover with Pennine Paints returns from export.|He says the customs papers are all fine. He also says the French broker rejected the declaration because its EORI number is incorrect.|That's the account being passed through.")
add(60,
    "The handheld crashed at Tollbridge Retail's Luton store and didn't capture the electronic POD.|Store manager signed a paper delivery note instead, but the driver has lost it.|Goods were delivered and accepted. We now haven't got either delivery record to hand, can somebody follow this up please.",
    "We need a POD for the Tollbridge Retail store delivery in Luton.|Goods accepted, but the driver's handheld crashed so there's no e-POD. Manager signed a paper delivery note, which the driver has since lost.|Please can someone help follow up the missing delivery record.")
add(61,
    "At the Pennine Paints customer in Bradford, opening the trailer revealed three dented drums and one cracked lid.|It's UN1263 paint, class 3 flammable, in 25-litre steel drums. They're upright, no leak seen and no smell.|Customer refused the damaged drums. Please pick this up.",
    "Customer in Bradford has refused damaged Pennine Paints drums: three dented, with a lid cracked on one.|The 25-litre steel drums contain UN1263 paint, ADR class 3 flammable. Damage found when opening the trailer.|All upright and nothing seen leaking or smelt. Sending the drum details through.")
add(62,
    "Had an accident at Doncaster, can somebody call the driver please.|That's the report we're passing on and the request is for a call back.|Please pick it up and speak to the driver so somebody can follow through on the account.",
    "Can someone ring back about an accident at Doncaster please.|The driver has asked for a call, and I'm putting that request through here.|Please get back to us about it so someone can speak to the driver and pick this up.")
add(63,
    "The pallet of office chairs for Sable Electronics' Reading office hasn't reached them.|The address label showed their old premises and the driver delivered there.|The new tenant at the old address has the pallet and is holding it. Can we get it to the current office please.",
    "Sable Electronics' office in Reading are missing their office-chair pallet because it went to the old premises.|Driver followed the address on the label, which was out of date.|New tenant there confirms they've got the pallet and are holding it for collection. Please arrange to put this right.")
add(64,
    "NV22 SUV arrived Tollbridge RDC Lutterworth with Sable Electronics tablets, carton count correct.|Door seal number differs from both CMR and manifest; several cartons have been opened and the tablets inside are smashed.|Nothing missing from the count. RDC have quarantined the load, please pick this up.",
    "Tollbridge RDC Lutterworth have quarantined the Sable Electronics tablet load on artic NV22 SUV.|The seal on the doors doesn't match the CMR or manifest. Cartons are all present, but several have been opened and their devices smashed.|Please follow up the seal and the damaged contents together.")
add(65,
    "Police stopped rigid NV67 SXA for a random check on the A1 near Newark.|They checked licence, tacho and load; everything in order. Vehicle held around two hours.|Ambient Tollbridge Retail delivery will be late as a result. Please pass on the time lost at the police check.",
    "Tollbridge Retail's ambient delivery on NV67 SXA has lost about two hours at a random police stop.|This was on the A1 near Newark; officers checked the driver's licence, tachograph and the load.|All were in order. It's the time held for the check that's making the delivery late.")
add(66,
    "NV66 TWA has sofas for a Tollbridge Retail home delivery.|Engine warning light on and in limp mode; driver says he's 'pulled over' on the A14 near Bury St Edmunds.|Customer told delivery will be about two hours late. Please pick up the engine problem on the rigid.",
    "The Tollbridge Retail sofa delivery will be roughly two hours late, customer has been told.|Rigid NV66 TWA has an engine warning and is in limp mode, driver reporting he's 'pulled over' on the A14 near Bury St Edmunds.|Can somebody follow up the fault please.")
add(67,
    "Recovery truck requested for 18-tonne rigid curtainsider NV68 PLW, gearbox failed.|It's stuck just after a bend on the single-carriageway A49 near Leominster and can't be moved; cars and lorries going round into the oncoming lane.|Building supplies for Greystone Builders Merchants, Hereford, no deadline. Please advise on recovery.",
    "Just asking for recovery for NV68 PLW, the 18-tonne rigid curtainsider on the A49 near Leominster.|Gearbox has failed just beyond a bend, vehicle immovable on the single carriageway. Traffic is passing it by using the opposite lane.|Load is building supplies for Greystone Builders Merchants in Hereford, no deadline to flag.")
add(68,
    "Reefer stopped on frozen trailer NV17 OWN, ice cream for Brackenridge Foods.|It's on the A1(M), thirty minutes from Brackenridge RDC Doncaster, box minus eighteen and doors sealed shut.|Driver continuing; RDC bay ready and they'll tip straight into their cold store on arrival. Please check the unit after tipping.",
    "NV17 OWN is continuing to Brackenridge RDC Doncaster with frozen ice cream, about half an hour away on the A1(M).|Unit has stopped, but box is -18 °C and doors remain sealed shut.|Goods-in have a bay ready and will tip into working refrigeration on arrival. Driver wants the reefer looked at once empty.")
add(69,
    "Wrenfield Dairies' yoghurt on chilled trailer NV19 CVB was rejected at the customer RDC on arrival.|Reefer download at goods-in showed eleven degrees in the box for three hours overnight.|Whole load being returned; the reefer is working again now. Please follow up the rejected yoghurt delivery.",
    "The customer RDC rejected all the yoghurt delivered on NV19 CVB for Wrenfield Dairies.|At goods-in they downloaded the reefer: box at 11 °C for three hours during the night.|It's coming back as a rejected load. Unit is running again now, but that's what the download showed.")
add(70,
    "02:00 on nights at Northvale Daventry depot, a forklift reversed into two cereal pallets waiting to be loaded.|It's Brackenridge Foods cereal; boxes are crushed and torn.|Nobody hurt. Please pick up the damaged pallets before this gets lost in the night shift handover.",
    "Two Brackenridge Foods cereal pallets have crushed and torn boxes at Northvale Daventry depot.|They were waiting for loading when a forklift reversed into them at two this morning on the night shift.|No one was injured. Passing the loading account through for follow-up.")
add(71,
    "Redgate Logistics driver on the Northvale parcels trunk reports at 01:30.|M25 closed J10 to J11 overnight for a police incident, nothing involving us.|The trunk into Northvale Daventry depot will be about three hours late. Ambient parcels, no deadline flagged; please pass the new timing on.",
    "The overnight parcels trunk to Northvale Daventry is running roughly three hours behind.|Subcontractor Redgate Logistics called it in at half one: the M25 is shut between J10 and J11 for a police incident unrelated to us.|It's ambient parcels with no flagged deadline on this run.")
add(72,
    "At Fenwick Garden Supplies' Ipswich warehouse the driver noticed a damaged racking upright in goods-in.|It is leaning slightly. The customer has been told, nobody hurt.|Please pick up the report about the racking at this delivery site and follow it through with them.",
    "Driver has reported a racking upright at the Fenwick Garden Supplies warehouse in Ipswich.|It's damaged and leaning a bit in the goods-in area. Customer already notified.|No injuries. Sending the observation through so someone can follow up the condition of the racking.")
add(73,
    "A colleague is reporting something from yesterday afternoon in the Northvale Warrington yard.|A shunter reversed a trailer without a banksman and nearly hit somebody walking across the yard.|Nobody was hurt. It is being reported the following day, please pick up the account of that reverse.",
    "Yesterday afternoon a pedestrian crossing Northvale Warrington depot yard was nearly hit by a reversing trailer.|The shunter was reversing without a banksman; no one got hurt.|A colleague has raised it today rather than yesterday. Please follow up what happened in the yard.")
add(74,
    "This home delivery for Tollbridge Retail is a DISASTER, the whole delivery wrecked!|It's cushions and throws, one carton has a scuffed corner, though the contents are unmarked.|I'm really angry about receiving it like this. Please get somebody to respond about the state of that carton.",
    "I'm furious about the Tollbridge Retail cushions and throws home delivery, what a disaster!|The carton has a scuffed corner; it's one carton and the contents don't have marks on them.|Still, the whole delivery feels wrecked to me, can somebody please respond to this.")
add(75,
    "At Brackenridge RDC Doncaster they've counted 36 of the 40 phone-accessory cartons on a mixed pallet.|Shrink-wrap looks like it's been re-wrapped, although the seal was intact and the number matched.|Driver didn't see the pallet being built. Please pick up the four-carton shortage.",
    "Four cartons of phone accessories missing from a mixed pallet at Brackenridge RDC Doncaster, expected forty.|The driver wasn't there when the pallet was built. Wrapping looks re-done, but the trailer seal is intact and matches.|Please follow up the difference in the carton count.")
add(76,
    "NV18 WEF has ambient flooring for Greystone Builders Merchants in Leeds.|Driver has reached his working-time duty limit at Lymm services and must take his daily rest.|Delivery moves from this evening to 07:00 tomorrow. Please pass on that revised arrival and pick up the rest requirement.",
    "The Greystone Builders Merchants Leeds flooring delivery on artic NV18 WEF will now be seven tomorrow morning rather than this evening.|Driver is at Lymm services, at his duty-time limit, and has to take his daily rest.|The load is ambient flooring. Please update the delivery timing.")
add(77,
    "NV65 MMC arrived Fenwick Garden Supplies, Bury St Edmunds, at 08:00 for the slot.|Gates locked and nobody answered the site phone. Driver waited forty minutes then went to the next drop.|Garden furniture still on board the rigid and intact. Please arrange another delivery with the site.",
    "Fenwick Garden Supplies in Bury St Edmunds couldn't be delivered to this morning, gates locked at the eight o'clock booking.|Driver on NV65 MMC tried the site phone, no answer, waited 40 minutes and moved on.|Their garden furniture is still on the rigid, undamaged. Please follow up access and redelivery.")
add(78,
    "Box damaged on the drop and the customer has refused one pallet.|Can somebody pick this up and get back to the driver please.|That's the report coming through, and we need someone to speak to the driver about the refused pallet.",
    "The driver says a box was damaged on the drop; customer refused a pallet.|Please can somebody come back to us about this.|I'm putting the report through here so it gets picked up and somebody can follow up the refusal.")
add(79,
    "NV69 OPA is stuck in a queue on the A303 near Stonehenge.|It's the rigid with the consignment for Kestrel Pharma, running about an hour late.|Please pass the delay on and get back to the driver about it; that's the update we're sending through.",
    "The Kestrel Pharma consignment on rigid NV69 OPA is going to be roughly an hour behind.|Driver is queuing on the A303 near Stonehenge.|Please pick up the timing change and come back to us, passing on the driver's update as received.")
add(80,
    "NV21 GDP inbound from Calais at Dover Eastern Docks with Marlow & Finch wine has been selected by Border Force.|They want an x-ray and physical examination; declarations and CMR checked, all in order.|Vehicle held with release expected in 3–4 hours. Ashford warehouse delivery will be late.",
    "Marlow & Finch's Ashford warehouse delivery of wine on NV21 GDP will be late.|The artic arrived Dover Eastern Docks from Calais and Border Force selected it for x-ray plus a physical examination.|CMR and declarations have been checked and are correct. It's held for the examination, expected release in three to four hours.")
add(81,
    "Could you advise what to do with NV22 COI please, steel coils for Corvid Automotive.|After hard braking on the A1(M), the coils shifted against the curtain and it's bulging. Driver pulled into a lay-by.|He's concerned a coil could come through onto the road if he moves. Just asking for guidance.",
    "A check-in on artic NV22 COI carrying Corvid Automotive steel coils, now in a lay-by off the A1(M).|Hard braking shifted the coils, which are pressing out against the bulging curtain. Driver thinks one could come through onto the road if he moves.|Please advise how to proceed from here.")
add(82,
    "All fine really, just a scratch at Greystone Builders Merchants' Wolverhampton yard.|Trailer clipped their banksman while reversing onto a bay. Graze and bruising to his forearm, first aid given.|Please pass that through, it's only a little graze as far as the account goes.",
    "Just reporting a scratch, all fine really, on the reverse onto a bay at Greystone Builders Merchants in Wolverhampton.|The trailer caught the customer's banksman and grazed and bruised his forearm.|He's had first aid. That's the account from the yard to pass on please.")
add(83,
    "NV70 BKT delivered four homeware pallets to Tollbridge Retail's Northampton store instead of Kettering.|Driver made an error reading the drop sheet. Northampton have the pallets safe and will hand them back.|Please arrange to get them to the Kettering store where they were meant to go.",
    "Tollbridge Retail Kettering's four pallets of homeware have gone to their Northampton store on rigid NV70 BKT.|It was a driver error with the drop sheet, wrong store.|Northampton confirm the pallets are safe with them and they're ready to give them back. Please sort getting them across.")
add(84,
    "NV71 ZPU is the frozen trailer with Carrier reefer on the A1 to Brackenridge RDC Doncaster.|Unit showed a fault code at 14:20. Driver stopped at services and restarted it, running normally since.|Box -19 °C, set point -20 °C. He wants an engineer to check it at the depot tonight.",
    "Driver requests a depot engineer check tonight for NV71 ZPU's Carrier unit, frozen trailer heading for Brackenridge RDC Doncaster via A1.|It put up a code at 2.20pm, then was restarted at services and has run normally ever since.|Set to minus twenty, actual box minus nineteen now.")
add(85,
    "NV22 BMO has an air leak, brakes locked on, stopped M25 anticlockwise near J27.|Driver first says he's on the hard shoulder, then says cars are swerving round the back of the trailer in lane 1.|He's out of the cab asking for recovery, ambient beverages for Oakhurst Brewery customers on board.",
    "Recovery requested for artic NV22 BMO on M25 ACW near J27, air escaping and brakes locked.|The account starts 'on the hard shoulder' but later says cars have to swerve round the trailer's back in lane one.|Driver out of cab. Load is ambient beverages for Oakhurst Brewery's customers.")
add(86,
    "Export speakers for a consignee in Rotterdam, Sable Electronics load at Northvale Thurrock depot.|Driver has noticed the CMR isn't signed by the consignor.|Vehicle hasn't left yet. Please sort the missing consignor signature on the international consignment note before this job heads out.",
    "The CMR for Sable Electronics' speaker export to Rotterdam has no consignor signature.|Driver spotted it at Northvale Thurrock depot, vehicle still there and not yet departed.|Could somebody get the signature sorted on that document please, passing on the pre-departure check.")
add(87,
    "23:40, NV17 HJT in the A12 lay-by near Colchester with Sable Electronics televisions.|Two men are trying the trailer doors and one banged on the cab door.|Driver's locked himself inside the cab and called 999. They're still there, please pick this up now.",
    "The men are still outside artic NV17 HJT, parked in a lay-by on the A12 near Colchester at twenty to midnight.|Two of them trying to open the trailer doors, one also banged on the cab.|Driver has locked himself in and phoned 999. Load is Sable Electronics TVs.")
add(88,
    "Driver arrived for the Norwich hospital pharmacy's 10:00 Halcyon Medical vaccine delivery, but the pallet isn't on the vehicle.|Northvale Daventry confirm it was left in the chilled store during loading. Seal fine, nothing else wrong.|There's no way to get the vaccines to Norwich by ten now.",
    "The vaccine pallet for the hospital pharmacy in Norwich was left behind at Northvale Daventry's chilled store when loading.|Driver discovered it wasn't on board on arrival for the 10:00 slot. It's Halcyon Medical vaccines, seal fine and nothing else wrong.|We cannot get it there by the booked time.")
add(89,
    "We've LOST a whole trailer! NVT 4012 isn't on its booked bay at Brackenridge RDC Doncaster.|RDC yard team think their shunter has moved it to the overflow yard and they're checking.|It's loaded with Northvale ambient snacks, no deadline, but please respond, this is a whole trailer we're looking for!",
    "Can't find loaded Northvale trailer NVT 4012 on the booked bay at Brackenridge RDC Doncaster, we've LOST it!|Yard team believe their shunter shifted it to the overflow yard; they're checking that now.|Ambient snacks, no deadline, but I'm panicking over where this whole trailer has gone.")
add(90,
    "Trailer brakes on NV19 FPL caught fire in the HGV park at Hilton Park services, M6.|Fire brigade called, driver has moved people away from the trailer.|It's the artic carrying ambient paper products for Marlow & Finch. Please pick up the fire report from the services.",
    "NV19 FPL's trailer is on fire at the brakes, parked in Hilton Park services HGV park on the M6.|Driver has moved people away and called the fire brigade.|Load is ambient paper products for Marlow & Finch. Passing through the account of the fire now.")
add(91,
    "NV70 CDX, 7.5-tonne box van on Halcyon Medical run, has a rear puncture in a lay-by on the A30 near Bodmin.|Spare missing from cradle. Driver safe; it's 10:05 and tyre service is ninety minutes away.|Dialysis fluids and consumables for a county hospital renal unit won't make the 11:00 slot.",
    "The county hospital renal unit's eleven o'clock delivery of dialysis fluids and consumables will be missed.|Halcyon Medical van NV70 CDX, 7.5-tonne box, has pulled into the A30 lay-by near Bodmin with a punctured rear tyre; no spare in the cradle.|Driver safe there. At five past ten, tyre service ETA is 90 minutes.")
add(92,
    "Pennine Paints' Huddersfield warehouse collection was booked for 09:00.|It's now 12:00 and the consignor is still loading; driver waiting.|Please pick up the late loading and get back to us about the collection, that's the timing update from the driver at the warehouse.",
    "Driver still waiting to collect at Pennine Paints in Huddersfield.|The booking was nine this morning, but the consignor is still loading at noon.|Can somebody follow this up with the warehouse please and come back to us about the wait on that collection.")
add(93,
    "Lorry's broken down, warning light on the dash and lost power.|Vehicle has stopped and the driver is waiting for recovery.|Please can somebody pick this up and get back to the driver about it, passing on the report as received.",
    "Driver reports a warning light and loss of power, lorry now stopped.|Waiting for recovery following the breakdown. Please get back to the driver about it.|I'm passing the account on here so somebody can pick it up and follow it through.")
add(94,
    "NV21 WQS parked overnight at the truck stop off the A5 near Hinckley.|At 05:00 driver found the nearside curtain slashed and six pallets of spirits gone.|He slept in the cab and heard nothing during the night. Police have been called; please pick up the missing goods.",
    "Six spirits pallets missing from artic NV21 WQS, found at five this morning after parking overnight near Hinckley off the A5.|Nearside curtain has been cut open at the truck stop.|Driver slept in the cab without hearing anything. Police called, sending the details through.")
add(95,
    "Night shift at Northvale Warrington depot reporting the shunting-area floodlights out for three nights.|Shunters say it's hard to see people walking there without the lighting.|No incident yet. Please pick up the lighting problem and come back to the night shift about it.",
    "The floodlights over Northvale Warrington's shunting area haven't worked for three nights.|The night shunters are saying pedestrians are hard to see as a result.|Nothing has happened yet, but please follow up the lights. Sending this from the night shift so it gets picked up.")
add(96,
    "Wrenfield Dairies butter export to Cork via Fishguard hasn't left Northvale Avonmouth depot yet.|Depot noticed before departure that the vet's stamp on the export health certificate is dated wrongly.|Reefer is working normally. Please sort the date on the certificate for this export load.",
    "The vet's stamp on the export health certificate for the Wrenfield Dairies butter has the wrong date.|Depot spotted it before departure at Northvale Avonmouth. Load is for a Cork customer via Fishguard and is still at the depot.|Reefer running normally; can someone pick up the certificate please.")
add(97,
    "04:45 at Northvale Daventry depot, driver rostered for 04:00 hasn't turned up and isn't answering.|Loaded ambient homeware trailer for Tollbridge Retail Milton Keynes store hasn't left.|Store expected it at 07:00. Night planner reporting the missing shift cover, please pick this up.",
    "Night planner here, Tollbridge Retail's Milton Keynes homeware trailer is still loaded at Northvale Daventry, not departed.|At quarter to five the driver booked for the four o'clock shift hasn't arrived or answered calls.|Ambient goods, store expecting seven this morning. We need someone to pick up the lack of a driver.")
add(98,
    "03:05, early-run driver at Northvale Avonmouth depot can't start tractor NV23 FPE, batteries flat.|Artic parked in the depot with ambient bottled water for a Tollbridge Retail store, delivery 07:00.|Can the night desk sort a jump pack or a spare tractor please, that's what the driver is asking for.",
    "Jump pack or another tractor requested for NV23 FPE at Northvale Avonmouth depot.|Driver arrived for the early run at five past three and found flat batteries, tractor won't start.|It's parked at the depot, loaded with Tollbridge Retail ambient bottled water for a seven o'clock store delivery.")
add(99,
    "Massive bang, driver thought he was going to die! NV20 YHT had a nearside tyre blow-out on M1 SB between J16 and J15.|He's pulled onto the hard shoulder, now safe behind the crash barrier, tyre service called.|Ambient paper products for Marlow & Finch, no deadline, but what a fright.",
    "That was a MASSIVE bang on NV20 YHT, driver says he thought he was going to die.|Nearside tyre blew between J16 and J15 on the M1 southbound; he got onto the hard shoulder and is safe behind the barrier. Tyre service called.|Artic has ambient Marlow & Finch paper products, no deadline. He's badly shaken.")
add(100,
    "Just checking in from Tebay services, M6, rigid NV70 HSE with Halcyon Medical blood-testing reagents.|They're for a hospital laboratory in Carlisle by 18:00. Tacho shows driver has reached nine hours driving and must stop.|No relief arranged yet; without one that six o'clock window will be missed. Please advise.",
    "A timing update on NV70 HSE, Halcyon Medical reagents for blood testing at a Carlisle hospital lab, due six this evening.|Driver is at Tebay services on the M6, nine-hour daily driving limit reached on the tachograph, so must stop.|There's no relief driver arranged; without cover the 18:00 window won't be made. Please pick this up.")


# A customer can relay a driver's account, but cannot know internal records first-hand.
# These Scenarios originate with customers, depot staff or named subcontractors.
CUSTOMER_ORIGIN = {25, 54, 74}
DEPOT_ORIGIN = {13, 15, 27, 29, 34, 55, 70, 73, 95, 97}
SUBCONTRACTOR = {4, 6, 8, 12, 40, 71}


def assemble():
    scenarios = [json.loads(line) for line in
                 Path("data/scenarios.jsonl").read_text(encoding="utf-8").splitlines()]
    assert list(PASSAGES) == [s["scenario_id"] for s in scenarios]
    reports = []
    patterns = ((0, 0, 0), (1, 1, 1), (0, 1, 0), (1, 0, 1))
    for scenario in scenarios:
        sid = scenario["scenario_id"]
        number = int(sid[2:])
        source_role = ("customer" if number in CUSTOMER_ORIGIN else
                       "depot" if number in DEPOT_ORIGIN else
                       "subcontractor" if number in SUBCONTRACTOR else "driver")
        # Where depot staff originated the account, the driver explicitly relays it.
        other_role = "driver" if source_role == "depot" else "depot"
        for variant, pattern in enumerate(patterns):
            passages = [PASSAGES[sid][choice][i] for i, choice in enumerate(pattern)]
            role = source_role if variant in (0, 2) else other_role
            if variant == 0:
                channel = "app"
                report_text = " ".join(passages)
            elif variant == 1:
                channel = "email"
                # Keep context first, but bring the requested action before detail.
                report_text = (f"Hello, passing on the {source_role}'s account below.\n\n"
                               + " ".join(passages[i] for i in (0, 2, 1))
                               + "\n\nPlease come back to us about this.")
            elif variant == 2:
                channel = "phone_transcript"
                report_text = ("Caller: " + passages[0] + "\nDesk: Right, go on.\nCaller: "
                               + passages[1] + "\nCaller: " + passages[2])
            else:
                channel = "app" if number % 2 else "email"
                report_text = (f"{source_role.capitalize()}'s report, as received: "
                               + " ".join(passages[i] for i in (1, 0, 2)))
            reports.append(dict(report_id="", scenario_id=sid, author_role=role,
                                channel=channel, text=report_text, generator=MODEL,
                                synthetic=True))
    random.Random(20261027).shuffle(reports)
    for index, report in enumerate(reports, 1):
        report["report_id"] = f"R-{index:04d}"
    with Path("data/reports.jsonl").open("w", encoding="utf-8", newline="\n") as output:
        for report in reports:
            output.write(json.dumps(report, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    assemble()
