#include <csignal>

int signal_flag = 0;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

void handle_signal(int) {
    signal_flag = 1;
}

int main() {
    std::signal(SIGINT, handle_signal);
    return signal_flag;
}
