# Krishi-Veda Vedic Kernels Build System
# ========================================
# Host (x86_64) build — used during development and on Replit
# Cross-compile (ARMv7-a) — for deployment on Raspberry Pi / old Indian processors

CXX      ?= g++
SRCS     = vedic_kernels.cpp
OUTDIR   = .

# ── Host Build (x86_64 with -Os for size) ──────────────────────────────────
# Same binary size as ARMv7 via -Os; runs on any Linux x86_64
HOST_FLAGS = -Os -fPIC -shared -std=c++14 -lm
HOST_OUT   = $(OUTDIR)/vedic_kernels.so

host:
	$(CXX) $(HOST_FLAGS) -o $(HOST_OUT) $(SRCS)
	@echo "Built host binary: $(HOST_OUT) ($$(du -sh $(HOST_OUT) | cut -f1))"

# ── ARM Cross-compile (for Raspberry Pi 2/3, old Cortex-A processors) ──────
# Install cross-toolchain first:
#   sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
# Then run:  make arm
ARM_CXX   = arm-linux-gnueabihf-g++
ARM_FLAGS = -Os -march=armv7-a -mfpu=neon -mfloat-abi=hard \
            -fPIC -shared -std=c++14 -lm
ARM_OUT   = $(OUTDIR)/vedic_kernels_armv7.so

arm:
	$(ARM_CXX) $(ARM_FLAGS) -o $(ARM_OUT) $(SRCS)
	@echo "Built ARM binary: $(ARM_OUT) ($$(du -sh $(ARM_OUT) | cut -f1))"

# ── Ultra-tiny ARMv6 (for very old hardware, Raspberry Pi Zero) ─────────────
ARM6_FLAGS = -Os -march=armv6 -mfpu=vfp -mfloat-abi=hard \
             -fPIC -shared -std=c++14 -lm
ARM6_OUT   = $(OUTDIR)/vedic_kernels_armv6.so

arm6:
	$(ARM_CXX) $(ARM6_FLAGS) -o $(ARM6_OUT) $(SRCS)
	@echo "Built ARMv6 binary: $(ARM6_OUT)"

clean:
	rm -f $(HOST_OUT) $(ARM_OUT) $(ARM6_OUT) /tmp/test_arm.so

.PHONY: host arm arm6 clean
.DEFAULT_GOAL := host
