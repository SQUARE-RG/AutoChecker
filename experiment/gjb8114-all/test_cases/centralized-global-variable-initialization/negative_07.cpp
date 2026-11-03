#include <vector>

namespace app {

std::vector<int> g_config_values = []() { return std::vector<int>{10, 20, 30}; }(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]

} // namespace app

int main() {
    return app::g_config_values.size() == 3 ? 0 : 1;
}
