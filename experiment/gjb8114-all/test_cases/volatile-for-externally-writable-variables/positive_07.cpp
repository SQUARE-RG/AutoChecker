#include <csignal>

volatile int signal_flag = 0;

void handle_signal(int) {
    signal_flag = 1;
}

int main() {
    std::signal(SIGINT, handle_signal);
    return signal_flag;
}
