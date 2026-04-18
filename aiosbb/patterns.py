__all__ = "ipv4_pattern"

from re import compile


"""IPv4 pattern used by SBBClient._validate_ip()."""
ipv4_pattern = compile(
    r"^(([0-9])|([1-9][0-9])|(1([0-9]{2}))|(2[0-4][0-9])|(25[0-5]))((\.(([0-9])|([1-9][0-9])|(1(["
    r"0-9]{2}))|(2[0-4][0-9])|(25[0-5]))){3})$"
)
