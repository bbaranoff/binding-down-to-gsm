# I am hurry 

> [!NOTE]
> Abstract : we will have to install open5gs-mmed (genuine), srsenb (patched), and osmocom in docker (comunity made)  to do the job

To install `open5gs-mmed`, follow these steps:

### Installing open5gs-mmed

1. **Prerequisites:**

   * Ensure your system meets the requirements for running `open5gs`.
   * Have `git` installed for cloning repositories and `cmake` for building.

2. **Clone open5gs repository:**

   ```bash
   git clone https://github.com/open5gs/open5gs
   cd open5gs
   ```

3. **Build and install open5gs-mmed:**

   ```bash
   meson build
   cd build
   ninja
   sudo ninja install
   ```

4. **Configure `open5gs-mmed` parameters:**

   * Edit the configuration file `mme.conf` located at `/usr/local/etc/freeDiameter/` to set necessary parameters such as network configuration, security settings, and interfaces.
   * Example configuration (partial excerpt):



```yaml
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
```

5. **Start open5gs-mmed:**

   * After configuration, start the `open5gs-mmed` service.
   * Ensure logging is configured as desired to `/var/local/log/open5gs/mme.log`.

### Install osmo-nipc

For `osmo-nipc`, follow these steps:

1. **Clone osmo-nipc repository:**

   ```bash
   git clone https://github.com/godfuzz3r/osmo-nidc
   cd osmo-nidc
   ```

2. **Start osmo-nipc using Docker Compose:**

   ```bash
   sudo docker-compose up
   ```

3. **Configure osmo-nipc:**

   * Edit `osmo-nipc` configuration as needed, typically found in `configs/configs.yaml`.
   * Example configuration (partial excerpt):

     ```yaml
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
     ```

4. **Start the osmo-nipc service:**

   * Ensure the configurations are correct and start the service accordingly.

### Patching srsran

To patch `srsran` for your specific needs, use the provided patch file (`csfb.patch`). Apply the patch as follows:

1. **Create the patch***

```patch

--- a/srsenb/hdr/stack/rrc/rrc_ue.h	2025-06-03 00:45:21.832243675 +0200
+++ b/srsenb/hdr/stack/rrc/rrc_ue.h	2025-06-03 00:45:51.091399988 +0200
@@ -173,7 +173,7 @@
   unique_rnti_ptr<rrc_mobility> mobility_handler;
   unique_rnti_ptr<rrc_endc>     endc_handler;
 
-  bool is_csfb = false;
+  bool is_csfb = true;
 
 private:
   srsran::unique_timer activity_timer; // for basic DL/UL activity timeout

```

2. **Apply the patch**

   ```bash
   patch -p1 < path/to/csfb.patch
   ```

3. **Verify changes in `rrc_ue.h`:**

   * Ensure `is_csfb` is correctly set to `true` as per the patch:

     ```cpp
     bool is_csfb = true;
     ```

### Using sib7.conf

Ensure your `sib7.conf` is correctly configured with the necessary parameters for broadcasting SIB7 information on ARFCN 871 for DCS1800 band, as per your network setup.


```
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
    t_resel_geran = 7;
    carrier_freqs_info_list =
    (
        {
            cell_resel_prio = 7;
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
```


---

By following these steps, you can effectively set up and configure `open5gs-mmed`, `osmo-nipc`, and patch `srsran` to align with your specific network requirements and testing scenarios. Adjust configurations as needed for your particular deployment environment and operational goals.
