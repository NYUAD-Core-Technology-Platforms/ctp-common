# Scheduling — CTPSS (Core Technology Platforms Scheduling System)

The CTPSS is the web-based reservation and scheduling system for all CTP equipment.

- URL: <https://corelabs.abudhabi.nyu.edu> (requires NYU network or VPN)
- Access request / training request: <mailto:CTP-group@nyu.edu>
- Linktree (all forms and quick links): <https://linktr.ee/CTPNYUAD>

## Access workflow

1. The user must first be trained on at least one piece of CTP equipment.
2. Once trained and approved by the technical CTP personnel, the user is registered in CTPSS and given a username and password (separate from the NYUAD password).
3. The user logs in, changes the password via the **My Account** tab, then books equipment under the **Schedule → Bookings** tab.

## Booking steps

1. Open <https://corelabs.abudhabi.nyu.edu>.
2. Log in with NYUAD NetID and the password issued by the CTPSS administrator.
3. **My Account → Change Password** to set a personal password.
4. **Schedule → Bookings**, then choose the CTP (each CTP has its own equipment list).
5. Click a white (reservable) block, pick the specific equipment and time, set the start and end time. Fill the **Title of reservation** with the sample type and the **Description** with the hardware setup needed. Click **Create**.
6. An automatic reference number appears — click **Close**.

## Screen lock

Most equipment PCs are protected by a screen lock. Unlock with the NYU NetID and password. Login is only allowed within the booked window; the system logs out automatically when the booking ends. The screen cannot be unlocked without an active booking. If a session finishes early, close programs and click **Lock Screen**.

## Saving and accessing data

CTP runs a dedicated server for user data. Save data via the `share.bat` shortcut on the equipment desktop, then enter NYU NetID for username and NYU password. Save into the directory matching the NetID. Disconnect with `disconnect.bat` after saving.

Data is stored **temporarily**; users must copy and back up their data to personal storage promptly — the server space is recycled when full.

### Mapping the share drive on a NYUAD-network computer

1. Open *My Computer*, choose **Map Network Drive**.
2. Use the path provided by IT, in the form `\\corelabs.abudhabi.nyu.edu\<netid>`.
3. Tick **Reconnect at sign-in** and click **Finish**.
4. If prompted, use `AD\<netid>` for the username with the NetID password.

## Training & support

Email <mailto:CTP-group@nyu.edu> to request training or access to any core equipment. Training is the prerequisite for any booking.
