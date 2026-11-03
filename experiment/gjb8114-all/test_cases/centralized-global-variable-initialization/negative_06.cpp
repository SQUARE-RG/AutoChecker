#include <string>
#include <utility>

namespace app {
namespace globals {
std::pair<int, std::string> g_config{7, "ready"}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]
}
}

int main() {
    return app::globals::g_config.first;
}
