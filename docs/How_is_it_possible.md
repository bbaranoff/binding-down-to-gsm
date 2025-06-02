# How is it possible

Binding down to unsafe network

---------------
	
This GitHub template includes fictional Python library
with some basic Sphinx docs.

The created documentation can be found at

https://brainelectronics-tutorial-template.readthedocs.io/en/latest/

<!-- MarkdownTOC -->

- [Getting started](#getting-started)
	- [Install required tools](#install-required-tools)
	- [Create documentation](#create-documentation)

<!-- /MarkdownTOC -->

## Getting started

### Install required tools

Below is an English‐language explanation of how the UE is forced to fall back to a GERAN (2G/EDGE) cell—specifically because we broadcast a fake Tracking Area Code (TAC) that is one higher or one lower than the “real” TAC, and because the `is_csfb` flag is set to true inside the `send_connection_release()` function. The snippet in question lives in **`rrc_ue.cc`** under **`void rrc::ue::send_connection_release()`**; it looks like this:

```cpp
void rrc::ue::send_connection_release()
{
  dl_dcch_msg_s dl_dcch_msg;
  auto&         rrc_release          = dl_dcch_msg.msg.set_c1().set_rrc_conn_release();
  rrc_release.rrc_transaction_id     = (uint8_t)((transaction_id++) % 4);
  rrc_conn_release_r8_ies_s& rel_ies = rrc_release.crit_exts.set_c1().set_rrc_conn_release_r8();
  rel_ies.release_cause              = release_cause_e::other;

  if (is_csfb) {
    if (parent->sib7.carrier_freqs_info_list.size() > 0) {
      rel_ies.redirected_carrier_info_present = true;
      rel_ies.redirected_carrier_info.set_geran();
      rel_ies.redirected_carrier_info.geran() = parent->sib7.carrier_freqs_info_list[0].carrier_freqs;
    } else {
      rel_ies.redirected_carrier_info_present = false;
    }
  }

  std::string octet_str;
  send_dl_dcch(&dl_dcch_msg, nullptr, &octet_str);
}
```

---

## What this code does (in plain English)

1. **Context: why `send_connection_release()` is called**

   * In a standard LTE eNodeB‐UE RRC procedure, the network can decide to tear down (release) an RRC connection by sending an **RRC Connection Release** message.
   * In our “interception 2G” scenario, we first lure the UE onto a cell whose TAC is artificially set to something like “original TAC + 1” (or “original TAC – 1”). Because the UE sees a new TAC that doesn’t match its currently registered TAC, it performs a **Tracking Area Update** and establishes an RRC Connection on that fake cell.
   * As soon as the UE is RRC‐connected to that fake cell (with TAC ±1), the eNodeB calls `send_connection_release()`. In other words, the UE is now camped on our fake LTE cell, and we want to immediately force it off LTE and onto GERAN.

2. **Breaking down the function**

   * We build a new downlink DCCH (Dedicated Control Channel) message of type **RRC Connection Release**.
   * We assign a transaction ID (`rrc_transaction_id`) in the normal way (just cycling through 0…3).
   * We set `release_cause = other` because “other” is a generic cause for releasing the connection.

3. **The crucial `if (is_csfb)` block**

   * The member variable `is_csfb` was set to `true` earlier (in `rrc_ue.h`). Because of that, this `if` always succeeds. If it had been `false`, the code inside would be skipped, and the RRC Release would carry **no redirection info**—the UE would simply go back to idle on LTE.

   * Since `is_csfb == true`, we check whether `parent->sib7.carrier_freqs_info_list.size() > 0`. In practice, `sib7.carrier_freqs_info_list[0].carrier_freqs` is a list of GERAN frequencies that we broadcast in the system information (SIB7) of our fake LTE cell. We typically populate that list with one or more GSM/EDGE ARFCNs (e.g., BCCH channels).

   * If the list is non‐empty, we set:

     ```cpp
     rel_ies.redirected_carrier_info_present = true;
     rel_ies.redirected_carrier_info.set_geran();
     rel_ies.redirected_carrier_info.geran() = parent->sib7.carrier_freqs_info_list[0].carrier_freqs;
     ```

     In other words, we instruct the UE:

     > “Here is your RRC Connection Release, but notice that I’m including `redirected_carrier_info` of type GERAN. Go camp on these GSM/EDGE frequencies instead.”

   * If for some reason `sib7.carrier_freqs_info_list` were empty, we would send `redirected_carrier_info_present = false`, meaning “no redirection; just drop to LTE idle.” But in our interception setup, we always ensure that `SIB7` advertises the neighbor GERAN BCCH frequencies.

4. **Sending the message**

   * Finally, `send_dl_dcch(&dl_dcch_msg, nullptr, &octet_str)` actually transmits the RRC Connection Release (with the redirection IE) over the air to the UE. At that instant, the UE’s LTE stack sees “RRC Connection Release with redirect to GERAN” and immediately switches to the indicated 2G/EDGE frequency.

---

## Why this makes the UE fall back to 2G for about one minute

1. **Step 1: UE camps on fake LTE cell (TAC ± 1)**

   * The UE was originally registered on a “real” LTE cell (TAC = X). We broadcast a second cell with TAC = X + 1 (or X – 1). Because the Tracking Area Code no longer matches, the UE performs a new RRC connection attachment to that fake cell. It’s now in LTE RRC Connected state on our interception cell.

2. **Step 2: RRC Connection Release + CSFB redirect**

   * Immediately, the eNodeB runs `send_connection_release()`. Because `is_csfb == true`, the UE receives:

     ```
     RRC Connection Release
       • release_cause = other
       • redirected_carrier_info_present = true
         – type = GERAN
         – list of GERAN frequencies (from SIB7)
     ```
   * LTE RRC dictates that as soon as an RRC Connection Release with redirection is received, the UE must tear down its LTE RRC session **and** immediately perform a cell reselection to the given 2G ARFCN(s).

3. **Step 3: UE camps on GERAN (Interception 2G)**

   * The UE tunes to the indicated BCCH frequency (e.g., an ARFCN in the GSM 900/1800 band). It performs a normal “GSM Attach” or “Location Update” on that cell. Because our IMSI‐catcher is pretending to be a legal GSM BTS, the UE finishes its location update and thinks it is “registered” on 2G.

4. **Step 4: No real service in the fake 2G network**

   * Our fake 2G BTS (the IMSI‐catcher) does not have a legitimate SGSN or MSC behind it. Therefore:

     1. The UE expects paging messages or a genuine Location Update Accept, but the interceptor either sends a fake “LAU Accept” then never responds to any further network requests, or simply never presents a valid GPRS path.
     2. The UE’s internal 2G protocol timers now start running (e.g., T3212 for SMS, T3192 for Paging Response, T3210 for periodic location update). Because the intercepting cell does not offer a true GPRS/EDGE attach or voice channel, the UE will never be handed off to a real MSC or SGSN.

5. **Step 5: UE gives up after ≈ 60 seconds**

   * After roughly one minute of “stuck in 2G without any real service,” the UE automatically decides that this 2G cell is useless. Its firmware triggers a “cell reselection” back to the strongest LTE cell available (which, in our testbed, is still the legitimate operator’s LTE cell).
   * At that point, the UE re‐attaches to LTE (or resumes its previous EPS context) and resumes normal data/VoLTE usage.

---

## Summary in English

* We broadcast a second LTE cell whose Tracking Area Code (TAC) is set to “original\_TAC ± 1.” Because the UE sees a mismatched TAC, it camps on our fake LTE cell in **RRC Connected** state.

* In the `send_connection_release()` function of `rrc_ue.cc`, we have forced `is_csfb = true` (in `rrc_ue.h`). As soon as the UE attaches to our fake cell, the code builds an **RRC Connection Release** message containing:

  1. `release_cause = other`
  2. `redirected_carrier_info_present = true`
  3. A **GERAN** redirection IE listing one or more 2G/EDGE frequencies (pulled from `parent->sib7.carrier_freqs_info_list[0]`).

* When the UE receives that RRC release with redirection, it immediately tears down LTE and camps onto the specified GSM/EDGE frequency.

* Because our fake 2G cell does not provide a genuine SGSN/MSC, the UE’s 2G‐layer timers expire after about one minute, and the phone gives up on the fake 2G cell and re‐selects back to the real LTE network.

* In short, the combination of:

  1. broadcasting TAC ± 1 to trick the UE into RRC‐connecting to our cell,
  2. setting `is_csfb = true` so that **every** RRC Connection Release includes a GERAN redirect,
     allows us to force the UE into 2G for roughly 60 seconds before it finally realizes “no real service here” and returns to LTE.

This is why, in an interception scenario, the UE ends up on the fake 2G network for about one minute: it’s following the standard CSFB procedure (driven by `is_csfb = true` in `send_connection_release()`), but the interceptor never completes a valid 2G attach/Authentication/MSC handover. After its internal 2G timers time out (≈ 60 s), the UE reverts to LTE.

