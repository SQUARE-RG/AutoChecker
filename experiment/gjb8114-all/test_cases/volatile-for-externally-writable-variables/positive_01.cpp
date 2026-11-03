#include <cstdint>

// Correctly declared volatile: the external interrupt controller writes it
// asynchronously, so the compiler must not cache or optimize away reads.
volatile bool g_interrupt_pending = false;

void external_interrupt_handler() {
    // Simulates the ISR running outside the normal program flow.
    g_interrupt_pending = true;
}

int main() {
    if (g_interrupt_pending) {
        return 1;
    }
    return 0;
}
