# KEEPING THE FALLBACK

Below is a step‐by‐step explanation of what happens when you redirect a phone twice to the same ARFCN, first advertising a “real” operator MCC/MNC (so the UE attaches normally), then advertising MCC = 001, MNC = 01 (PLMN 001–01). In particular, we’ll see why the UE stays camped on 2G 001–01 (even though that PLMN is “not allowed” by its SIM) and never immediately falls back to 4G.

---

## 1. Scenario summary

1. **First redirection**:

   * You run your fake eNodeB on a given GSM ARFCN (e.g. BCCH = ARFCN 871).
   * In `send_connection_release()`, you set `is_csfb = true` and include in the RRC Release that same ARFCN under a “real” operator PLMN (call it MCC/MNC = AAA–BBB).
   * The UE receives “RRC Release + redirect to GSM ARFCN 871 under PLMN AAA–BBB,” tears down LTE and camps on that 2G cell in PLMN AAA–BBB. Because AAA–BBB is a valid Home (or equivalent) PLMN, the UE attaches successfully in 2G.

2. **Second redirection (same ARFCN, but now PLMN = 001–01)**:

   * You leave the same GSM BCCH ARFCN 871 on air, but you change the cell’s MCC/MNC to 001–01. In other words, everything about that 2G cell (ARFCN, BSIC, SIB7 neighbor lists, etc.) is identical—only the PLMN now reads “001–01” instead of “AAA–BBB.”
   * The UE, still camped on 2G AAA–BBB or coming from LTE, gets redirected again via LTE RRC Release → it tears down LTE and camps on 2G ARFCN 871 under MCC/MNC 001–01.
   * Now the UE performs a normal 2G Location Update, but the fake 2G BTS (IMSI‐catcher) replies “LAU Reject: PLMN not allowed.”

At this point, the UE is sitting on a 2G cell broadcasting PLMN 001–01—which is not in its allowed PLMN list—yet it does **not** immediately go back to LTE. Why?

---

## 2. How the UE decides which PLMN to camp on in 2G

### 2.1. 2G cell selection / reselection basics

When a UE is in Idle mode (RRC IDLE on LTE or Idle on 2G), it continually looks for the “best” cell according to these priorities (per 3GPP TS 23.122 and TS 36.304):

1. **Highest‐priority PLMN**:

   * The UE has a list of PLMNs in its USIM—starting with the Home PLMN (HPLMN), then any Equivalent PLMNs (EF-PLMN), then the list of “Allowed” PLMNs (if it’s roaming).
   * It will prefer to camp on a carrier whose broadcast PLMN matches one of those, in priority order.

2. **Cell‐ranking inside a given PLMN**:

   * If multiple cells broadcast the same PLMN, the UE uses “cell reselection” criteria (signal‐strength thresholds and ranking parameters) to choose which one it likes best.
   * If a cell’s PLMN is on the SIM’s **Forbidden PLMN** (FPLMN) list, the UE will normally treat that cell as “barred” and not camp on it—unless it was forced by RRC redirection.

### 2.2. Forced RRC redirection overrides normal camp rules

* When an LTE eNodeB sends **“RRC Connection Release with redirected\_carrier\_info → GERAN, PLMN = 001–01, ARFCN = 871”**, the UE immediately **aborts** whatever it was about to do in LTE (or 2G) and tunes to GERAN ARFCN 871 under PLMN 001–01.
* Even if PLMN 001–01 is not in the UE’s allowed list, the UE obeys the RRC redirection first. In other words:

  1. **RRC release** → UE is told “drop your LTE RRC and go camp on that 2G BCCH (ARFCN 871, MCC/MNC 001–01).”
  2. UE tunes to 2G ARFCN 871, decodes SIBs, sees PLMN 001–01, and camps—even though that PLMN is “forbidden” by its SIM. Because RRC redirection has **higher priority**, the UE must at least attempt to attach.

---

## 3. What happens when the UE sees “PLMN not allowed” in 2G

1. **Location Update procedure**

   * As soon as the UE camps on ARFCN 871 under PLMN 001–01, it initiates a **GSM Location Update** (LAU) to the IMSI-catcher (or “fake MSC”).
   * The fake MSC (or SGSN if packet‐switched) can respond with **LAU Reject, cause = “PLMN not allowed.”** This is the standard GSM cause code for “the UE is not allowed to register on this PLMN.”

2. **UE’s reaction to “LAU Reject: PLMN not allowed”**

   * Upon receiving that reject, the UE does the following (per TS 04.08 / TS 22.010):

     * It knows its SIM/USIM does **not** allow registration on 001–01, so it adds **001–01** to its **Forbidden PLMN (FPLMN) list**—meaning: “don’t try this PLMN again until after a timer (T3245) expires.”
     * However, it stays physically camped on that BCCH frequency (ARFCN 871) until it finds another acceptable cell, because to leave a 2G RACH/BCCH behind, it must find an alternate “better” cell first.

---

