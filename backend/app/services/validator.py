from app.models.schemas import DeploymentSpec, ValidationReport, ValidationResult, Severity


def validate_spec(spec: DeploymentSpec) -> ValidationReport:
    r: list[ValidationResult] = []
    def add(cid, title, ok, detail, remediation=None, severity=Severity.error):
        r.append(ValidationResult(check_id=cid,title=title,passed=ok,severity=Severity.info if ok else severity,detail=detail,remediation=remediation))

    add("HOST_COUNT", "Management host count", len(spec.hosts) >= 4,
        f"{len(spec.hosts)} host(s) supplied.", "Provide at least four hosts for the initial management-domain lab topology.")
    names = [h.fqdn.lower() for h in spec.hosts]
    add("HOST_UNIQUE", "Unique ESXi identities", len(names) == len(set(names)),
        "Host FQDNs are unique." if len(names)==len(set(names)) else "Duplicate host FQDN detected.", "Assign a unique FQDN to every ESXi host.")
    addresses = [str(host.management_ip) for host in spec.hosts]
    add("HOST_IP_UNIQUE", "Unique management IP addresses", len(addresses) == len(set(addresses)),
        "Management IP addresses are unique." if len(addresses) == len(set(addresses)) else "Duplicate management IP address detected.",
        "Assign a unique management IP address to every ESXi host.")
    components = [spec.vcenter_fqdn, spec.sddc_manager_fqdn, spec.nsx_manager_fqdn]
    if spec.operations_fqdn is not None:
        components.append(spec.operations_fqdn)
    identities = names + components
    add("IDENTITY_UNIQUE", "Unique host and appliance identities", len(identities) == len(set(identities)),
        "Host and appliance names are unique." if len(identities) == len(set(identities)) else "Host or appliance DNS identity collision detected.",
        "Assign distinct FQDNs to all hosts and appliances, including Operations.")
    vlans = [spec.network.management_vlan, spec.network.vmotion_vlan, spec.network.vsan_vlan, spec.network.nsx_host_overlay_vlan]
    add("VLAN_SEPARATION", "Traffic VLAN separation", len(vlans) == len(set(vlans)),
        "Management, vMotion, vSAN and NSX overlay VLAN IDs are distinct." if len(vlans)==len(set(vlans)) else "One or more traffic classes share a VLAN ID.",
        "Use distinct VLANs for the lab unless your validated design intentionally combines traffic.", Severity.warning)
    add("JUMBO_MTU", "Overlay/vSAN MTU", spec.network.mtu >= 1600,
        f"Configured MTU: {spec.network.mtu}.", "Increase end-to-end MTU and verify the physical/nested path supports it.")
    add("DNS", "DNS configured", len(spec.network.dns_servers) > 0, f"{len(spec.network.dns_servers)} DNS server(s) supplied.", "Supply reachable DNS servers and create forward/reverse records.")
    add("NTP", "NTP configured", len(spec.network.ntp_servers) > 0, f"{len(spec.network.ntp_servers)} NTP source(s) supplied.", "Supply a common reachable NTP source for all VCF components.")
    fqdn_set = {spec.vcenter_fqdn.lower(), spec.sddc_manager_fqdn.lower(), spec.nsx_manager_fqdn.lower()}
    add("COMPONENT_NAMES", "Unique component FQDNs", len(fqdn_set) == 3, "Core appliance names are unique." if len(fqdn_set)==3 else "Core appliance FQDN collision detected.", "Use unique FQDNs for vCenter, SDDC Manager and NSX Manager.")
    add("INSTALLER_VERSION", "VCF 9 installer baseline", spec.vcf_version.startswith("9."), f"Requested VCF release: {spec.vcf_version}.", "Select a supported VCF 9.x release.")

    failures = sum(1 for x in r if not x.passed and x.severity == Severity.error)
    score = round(100 * sum(1 for x in r if x.passed) / len(r)) if r else 0
    return ValidationReport(ready=failures == 0, score=score, results=r)
