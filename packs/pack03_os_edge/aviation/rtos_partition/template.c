/* rtos_partition/template.c
 * Skeleton for safety partition
 * Real RTOS integration needs formal verification and DO-178C style process.
 */

#include <stdio.h>
#include "FreeRTOS.h"
#include "task.h"

void SafetyTask(void *pvParameters) {
    for (;;) {
        // read commands from queue; do not accept unsigned commands
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

int main(void) {
    xTaskCreate(SafetyTask, "SafetyTask", 1024, NULL, 5, NULL);
    vTaskStartScheduler();
    while (1) {}
    return 0;
}
