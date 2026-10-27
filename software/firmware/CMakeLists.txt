cmake_minimum_required(VERSION 3.20)
# Host build (default): unit tests with mocks.   cmake -B build-host && cmake --build build-host && ctest --test-dir build-host
# Target build:  cmake -B build-arm -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake && cmake --build build-arm
project(pocketmate_mcu C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(PM_CORE_SRC src/crc16.c src/cobs.c src/frame.c src/privacy.c src/charge.c src/wdtsup.c src/buttons.c src/app.c)
set(PM_WARN -Wall -Wextra -Werror -Wshadow -Wconversion -Wno-sign-conversion)

if(CMAKE_SYSTEM_NAME STREQUAL "Generic")
  add_executable(pm_mcu.elf ${PM_CORE_SRC} target/hal_stm32u0.c target/startup_stm32u031.c target/main.c)
  target_include_directories(pm_mcu.elf PRIVATE include)
  target_compile_options(pm_mcu.elf PRIVATE ${PM_WARN} -mcpu=cortex-m0plus -mthumb -Os -ffunction-sections -fdata-sections)
  target_link_options(pm_mcu.elf PRIVATE -mcpu=cortex-m0plus -mthumb -nostartfiles --specs=nano.specs --specs=nosys.specs
      -T${CMAKE_SOURCE_DIR}/target/stm32u031k8_slotA.ld -Wl,--gc-sections -Wl,-Map=pm_mcu.map -Wl,--print-memory-usage)
  add_custom_command(TARGET pm_mcu.elf POST_BUILD
      COMMAND ${CMAKE_OBJCOPY} -O binary pm_mcu.elf pm_mcu.bin
      COMMAND ${CMAKE_SIZE} pm_mcu.elf)
else()
  enable_testing()
  add_executable(pm_fw_tests ${PM_CORE_SRC} test/hal_mock.c test/test_main.c)
  target_include_directories(pm_fw_tests PRIVATE include test)
  target_compile_options(pm_fw_tests PRIVATE ${PM_WARN} -g -fsanitize=address,undefined)
  target_link_options(pm_fw_tests PRIVATE -fsanitize=address,undefined)
  add_test(NAME pm_fw_tests COMMAND pm_fw_tests)
endif()
