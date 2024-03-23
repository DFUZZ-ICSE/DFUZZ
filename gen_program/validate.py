# reference: https://github.com/ise-uiuc/TitanFuzz/blob/main/validate.py

import subprocess
import time
from enum import IntEnum, auto

CURRENT_TIME = time.time()


class ExecutionStatus(IntEnum):
    SUCCESS = auto()
    EXCEPTION = auto()
    CRASH = auto()
    NOTCALL = auto()
    TIMEOUT = auto()

def run_cmd(
    cmd_args,
    timeout=10,
    verbose=False,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=False,
) -> (ExecutionStatus, str):
    try:
        output = subprocess.run(
            cmd_args, stdout=stdout, stderr=stderr, timeout=timeout, shell=shell
        )

    except subprocess.TimeoutExpired as te:
        if verbose:
            print("Timed out")
        return ExecutionStatus.TIMEOUT, ""
    else:
        if verbose:
            print("output.returncode: ", output.returncode)
        if output.returncode != 0:
            # 134 = Crash
            # 1 = exception
            error_msg = ""
            if output.stdout is not None:
                stdout_msg = output.stdout.decode("utf-8")
                stderr_msg = output.stderr.decode("utf-8")
                if verbose:
                    print("stdout> ", stdout_msg)
                if verbose:
                    print("stderr> ", stderr_msg)
                stdout_msg = stdout_msg[:30]
                error_msg = "---- returncode={} ----\nstdout> {}\nstderr> {}\n".format(
                    output.returncode, stdout_msg, stderr_msg
                )

            if output.returncode == 134:  # Failed assertion
                return ExecutionStatus.CRASH, "SIGABRT Triggered\n" + error_msg
            elif output.returncode == 132:
                return ExecutionStatus.CRASH, "SIGILL\n" + error_msg
            elif output.returncode == 133:
                return ExecutionStatus.CRASH, "SIGTRAP\n" + error_msg
            elif output.returncode == 136:
                return ExecutionStatus.CRASH, "SIGFPE\n" + error_msg
            elif output.returncode == 137:
                return ExecutionStatus.CRASH, "OOM\n" + error_msg
            elif output.returncode == 138:
                return ExecutionStatus.CRASH, "SIGBUS Triggered\n" + error_msg
            elif output.returncode == 139:
                return (
                    ExecutionStatus.CRASH,
                    "Segmentation Fault Triggered\n" + error_msg,
                )
            else:
                if output.returncode != 1:
                    # Check Failed: -6
                    print("output.returncode: ", output.returncode)
                    print(cmd_args)
                    print("stdout> ", stdout_msg)
                    print("stderr> ", stderr_msg)
                    return ExecutionStatus.CRASH, error_msg
                else:
                    return ExecutionStatus.EXCEPTION, error_msg
        else:
            if verbose:
                stdout_msg = output.stdout.decode("utf-8")
                print("stdout> ", stdout_msg)
            return ExecutionStatus.SUCCESS, ""

def validate_status_process(
    g_code, python="python", device="cpu", verbose=False
) -> (ExecutionStatus, str):
    with open("./tmp/tmp{}.py".format(CURRENT_TIME), "w") as f:
        f.write(g_code)
    # print("/tmp/tmp{}.py".format(CURRENT_TIME))
    run_args = [python, "./tmp/tmp{}.py".format(CURRENT_TIME)]
    status, msg = run_cmd(run_args, verbose=verbose)
    return status, msg

if __name__ == "__main__":
    g_code = """text = "sss"

# 打开文件（如果文件不存在，则创建）
with open("./tmp/custom_tags.txt", "w") as file:
    # 写入文本
    file.write(text)

print("文本写入成功！")
"""
    status, msg = validate_status_process(g_code)
    print(status, msg)