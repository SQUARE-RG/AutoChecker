#include <csignal>
#include <cstdlib>

namespace {
void handle_termination(int) {
    std::exit(EXIT_FAILURE); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
}
}

int main() {
    std::signal(SIGTERM, handle_termination);
    return EXIT_SUCCESS;
}
