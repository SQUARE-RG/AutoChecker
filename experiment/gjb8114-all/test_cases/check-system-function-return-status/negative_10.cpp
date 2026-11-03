#include <cstdlib>

int run_command(const char* cmd) {
    return (std::system(cmd), 0); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
}

int main() {
    return run_command("echo hello");
}
