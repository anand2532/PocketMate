/* STM32U031K8: 64 KB flash, 12 KB SRAM (ARCHITECTURE.md §12).
 * Flash map: bootloader 8 KB @0x08000000 | slot A 26 KB @0x08002000 | slot B 26 KB @0x08008800 |
 *            config/cal 2 KB @0x0800F000 | log 2 KB @0x0800F800.  The app must fit 26 KB. */
MEMORY {
  FLASH (rx) : ORIGIN = 0x08002000, LENGTH = 26K
  RAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 12K
}
_estack = ORIGIN(RAM) + LENGTH(RAM);
_min_stack = 2K;
ENTRY(Reset_Handler)
SECTIONS {
  .isr_vector : { KEEP(*(.isr_vector)) } > FLASH
  .text : { *(.text*) *(.rodata*) . = ALIGN(4); _etext = .; } > FLASH
  .data : AT(_etext) { _sdata = .; *(.data*) . = ALIGN(4); _edata = .; } > RAM
  .bss (NOLOAD) : { _sbss = .; *(.bss*) *(COMMON) . = ALIGN(4); _ebss = .; } > RAM
  ASSERT(_ebss + _min_stack <= _estack, "SRAM budget exceeded (need 2 KB stack)")
  /DISCARD/ : { *(.ARM.exidx*) *(.comment) }
}
