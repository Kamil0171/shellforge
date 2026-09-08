from app.admin_duty.rocky import access, filesystem, network, packages, security, system

HANDLERS = {
    **access.HANDLERS,
    **system.HANDLERS,
    **network.HANDLERS,
    **packages.HANDLERS,
    **security.HANDLERS,
    "shell.pwd": filesystem.shell_pwd,
    "shell.cd": filesystem.shell_cd,
    **{
        f"filesystem.{key}": getattr(filesystem, "shell_" + handler)
        for key, handler in {
            "list": "ls",
            "read": "cat",
            "head": "head",
            "tail": "tail",
            "grep": "grep",
            "path-stat": "path_stat",
            "find": "find",
            "mkdir": "mkdir",
            "touch": "touch",
            "copy": "copy",
            "move": "move",
            "remove": "remove",
            "rmdir": "rmdir",
            "chmod": "chmod",
            "chown": "chown",
            "du": "du",
            "edit": "nano",
        }.items()
    },
}
