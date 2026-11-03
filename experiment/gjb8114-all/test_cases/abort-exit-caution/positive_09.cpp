#include <csignal>
#include <cstdlib>

namespace {
volatile std::sig_atomic_t g_termination_requested = 0;

void handle_termination(int) {
    g_termination_requested = 1;
}
}

int main() {
    std::signal(SIGTERM, handle_termination);
    if (g_termination_requested != 0) {
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
