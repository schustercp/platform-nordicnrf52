# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Default flags for bare-metal programming (without any framework layers)
#

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

print("Running _bare.py")
print(env.Dump())

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],

    CCFLAGS=[
        "-Os",  # optimize for size
        "-ffunction-sections",  # place each function in its own section
        "-fdata-sections",
        "-fno-strict-aliasing",
        "-Wall",
        "-Werror",
        "-nostdlib",
        "-fno-builtin",
        "-fshort-enums"
    ],

    CXXFLAGS=[
        "-fno-rtti",
        "-fno-exceptions",
        "-std=gnu++11",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        ("F_CPU", board.get("build.f_cpu"))
    ],

    LINKFLAGS=[
        "-Os",
        "-Wl,--gc-sections,--relax",
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ],

    LIBS=["c", "gcc", "m", "stdc++", "nosys"]
)

if "BOARD" in env:
    env.Append(
        CCFLAGS=[
            "-mcpu=%s" % board.get("build.cpu")
        ],
        LINKFLAGS=[
            "-mcpu=%s" % board.get("build.cpu")
        ]
    )
    if board.get("build.mcu") == "nrf52840":
        env.Append(
            CCFLAGS=[
                "-mthumb",
                "-mabi=aapcs",
                "-mfloat-abi=hard",
                "-mfpu=fpv4-sp-d16"
            ],
            LINKFLAGS=[
                "-mthumb",
                "-mabi=aapcs",
                "-mfloat-abi=hard",
                "-mfpu=fpv4-sp-d16"
            ],
            CPPDEFINES=[
                "FLOAT_ABI_HARD",
                "NRF52840_XXAA"
            ],
        )
    if board.get("build.softdevice"):
        env.Append(
            CPPDEFINES=[
                "SOFTDEVICE_PRESENT",
                "%s" % env.BoardConfig().get("build.softdevice")
            ],
        )


# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

# Process softdevice options
softdevice_ver = None
ldscript_path = None
cpp_defines = env.Flatten(env.get("CPPDEFINES", []))
print("_bare.py cpp_defines:" + str(cpp_defines))
if "NRF52_S132" in cpp_defines:
    softdevice_ver = "s132"
elif "NRF51_S130" in cpp_defines:
    softdevice_ver = "s130"
elif "NRF51_S110" in cpp_defines:
    softdevice_ver = "s110"
elif "S140" in cpp_defines:
    softdevice_ver = "s140"
elif "S132" in cpp_defines:
    softdevice_ver = "s132"

if softdevice_ver:
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "cores", board.get("build.core"),
                 "SDK", "components", "softdevice", softdevice_ver, "headers")
        ]
    )

    hex_path = join(FRAMEWORK_DIR, "cores", board.get("build.core"),
                    "SDK", "components", "softdevice", softdevice_ver, "hex")

    for f in listdir(hex_path):
        if f.endswith(".hex") and f.lower().startswith(softdevice_ver):
            env.Append(SOFTDEVICEHEX=join(hex_path, f))

    if "SOFTDEVICEHEX" not in env:
        print("Warning! Cannot find an appropriate softdevice binary!")

print("End _bare.py")
print(env.Dump())
