#include <string>

std::string g_app_name("inventory"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]

int main() {
    return g_app_name.empty() ? 1 : 0;
}
