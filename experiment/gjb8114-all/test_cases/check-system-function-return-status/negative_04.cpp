#include <cstdlib>

int execute_command() {
    return std::system("exit 0"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
}

int main() {
    int status = execute_command();
    (void)status;
    return 0;
}
