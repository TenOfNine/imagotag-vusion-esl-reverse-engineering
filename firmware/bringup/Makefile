# Makefile - bare-metal bring-up images for the RFRTx026D (EFR32FG22).
#
#   ./fetch_sdk.sh      # once: device + CMSIS headers into ./sdk
#   make                # builds build/bringup_step1.{elf,hex,bin}
#
# Variables: STEP (only 1 exists so far), DEVICE (selects the device
# header; the image itself is the same for the 256 kB and 512 kB part).

STEP   ?= 1
DEVICE ?= EFR32FG22C121F256GM40
SDK    ?= sdk/gecko_sdk

NAME   := bringup_step$(STEP)
BUILD  := build

CROSS  ?= arm-none-eabi-
CC     := $(CROSS)gcc
OBJCOPY:= $(CROSS)objcopy
SIZE   := $(CROSS)size

SRCS   := src/startup.c src/rtt.c src/main.c
OBJS   := $(SRCS:src/%.c=$(BUILD)/%.o)

CFLAGS := -mcpu=cortex-m33 -mthumb -mfloat-abi=soft \
          -Os -g3 -std=gnu11 -Wall -Wextra -Werror \
          -ffunction-sections -fdata-sections -fno-common \
          -D$(DEVICE) -DBRINGUP_STEP=$(STEP) \
          -I$(SDK)/platform/Device/SiliconLabs/EFR32FG22/Include \
          -I$(SDK)/platform/CMSIS/Core/Include

LDFLAGS:= -mcpu=cortex-m33 -mthumb -mfloat-abi=soft \
          -T efr32fg22_bringup.ld -nostartfiles \
          --specs=nano.specs --specs=nosys.specs \
          -Wl,--gc-sections -Wl,-Map=$(BUILD)/$(NAME).map

.PHONY: all clean

all: $(BUILD)/$(NAME).hex $(BUILD)/$(NAME).bin
	$(SIZE) $(BUILD)/$(NAME).elf
	sha256sum $(BUILD)/$(NAME).hex $(BUILD)/$(NAME).bin

$(BUILD)/%.o: src/%.c src/rtt.h | $(BUILD)
	@test -d $(SDK) || (echo "missing $(SDK): run ./fetch_sdk.sh first" && false)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/$(NAME).elf: $(OBJS) efr32fg22_bringup.ld
	$(CC) $(LDFLAGS) $(OBJS) -o $@

$(BUILD)/$(NAME).hex: $(BUILD)/$(NAME).elf
	$(OBJCOPY) -O ihex $< $@

$(BUILD)/$(NAME).bin: $(BUILD)/$(NAME).elf
	$(OBJCOPY) -O binary $< $@

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
