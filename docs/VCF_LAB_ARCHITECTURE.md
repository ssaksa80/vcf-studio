# Nested lab architecture

The intended target is a physical vCenter hosting four editable nested ESXi VMs. The current schema describes host CPU, memory, aggregate datastore size and NIC count only. It cannot yet express placement, boot/data disk layout, CIDRs or network backing.

Current defaults are inherited scaffold values, not a verified VCF hardware compatibility profile. No live VMware integration or installation is performed. No storage layout, cache tier, hardware version or installer minor release is certified by this increment.

Before adding provisioning, verify release-specific requirements against official Broadcom documentation, including nested virtualization, supported guest configuration, datastore layout and host networking. Store version-specific constraints in the backend. Capacity must include appliance overhead, reservations and existing usage.