## 4. Why the UE does *not* immediately fall back to 4G

Once the UE has marked PLMN 001–01 as forbidden, you might think it would simply go look for LTE again—after all, its SIM says “I’m not allowed on 001–01, so I’ll reselect back to LTE.” But in practice, it usually does **not** instantaneously re‐camp to LTE, for two reasons:

### 4.1. No LTE neighbor info (or LTE cell absent)

* When you broadcast that fake 2G cell on ARFCN 871, you typically only advertise **GERAN frequencies** (and your fake PLMN 001–01). You do **not** broadcast any E-UTRAN neighbor information (no SIB7 for LTE, no SIB19, etc.) on that BCCH.

* A UE in idle on 2G waits for periodic “cell reselection” checks (every few hundred ms). It will consider these in order:

  1. “Is there a higher‐priority 2G or 3G cell whose PLMN is allowed?”
  2. “Is there a same‐priority 2G/3G cell I like better?”
  3. “Is there any 3G/4G (UTRAN/E-UTRAN) neighbor in the SIBs I can reselect to?”

* Because your fake 2G BCCH only lists itself (ARFCN 871, PLMN 001–01) and no LTE neighbor, the UE’s reselection algorithm never “sees” any E-UTRAN cell it could go to. Even if a real LTE cell from its operator is physically close by, the UE doesn’t know about it—because no neighbor‐list IE pointed to it.
* Therefore, from the UE’s point of view:

  > “I’m camped on ARFCN 871 (2G), PLMN 001–01 (which I just marked forbidden), but I have no other candidate cell broadcasts in my BCCH. I must stay here until I find an alternative cell.”
  > It will not hop back to LTE “by itself” unless it actually sees a higher‐priority (allowed) cell in the same BCCH’s neighbor‐list or it runs out of reacquisition timers entirely.

### 4.2. Forbidden PLMN → barred for some time, but not immediate reselect

* After “PLMN not allowed,” the UE writes 001–01 into its **Local FPLMN** list for a duration T3245 (usually several minutes).
* While that PLMN is in the FPLMN, the UE treats any 2G/3G cell broadcasting 001–01 as “barred” for reselection. In a normal scenario, it would immediately drop that barred cell and look for another allowed cell (e.g. another 2G PLMN or 3G or LTE).
* But because **no other cells** are visible in its immediate vicinity (recall—your fake BCCH does not advertise a valid LTE neighbor), it has nowhere else to go. In other words:

  * It does **not** say “I’ll drop 2G and go register on LTE,” because the 2G BCCH is still strongest—so it stays camped.
  * It does **not** see any “allowed” PLMN on that frequency, because the only PLMN is 001–01 (now forbidden).
  * It does **not** see any 4G neighbor IE, because your fake 2G cell never told it about LTE.

According to 3GPP TS 23.122 (for GSM/UTRAN cell selection) and TS 36.304 (for E-UTRAN), a barred PLMN cannot be reselected on that RAT, but the UE still must await the next “cell search” window. If it finds nothing else there, it remains stuck, nominally, on the barred BCCH until it detects a stronger/allowed candidate—then it finally hops to that. In practice:

1. **PLMN 001–01 is barred** → the UE marks ARFCN 871/001–01 as ineligible for camp.
2. **Immediately afterward**, no other BCCH is strong enough (or none was advertised), so the UE stays on ARFCN 871 (even though it’s barred) because the reselection algorithm needs an “actual replacement” before leaving.
3. **Without LTE neighbor info**, the UE never realizes “hey, there’s a valid LTE cell on frequency X” → so it never triggers a 4G reselection event.
4. Over time (T3245 expires), the UE might remove 001–01 from FPLMN and try 2G 001–01 again—only to get “PLMN not allowed” again. Only once it sees a real LTE neighbor or some other allowed 2G/3G PLMN will it move.

---

## 5. Putting it all together

* **First redirection (PLMN AAA–BBB)** → UE obeys RRC Release, camps on 2G ARFCN 871/AAA–BBB, attaches normally because AAA–BBB is in its allowed list.
* **Second redirection (PLMN 001–01)** → UE obeys RRC Release again, camps on 2G ARFCN 871/001–01, then sends LAU. Network replies “PLMN not allowed.” UE marks 001–01 as forbidden but remains physically on ARFCN 871 because:

  1. It was forced there by RRC, ignoring normal “don’t camp on forbidden” immediately.
  2. No other cell (including any real LTE) was advertised in that 2G BCCH’s neighbor lists.
  3. The UE’s cell‐reselection logic must find a strictly “better” allowed cell before vacating ARFCN 871—hence it stays there until such a cell appears.

Thus, you see the UE stay on 2G 001–01 for several seconds (or even minutes, until it finds a different allowed PLMN / RAT). It does **not** “refall back to 4G” immediately, because from the UE’s perspective there simply isn’t any other *advertised* cell to go to—only that one forbidden‐PLMN 2G cell, which it can’t deregister from until it finds an alternative.
