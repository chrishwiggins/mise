#!/usr/bin/env python3
"""
slyp - A wrapper for running zeroshot in persistent Docker VMs.

Usage:
    slyp --new --vm <name>           Create a new persistent Docker VM
    slyp <file>.md --vm <name>       Run zeroshot on specified VM
    slyp <file>.md                   Run on single VM (or list if multiple)
    slyp --list                      List all slyp VMs
    slyp --stop --vm <name>          Stop a VM
    slyp --rm --vm <name>            Remove a VM
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
DEFAULT_IMAGE = "slyp-base:latest"
VM_LABEL = "slyp-vm"  # Label to identify slyp-managed containers


def run_cmd(cmd: List[str], capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    return subprocess.run(cmd, check=check)


def get_slyp_vms() -> List[Dict]:
    """Get list of all slyp-managed VMs (running or stopped)."""
    result = run_cmd(
        ["docker", "ps", "-a", "--filter", f"label={VM_LABEL}", "--format", "{{.Names}}\t{{.Status}}"],
        capture=True,
        check=False
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    vms = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split("\t")
            name = parts[0]
            status = parts[1] if len(parts) > 1 else "unknown"
            running = status.lower().startswith("up")
            vms.append({"name": name, "status": status, "running": running})
    return vms


def get_running_vms() -> List[Dict]:
    """Get list of running slyp VMs."""
    return [vm for vm in get_slyp_vms() if vm["running"]]


def vm_exists(name: str) -> bool:
    """Check if a VM with given name exists."""
    return any(vm["name"] == name for vm in get_slyp_vms())


def vm_is_running(name: str) -> bool:
    """Check if a VM is currently running."""
    return any(vm["name"] == name for vm in get_running_vms())


def create_vm(name: str) -> int:
    """Create and start a new persistent Docker VM."""
    if vm_exists(name):
        print(f"Error: VM '{name}' already exists.", file=sys.stderr)
        print(f"  Use 'slyp --rm --vm {name}' to remove it first.", file=sys.stderr)
        return 1

    # Build the docker run command
    home = Path.home()
    cwd = Path.cwd()

    # Mount points for workspace
    # Note: We run as 'node' user (uid 1000) to avoid root restrictions in claude
    mounts = [
        "-v", f"{cwd}:/workspace",
    ]

    # Optional mounts (only if they exist)
    optional_mounts = [
        (home / ".gitconfig", "/home/node/.gitconfig:ro"),
        (home / ".ssh", "/home/node/.ssh:ro"),
        (home / ".config" / "gh", "/home/node/.config/gh:ro"),
    ]

    for host_path, container_path in optional_mounts:
        if host_path.exists():
            mounts.extend(["-v", f"{host_path}:{container_path}"])

    cmd = [
        "docker", "run", "-d",
        "--name", name,
        "--label", VM_LABEL,
        "--user", "node",
        "-e", "HOME=/home/node",
        "-w", "/workspace",
    ] + mounts + [
        DEFAULT_IMAGE,
        "tail", "-f", "/dev/null"  # Keep container running
    ]

    print(f"Creating VM '{name}' with image {DEFAULT_IMAGE}...")
    result = run_cmd(cmd, check=False)

    if result.returncode == 0:
        print(f"VM '{name}' created successfully.")
        print(f"  Note: You may need to install zeroshot inside the VM:")
        print(f"    docker exec -it {name} npm install -g @covibes/zeroshot")
        return 0
    else:
        print(f"Error creating VM '{name}'.", file=sys.stderr)
        return result.returncode


def list_vms() -> int:
    """List all slyp VMs."""
    vms = get_slyp_vms()
    if not vms:
        print("No slyp VMs found.")
        print("  Create one with: slyp --new --vm <name>")
        return 0

    print("Slyp VMs:")
    for vm in vms:
        status_marker = "[running]" if vm["running"] else "[stopped]"
        print(f"  {vm['name']} {status_marker}")
    return 0


def stop_vm(name: str) -> int:
    """Stop a running VM."""
    if not vm_exists(name):
        print(f"Error: VM '{name}' does not exist.", file=sys.stderr)
        return 1

    if not vm_is_running(name):
        print(f"VM '{name}' is not running.")
        return 0

    print(f"Stopping VM '{name}'...")
    result = run_cmd(["docker", "stop", name], check=False)
    if result.returncode == 0:
        print(f"VM '{name}' stopped.")
    return result.returncode


def remove_vm(name: str) -> int:
    """Remove a VM (stops it first if running)."""
    if not vm_exists(name):
        print(f"Error: VM '{name}' does not exist.", file=sys.stderr)
        return 1

    if vm_is_running(name):
        print(f"Stopping VM '{name}'...")
        run_cmd(["docker", "stop", name], check=False)

    print(f"Removing VM '{name}'...")
    result = run_cmd(["docker", "rm", name], check=False)
    if result.returncode == 0:
        print(f"VM '{name}' removed.")
    return result.returncode


def start_vm(name: str) -> int:
    """Start a stopped VM."""
    if not vm_exists(name):
        print(f"Error: VM '{name}' does not exist.", file=sys.stderr)
        return 1

    if vm_is_running(name):
        return 0  # Already running

    print(f"Starting VM '{name}'...")
    result = run_cmd(["docker", "start", name], check=False)
    return result.returncode


def run_zeroshot(filename: str, vm_name: Optional[str]) -> int:
    """Run zeroshot on a file in the specified VM."""
    # Validate file exists
    filepath = Path(filename)
    if not filepath.exists():
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        return 1

    # Determine which VM to use
    if vm_name:
        if not vm_exists(vm_name):
            print(f"Error: VM '{vm_name}' does not exist.", file=sys.stderr)
            print("  Available VMs:", file=sys.stderr)
            list_vms()
            return 1
    else:
        # Auto-detect VM
        running = get_running_vms()
        if len(running) == 0:
            print("Error: No running VMs found.", file=sys.stderr)
            print("  Create one with: slyp --new --vm <name>", file=sys.stderr)
            return 1
        elif len(running) > 1:
            print("Multiple VMs running. Please specify which one to use:", file=sys.stderr)
            for vm in running:
                print(f"  slyp {filename} --vm {vm['name']}", file=sys.stderr)
            return 1
        else:
            vm_name = running[0]["name"]
            print(f"Using VM: {vm_name}")

    # Ensure VM is running
    if not vm_is_running(vm_name):
        start_result = start_vm(vm_name)
        if start_result != 0:
            return start_result

    # Convert filepath to be relative to workspace
    cwd = Path.cwd()
    try:
        relative_path = filepath.resolve().relative_to(cwd)
    except ValueError:
        # File is outside cwd, copy it in? For now, error out
        print(f"Error: File must be within current directory ({cwd}).", file=sys.stderr)
        return 1

    # Run zeroshot in the container
    # Use -it only if we have a TTY
    docker_flags = ["-it"] if sys.stdin.isatty() else []
    cmd = [
        "docker", "exec", *docker_flags, vm_name,
        "zeroshot", "run", str(relative_path)
    ]

    print(f"Running: zeroshot run {relative_path}")
    result = run_cmd(cmd, check=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="slyp - Run zeroshot in persistent Docker VMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  slyp --new --vm dev           Create a new VM named 'dev'
  slyp task.md --vm dev         Run zeroshot on task.md in 'dev' VM
  slyp task.md                  Run on single running VM (auto-detect)
  slyp --list                   List all slyp VMs
  slyp --stop --vm dev          Stop the 'dev' VM
  slyp --rm --vm dev            Remove the 'dev' VM
"""
    )

    parser.add_argument("filename", nargs="?", help="Task file to run (e.g., feature.md)")
    parser.add_argument("--vm", metavar="NAME", help="VM name to use or create")
    parser.add_argument("--new", action="store_true", help="Create a new VM")
    parser.add_argument("--list", action="store_true", help="List all slyp VMs")
    parser.add_argument("--stop", action="store_true", help="Stop a VM")
    parser.add_argument("--rm", action="store_true", help="Remove a VM")

    args = parser.parse_args()

    # Handle --list
    if args.list:
        return list_vms()

    # Handle --new --vm <name>
    if args.new:
        if not args.vm:
            print("Error: --new requires --vm <name>", file=sys.stderr)
            return 1
        return create_vm(args.vm)

    # Handle --stop --vm <name>
    if args.stop:
        if not args.vm:
            print("Error: --stop requires --vm <name>", file=sys.stderr)
            return 1
        return stop_vm(args.vm)

    # Handle --rm --vm <name>
    if args.rm:
        if not args.vm:
            print("Error: --rm requires --vm <name>", file=sys.stderr)
            return 1
        return remove_vm(args.vm)

    # Handle running zeroshot on a file
    if args.filename:
        return run_zeroshot(args.filename, args.vm)

    # No arguments - show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
